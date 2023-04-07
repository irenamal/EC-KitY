import os
import random
import sys
import subprocess
import threading
import numpy as np
from eckity.evaluators.simple_individual_evaluator import SimpleIndividualEvaluator
import shutil
from sklearn.preprocessing import StandardScaler, PowerTransformer

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
                f.write("db 0xC0\n")
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
        all_individual_scores = []
        all_alive_time = []
        all_group_scores = []
        score1 = 0
        score2 = 0
        score = 0
        alive_time1 = 0
        alive_time2 = 0
        with open(os.path.join(path, "scores.csv")) as scores:
            flag_ind = False
            scores = scores.readlines()
            for line in scores:
                if line == "Groups:\n":
                    continue
                if not flag_ind and line != "Warriors:\n" and line != "\n":
                    line = line.split(',')
                    if line[0] == individual_name1[:-1]:
                        score = float(line[1][:-1])
                    all_group_scores.append(float(line[1][:-1]))
                    continue
                if line == "Warriors:\n":
                    flag_ind = True
                    continue
                if flag_ind:
                    line = line.split(',')
                    if line[0] == individual_name1:
                        score1 = float(line[1])
                        alive_time1 = float(line[2][:-1])
                    if line[0] == individual_name2:
                        score2 = float(line[1])
                        alive_time2 = float(line[2][:-1])
                    all_individual_scores.append(float(line[1]))
                    all_alive_time.append(float(line[2][:-1]))
        all_individual_scores.sort()
        all_group_scores.sort()
        all_alive_time.sort()
        return {"warrior1": score1, "warrior2": score2, "survivor": score,
                "all_warriors": all_individual_scores, "all_survivors": all_group_scores,
                "alive1": alive_time1, "alive2": alive_time2, "all_alive": all_alive_time}

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
        shutil.copytree(os.path.join(self.root_path, "corewars8086", "survivors"), survivors_path, dirs_exist_ok=True)
        if not os.path.exists(os.path.join(self.root_path, "corewars8086_" + worker, self.engine)):
            shutil.copy(os.path.join(self.root_path, "corewars8086", self.engine),
                        os.path.join(self.root_path, "corewars8086_" + worker, self.engine))
        nasm_path = os.path.join(self.root_path, "corewars8086_" + worker, "nasm")
        if not os.path.exists(nasm_path):
            shutil.copy(self.nasm_path, os.path.join(self.root_path, "corewars8086_" + worker, "nasm"))

        individual_name1 = str(individual.id) + "try1"
        individual_name2 = str(individual.id) + "try2"
        file_path1 = os.path.join(self.root_path, 'survivors', individual_name1 + '.asm')
        file_path2 = os.path.join(self.root_path, 'survivors', individual_name2 + '.asm')
        self._write_survivor_to_file(individual.tree1, file_path1)
        self._write_survivor_to_file(individual.tree2, file_path2)

        score1 = self._compile_survivor(file_path1, individual_name1, survivors_path, nasm_path)
        score2 = self._compile_survivor(file_path2, individual_name2, survivors_path, nasm_path)

        if score1 == -1 or score2 == -1:  # one of the trees in invalid
            if os.path.exists(os.path.join(self.survivors_path, individual_name1)):
                os.remove(os.path.join(self.survivors_path, individual_name1))
            if os.path.exists(os.path.join(self.survivors_path, individual_name2)):
                os.remove(os.path.join(self.survivors_path, individual_name2))
            return [score1, score2, min(score1, score2)]

        os.system("cd {} && java -cp {} il.co.codeguru.corewars8086.CoreWarsEngine".format(os.path.join(self.root_path, "corewars8086_" + worker), self.engine)) # & cgx.bat
        os.remove(os.path.join(survivors_path, individual_name1))
        os.remove(os.path.join(survivors_path, individual_name2))

        # open scores.csv and get the survivors score in comparison to others
        results = self._read_scores(os.path.join(self.root_path, "corewars8086_" + worker),
                                    individual_name1, individual_name2)

        normalized_score1 = normalize_fitness_from_list(results["all_warriors"], results["warrior1"])
        normalized_score2 = normalize_fitness_from_list(results["all_warriors"], results["warrior2"])
        normalized_score = normalize_fitness_from_list(results["all_survivors"], results["survivor"])
        normalized_alive_time1 = normalize_from_list(results["all_alive"], results["alive1"])
        normalized_alive_time2 = normalize_from_list(results["all_alive"], results["alive2"])
        normalized_alive_time = max(normalized_alive_time1, normalized_alive_time2)
        fitness1 = fitness_calculation(normalized_score1, normalized_alive_time1)
        fitness2 = fitness_calculation(normalized_score2, normalized_alive_time2)
        fitness = fitness_calculation(normalized_score, normalized_alive_time)
        print("{} score: {}".format(individual_name1, fitness1))
        print("{} score: {}".format(individual_name2, fitness2))
        print("Total {} score: {}".format(individual_name2[:-1], fitness))

        return [fitness1, fitness2, fitness]  # how many did the survivor beat * its partial score?


def normalize_from_list(list: list, element):
    return list.index(element) + element/sum(list)

def normalize_fitness_from_list(list: list, element):
    return list.index(element) *  10 + element/sum(list)

def fitness_calculation(score, alive_time):
    return round(0.7 * score + 0.3 * alive_time, 5)
