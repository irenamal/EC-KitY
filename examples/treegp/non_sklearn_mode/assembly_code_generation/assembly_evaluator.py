import csv
import os
import random
import sys
import subprocess
import threading
import numpy as np
from eckity.evaluators.simple_individual_evaluator import SimpleIndividualEvaluator
import shutil
from sklearn.preprocessing import StandardScaler, PowerTransformer, MinMaxScaler

# 0 - score, 1 - lifetime, 2 - written bytes
SCORE = 0
LIFETIME = 1
BYTES = 2

class AssemblyEvaluator(SimpleIndividualEvaluator):
# Allow some evaluators run in parallel. Need to modify the paths for the execution.
# Need to duplicate the original directory for this to work properly
    def __init__(self, root_path, nasm_path):
        super().__init__()
        self.nasm_path = nasm_path
        self.root_path = root_path
        self.engine = "corewars8086-5.1.0-SNAPSHOT-jar-with-dependencies.jar"

       # for f in os.listdir(os.path.join(root_path, "survivors")):
        #    os.remove(os.path.join(root_path, "survivors", f))

    def _write_survivor_to_file(self, tree, file_path):
        original_stdout = sys.stdout
        with open(file_path, 'w+') as f:
            f.write("@start:\n")
            sys.stdout = f
            tree.execute()  # ax="ax", bx="bx", cx="cx", dx="dx", es="es", ds="ds", cs="cs", ss="ss",
            # abx="[bx]", asi="[si]", adi="[di]", asp="[sp]", abp="[bp]")
            sys.stdout = original_stdout
            f.write("@end:\n")
            f.seek(0, os.SEEK_END)
            while f.tell() < 512:
                f.write("\ndb 0xC0")
                f.seek(0, os.SEEK_END)
        f.close()

    def _compile_survivor(self, file_path, individual_name, survivors_path, nasm_path):
        proc = subprocess.Popen([nasm_path, "-f bin", file_path, "-o", os.path.join(survivors_path, individual_name)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if "error" in str(stderr):
            print(stderr)
            return -1  # fitness = -1
        return 0

    def _read_scores(self, path, individual_name1, individual_name2):
        group_data = []
        indiv_data = []
        group_index = 0

        with open(os.path.join(path, "scores.csv")) as scores:
            info = csv.reader(scores)
            flag_ind = False
            for index, line in enumerate(info):
                if line.__contains__("Groups:"):
                    continue
                if not flag_ind and not line.__contains__("Warriors:") and line != []:
                    group_data.append(line[1:])
                    if line[0] == individual_name1[:-1]:
                        group_index = index - 1
                    continue
                if line.__contains__("Warriors:"):
                    flag_ind = True
                    continue
                if flag_ind:
                    indiv_data.append(line[1:])

        return {"group_data": group_data, "indiv_data": indiv_data,
                "group_index": group_index, "indiv1_index": group_index, "indiv2_index": group_index + 1}

    def _evaluate_individual(self, individual):
        """
        Compute the fitness value of a given individual.

        Fitness evaluation is done calculating the accuracy between the tree execution result and the optimal result
        (multiplexer truth table).

        Parameters
        ----------
        individual: Tree
            The individual to compute the fitness value for.

        Returns
        -------
        float
            The evaluated fitness value of the given individual.
            The value ranges from 0 (worst case) to 1 (best case).
        """

        worker = str(threading.get_ident())
        if not os.path.exists(os.path.join(self.root_path, "corewars8086_" + worker)):
            os.mkdir(os.path.join(self.root_path, "corewars8086_" + worker))
        survivors_path = os.path.join(self.root_path, "corewars8086_" + worker, "survivors")
        all_train_set = os.listdir(os.path.join(self.root_path, "corewars8086", "survivors"))
        all_train_set = list(set([survivor[:-1] for survivor in all_train_set]))
        chosen_train_combination = random.sample(all_train_set, k=11)
        if not os.path.exists(survivors_path):
            os.mkdir(survivors_path)
        for f in os.listdir(survivors_path):
            try:
                os.remove(os.path.join(survivors_path, f)) # remove previous survivors
            except Exception:
                continue
        [shutil.copy(os.path.join(self.root_path, "corewars8086", "survivors", survivor+i),
                     survivors_path) for i in ["1","2"] for survivor in chosen_train_combination]

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
            return [score1, score2, min(score1, score2), [-1, -1, -1]]

        os.system("cd {} && java -jar {}".format(os.path.join(self.root_path, "corewars8086_" + worker), self.engine)) # & cgx.bat
        os.remove(os.path.join(survivors_path, individual_name1))
        os.remove(os.path.join(survivors_path, individual_name2))

        # open scores.csv and get the survivors score in comparison to others
        results = self._read_scores(os.path.join(self.root_path, "corewars8086_" + worker),
                                    individual_name1, individual_name2)

        # The data should be in format of m_samples x n_features
        #normalized_indiv_scores = normalize_data(results["indiv_data"])
        #normalized_group_scores = normalize_data(results["group_data"])

        norm_indiv1 = normalize_data(results["indiv_data"], results["indiv1_index"])
        fitness1 = fitness_calculation(norm_indiv1[SCORE], norm_indiv1[LIFETIME], norm_indiv1[BYTES])
        norm_indiv2 = normalize_data(results["indiv_data"], results["indiv2_index"])
        fitness2 = fitness_calculation(norm_indiv2[SCORE], norm_indiv2[LIFETIME], norm_indiv2[BYTES])
        norm_group = normalize_data(results["group_data"], results["group_index"])
        fitness = fitness_calculation(norm_group[SCORE], norm_group[LIFETIME], norm_group[BYTES])

        #print("{} score: {}".format(individual_name1, fitness1))
        #print("{} score: {}".format(individual_name2, fitness2))
        #print("Total {} score: {}".format(individual_name2[:-1], fitness))

        return [fitness1, fitness2, fitness, norm_group]  # how many did the survivor beat * its partial score?

def normalize_data(data, index):
    data = np.array(data).astype(float)
    # normalized score by score/played_game
    score = data[index][SCORE]
    # normalize lifetime by log?
    lifetime = data[index][LIFETIME] #math.log(data[index][LIFETIME], 2) if data[index][LIFETIME] > 0 else 0
    # normilize bytes by log?
    bytes = data[index][BYTES] #math.log(data[index][BYTES], 2) if data[index][BYTES] > 0 else 0
    return [score, lifetime, bytes]
    #return MinMaxScaler().fit_transform(data) # [0-1] range

def fitness_calculation(score, alive_time, bytes_written):
    return round(score + 0.05 * alive_time + 0.05 * bytes_written, 5)
