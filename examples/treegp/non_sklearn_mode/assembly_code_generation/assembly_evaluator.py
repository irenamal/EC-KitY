import csv
import os
import subprocess
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor

import numpy as np
from eckity.evaluators.simple_individual_evaluator import SimpleIndividualEvaluator
import shutil

# 0 - score, 1 - lifetime, 2 - written bytes
SCORE = 0
LIFETIME = 1
BYTES = 2
RATE = 3


class AssemblyEvaluator(SimpleIndividualEvaluator):
    # Allow some evaluators run in parallel. Need to modify the paths for the execution.
    # Need to duplicate the original directory for this to work properly
    def __init__(self, root_path, nasm_path):
        super().__init__()
        self.nasm_path = nasm_path
        self.root_path = root_path
        self.engine = "corewars8086-5.1.0-SNAPSHOT-jar-with-dependencies.jar"
        self.executor = ThreadPoolExecutor(max_workers=4)

    # for f in os.listdir(os.path.join(root_path, "survivors")):
    #    os.remove(os.path.join(root_path, "survivors", f))

    def _write_survivor_to_file(self, tree, file_path):
        with open(file_path, "w+") as file:
            print("@start:", file=file)
            tree.execute(file)  # ax="ax", bx="bx", cx="cx", dx="dx", es="es", ds="ds", cs="cs", ss="ss",
            # abx="[bx]", asi="[si]", adi="[di]", asp="[sp]", abp="[bp]")
            print("@end:", file=file)
            file.seek(0, os.SEEK_END)
            while file.tell() < 510:
                file.write("db 0x0F\n")
        file.close()

    def _compile_survivor(self, file_path, individual_name, survivors_path, nasm_path):
        proc = subprocess.Popen([nasm_path, "-f bin", file_path, "-o", os.path.join(survivors_path, individual_name)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if "error" in str(stderr):
            print(stderr)
            return -1  # fitness = -1
        return 0

    def _read_scores(self, path, individual_name1):
        group_data = []
        indiv_data = []

        with open(os.path.join(path, "scores.csv"), 'r') as scores:
            info = csv.reader(scores)
            flag_ind = False
            for index, line in enumerate(info):
                if line.__contains__("Groups:"):
                    continue
                if not flag_ind and not line.__contains__("Warriors:") and line != []:
                    if line[0] == individual_name1[:-1]:
                        group_data.append(line[1:])
                    continue
                if line.__contains__("Warriors:"):
                    flag_ind = True
                    continue
                if flag_ind:
                    if line[0][:-1] == individual_name1[:-1]:
                        indiv_data.append(line[1:])
        scores.close()

        return {"group_data": group_data, "indiv_data": indiv_data,
                "group_index": 0, "indiv1_index": 0, "indiv2_index": 1}

    def evaluate_individual(self, individual):
        """
              Compute the fitness value of a given individual.

              Fitness evaluation is done calculating the accuracy between the tree execution result and the optimal result
              (multiplexer truth table).

              Parameters
              ----------
              opponents : Name of the survivor to compete against
              individual: Tree
                  The individual to compute the fitness value for.

              Returns
              -------
              float
                  The evaluated fitness value of the given individual.
                  The value ranges from 0 (worst case) to 1 (best case).
              """
        #worker = str(threading.get_ident())  # multithreading
        worker = str(os.getpid())  # multiprocessing
        if not os.path.exists(os.path.join(self.root_path, "corewars8086_" + worker)):
            os.mkdir(os.path.join(self.root_path, "corewars8086_" + worker))
        survivors_path = os.path.join(self.root_path, "corewars8086_" + worker, "survivors")
        if not os.path.exists(survivors_path):
            os.mkdir(survivors_path)
        for f in os.listdir(survivors_path):
            try:
                os.remove(os.path.join(survivors_path, f))  # remove previous survivors
            except Exception:
                continue
        all_train_set = os.listdir(os.path.join(self.root_path, "corewars8086", "survivors"))
        opponents = list(set([survivor[:-1] for survivor in all_train_set]))
        [shutil.copy(os.path.join(self.root_path, "corewars8086", "survivors", opponent + i),
                     survivors_path) for opponent in opponents for i in ["1", "2"]]

        if not os.path.exists(os.path.join(self.root_path, "corewars8086_" + worker, self.engine)):
            shutil.copy(os.path.join(self.root_path, "corewars8086", self.engine),
                        os.path.join(self.root_path, "corewars8086_" + worker, self.engine))
        nasm_path = os.path.join(self.root_path, "corewars8086_" + worker, "nasm")
        if not os.path.exists(nasm_path):
            shutil.copy(self.nasm_path, os.path.join(self.root_path, "corewars8086_" + worker, "nasm"))

        individual_name1 = str(individual.id) + "try1"
        individual_name2 = str(individual.id) + "try2"
        file_path1 = os.path.join(self.root_path, "corewars8086_" + worker, 'survivors', individual_name1 + '.asm')
        file_path2 = os.path.join(self.root_path, "corewars8086_" + worker, 'survivors', individual_name2 + '.asm')
        self._write_survivor_to_file(individual.tree1, file_path1)
        self._write_survivor_to_file(individual.tree2, file_path2)

        score1 = self._compile_survivor(file_path1, individual_name1, survivors_path, nasm_path)
        score2 = self._compile_survivor(file_path2, individual_name2, survivors_path, nasm_path)

        if score1 == -1 or score2 == -1:  # one of the trees in invalid
            if os.path.exists(os.path.join(survivors_path, individual_name1)):
                os.remove(os.path.join(survivors_path, individual_name1))
            if os.path.exists(os.path.join(survivors_path, individual_name2)):
                os.remove(os.path.join(survivors_path, individual_name2))
            return [0, 0, 0, [0, 0, 0, 0]]

        if os.path.exists(os.path.join(self.root_path, "corewars8086_" + worker, "scores.csv")):
            os.remove(os.path.join(self.root_path, "corewars8086_" + worker, "scores.csv"))
        proc = subprocess.Popen(
            ["java", "-Xmx1500m", "-jar", os.path.join(self.root_path, "corewars8086_" + worker, self.engine),
             survivors_path, os.path.join(self.root_path, "corewars8086_" + worker, "scores.csv")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if "b''" != str(stderr):
            print(stderr)

        os.remove(os.path.join(survivors_path, individual_name1))
        os.remove(os.path.join(survivors_path, individual_name2))

        # open scores.csv and get the survivors score in comparison to others
        for i in range(3):
            if not os.path.exists(os.path.join(self.root_path, "corewars8086_" + worker, "scores.csv")):
                time.sleep(5)
            else:
                break
        if not os.path.exists(os.path.join(self.root_path, "corewars8086_" + worker, "scores.csv")):
            return [0, 0, 0, [0, 0, 0, 0]]
        results = self._read_scores(os.path.join(self.root_path, "corewars8086_" + worker), individual_name1)

        norm_indiv1 = normalize_data(results["indiv_data"], results["indiv1_index"])
        fitness1 = fitness_calculation(norm_indiv1[SCORE], norm_indiv1[LIFETIME], norm_indiv1[BYTES],
                                       norm_indiv1[RATE])
        norm_indiv2 = normalize_data(results["indiv_data"], results["indiv2_index"])
        fitness2 = fitness_calculation(norm_indiv2[SCORE], norm_indiv2[LIFETIME], norm_indiv2[BYTES],
                                       norm_indiv2[RATE])
        norm_group = normalize_data(results["group_data"], results["group_index"])
        fitness = fitness_calculation(norm_group[SCORE], norm_group[LIFETIME], norm_group[BYTES], norm_group[RATE])

        return [fitness1, fitness2, fitness, norm_group]  # how many did the survivor beat * its partial score?

    def calculate_avg_fitness(self, individual):
        # This function is relevant for more than one opponent
        all_train_set = os.listdir(os.path.join(self.root_path, "corewars8086", "survivors"))
        opponents = list(set([survivor[:-1] for survivor in all_train_set]))

        eval_results = self.executor.map(self.evaluate_individual, [individual] * len(opponents), opponents)
        fitness_array = []
        for opp, result in zip(opponents, eval_results):
            fitness_array.append(result)

        # calculate the average fitness between all the games against each opponent
        first_tree = sum(fit[0] for fit in fitness_array) / len(fitness_array)
        second_tree = sum(fit[1] for fit in fitness_array) / len(fitness_array)
        group = sum(fit[2] for fit in fitness_array) / len(fitness_array)
        score = sum(fit[3][SCORE] for fit in fitness_array) / len(fitness_array)
        life = sum(fit[3][LIFETIME] for fit in fitness_array) / len(fitness_array)
        bytes = sum(fit[3][BYTES] for fit in fitness_array) / len(fitness_array)
        rate = sum(fit[3][RATE] for fit in fitness_array) / len(fitness_array)

        return [first_tree, second_tree, group, [score, life, bytes, rate]]

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['executor']

        return state

    # Necessary for valid unpickling, since SimpleQueue object cannot be pickled
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.executor = ThreadPoolExecutor(max_workers=4)



def normalize_data(data, index):
    data = np.array(data).astype(float)
    # normalized score by score/played_game
    score = data[index][SCORE]
    # normalize lifetime by log?
    lifetime = data[index][LIFETIME]  # math.log(data[index][LIFETIME], 2) if data[index][LIFETIME] > 0 else 0
    # normilize bytes by log?
    bytes = data[index][BYTES]  # math.log(data[index][BYTES], 2) if data[index][BYTES] > 0 else 0
    rate = data[index][RATE]
    return [score, lifetime, bytes, rate]
    # return MinMaxScaler().fit_transform(data) # [0-1] range


def fitness_calculation(score, alive_time, bytes_written, writing_rate):
   # if bytes_written >= 5:
    #    bytes_written = 10 # 4 is the maximum in regular commands
    max_value = 10
    return round(2 * score + 0.02 * alive_time + 0.03 * min(max_value, bytes_written) + 0.01 * min(max_value, writing_rate), 5)
