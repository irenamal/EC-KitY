import os
import random
import sys
import subprocess
from eckity.evaluators.simple_individual_evaluator import SimpleIndividualEvaluator


class AssemblyEvaluator(SimpleIndividualEvaluator):

    def __init__(self):
        super().__init__()
        self.nasm_path = "C:\\Users\\user\\AppData\\Local\\bin\\NASM\\nasm"
        self.survivors_path = "corewars8086\\survivors\\"
        for f in os.listdir("survivors"):
            os.remove(os.path.join("survivors", f))

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

        individual_name1 = str(individual.id) + "try1"
        individual_name2 = str(individual.id) + "try2"
        original_stdout = sys.stdout
        file_path1 = 'survivors\\' + individual_name1 + '.asm'
        file_path2 = 'survivors\\' + individual_name2 + '.asm'
        with open(file_path1, 'w+') as f:
            f.write("@start:\n")
            sys.stdout = f
            individual.execute1() #ax="ax", bx="bx", cx="cx", dx="dx", es="es", ds="ds", cs="cs", ss="ss",
                               #abx="[bx]", asi="[si]", adi="[di]", asp="[sp]", abp="[bp]")
            sys.stdout = original_stdout
            f.write("@end:\n")
            f.seek(0, os.SEEK_END)
            while f.tell() < 512:
                f.write("db 0xC0\n")
                f.seek(0, os.SEEK_END)
        f.close()

        with open(file_path2, 'w+') as f:
            f.write("@start:\n")
            sys.stdout = f
            individual.execute2() #ax="ax", bx="bx", cx="cx", dx="dx", es="es", ds="ds", cs="cs", ss="ss",
                               #abx="[bx]", asi="[si]", adi="[di]", asp="[sp]", abp="[bp]")
            sys.stdout = original_stdout
            f.write("@end:\n")
            f.seek(0, os.SEEK_END)
            while f.tell() < 512:
                f.write("db 0xC0\n")
                f.seek(0, os.SEEK_END)
        f.close()

        score1 = 0
        score2 = 0

        proc = subprocess.Popen([self.nasm_path, "-f bin", file_path1, "-o", self.survivors_path + individual_name1],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if "error" in str(stderr):
            print(stderr)
            score1 = -1  # fitness = -1
        proc = subprocess.Popen([self.nasm_path, "-f bin", file_path2, "-o", self.survivors_path + individual_name2],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if "error" in str(stderr):
            print(stderr)
            score2 = -1  # fitness = -1

        if score1 == -1 or score2 == -1:  # one of the trees in invalid
            if os.path.exists(self.survivors_path + individual_name1):
                os.remove(self.survivors_path + individual_name1)
            if os.path.exists(self.survivors_path + individual_name2):
                os.remove(self.survivors_path + individual_name2)
            return [score1, score2, min(score1, score2)]

        os.system("cd corewars8086 & cgx.bat")
        os.remove(self.survivors_path + individual_name1)
        os.remove(self.survivors_path + individual_name2)

        # open scores.csv and get the survivors score in comparison to others
        score = 0
        all_individual_scores = []
        all_group_scores = []
        # compute fitness for each of the trees
        with open("corewars8086\\scores.csv") as scores:
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
                        score1 = float(line[1][:-1])
                    if line[0] == individual_name2:
                        score2 = float(line[1][:-1])
                    all_individual_scores.append(float(line[1][:-1]))

        all_individual_scores.sort()
        all_group_scores.sort()
        fitness1 = all_individual_scores.index(score1) + (score1 / sum(all_individual_scores))
        fitness2 = all_individual_scores.index(score2) + (score2 / sum(all_individual_scores))
        fitness = all_group_scores.index(score) + (score / sum(all_group_scores))
        print("{} score: {}".format(individual_name1, fitness1))
        print("{} score: {}".format(individual_name2, fitness2))
        print("Total {} score: {}".format(individual_name2[:-1], fitness))

        return [fitness1, fitness2, fitness]  # how many did the survivor beat * its partial score?
