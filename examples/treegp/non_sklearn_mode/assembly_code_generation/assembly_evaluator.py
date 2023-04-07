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
            return -10  # fitness = -1
        return 0

    def _read_scores(self, path, individual_name1, individual_name2):
        all_individual_scores = []
        all_alive_time = []
        all_bytes_written = []
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
                        alive_time1 = float(line[2])
                        bytes1 = float(line[3][:-1])
                    if line[0] == individual_name2:
                        score2 = float(line[1])
                        alive_time2 = float(line[2])
                        bytes2 = float(line[3][:-1])
                    all_individual_scores.append(float(line[1]))
                    all_alive_time.append(float(line[2]))
                    all_bytes_written.append(float(line[3][:-1]))
        data = [all_individual_scores, all_alive_time, all_bytes_written]
        data = np.transpose(data)

        return {"data": data,
                "all_group_scores": np.array(all_group_scores).reshape(-1,1),
                "score": all_group_scores.index(score),
                "score1": all_individual_scores.index(score1),
                "score2": all_individual_scores.index(score2),
                "alive1": all_alive_time.index(alive_time1),
                "alive2": all_alive_time.index(alive_time2),
                "bytes1": all_bytes_written.index(bytes1),
                "bytes2": all_bytes_written.index(bytes2) }

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

        if score1 == -10 or score2 == -10:  # one of the trees in invalid
            if os.path.exists(os.path.join(survivors_path, individual_name1)):
                os.remove(os.path.join(survivors_path, individual_name1))
            if os.path.exists(os.path.join(survivors_path, individual_name2)):
                os.remove(os.path.join(survivors_path, individual_name2))
            return [score1, score2, min(score1, score2), [-10, -10, -10]]

        os.system("cd {} && java -cp {} il.co.codeguru.corewars8086.CoreWarsEngine".format(os.path.join(self.root_path, "corewars8086_" + worker), self.engine)) # & cgx.bat
        os.remove(os.path.join(survivors_path, individual_name1))
        os.remove(os.path.join(survivors_path, individual_name2))

        # open scores.csv and get the survivors score in comparison to others
        results = self._read_scores(os.path.join(self.root_path, "corewars8086_" + worker),
                                    individual_name1, individual_name2)

        normalized_data = normalize_data(results["data"])
     #   normalized_group_scores = normalize_data(results["all_group_scores"])

        fitness1 = fitness_calculation(normalized_data[results["score1"]][0],
                                       normalized_data[results["alive1"]][1],
                                       normalized_data[results["bytes1"]][2])
        fitness2 = fitness_calculation(normalized_data[results["score2"]][0],
                                       normalized_data[results["alive2"]][1],
                                       normalized_data[results["bytes2"]][2])
        #fitness = round(normalized_group_scores[results["score"]][0], 5)
        survivor_score = normalized_data[results["score1"]][0] + normalized_data[results["score2"]][0]
        survivor_alive = max(normalized_data[results["alive1"]][1], normalized_data[results["alive2"]][1])
        survivor_bytes = normalized_data[results["bytes1"]][2] + normalized_data[results["bytes2"]][2]
        fitness = fitness_calculation(survivor_score, survivor_alive, survivor_bytes)
        print("{} score: {}".format(individual_name1, fitness1))
        print("{} score: {}".format(individual_name2, fitness2))
        print("Total {} score: {}".format(individual_name2[:-1], fitness))

        return [fitness1, fitness2, fitness, [survivor_score, survivor_alive, survivor_bytes]]  # how many did the survivor beat * its partial score?

def normalize_data(data):
    return StandardScaler().fit_transform(data)

def fitness_calculation(score, alive_time, bytes_written):
    return round(0.5 * score + 0.25 * alive_time + 0.25 * bytes_written, 5)
