import random
import shutil
from time import time
import sys
import os

TYPED = True
WINDOWS = False
if not WINDOWS:
    sys.path.extend(['/cs_storage/irinamal/thesis/EC-KitY/'])

from eckity.algorithms.simple_evolution import SimpleEvolution
from eckity.breeders.simple_breeder import SimpleBreeder
from eckity.creators.gp_creators.grow_typed import GrowCreator
from eckity.genetic_operators.crossovers.subtree_crossover import SubtreeCrossover
from eckity.genetic_operators.mutations.assembly_replacing_mutation import AssemblyReplacingMutation
from eckity.genetic_operators.mutations.assembly_duplication_mutation import AssemblyDuplicationMutation
from eckity.genetic_operators.mutations.subtree_mutation import SubtreeMutation
from eckity.genetic_operators.selections.tournament_selection import TournamentSelection
from eckity.statistics.best_average_worst_statistics import BestAverageWorstStatistics
from eckity.subpopulation import Subpopulation
from eckity.termination_checkers.threshold_from_target_termination_checker import ThresholdFromTargetTerminationChecker
from examples.treegp.non_sklearn_mode.assembly_code_generation.assembly_evaluator import AssemblyEvaluator
from examples.treegp.non_sklearn_mode.assembly_code_generation.assembly_parameters import *

def clear_folder(path):
    folder = os.listdir(path)
    for f in folder:
        os.remove(os.path.join(path, f))

def move_survivors(path):
    """save the survivors into directory of this run for keeping history"""
    folder = os.listdir(path)
    time_stamp = str(time())
    os.mkdir(os.path.join(".", "survivors_" + time_stamp))
    for f in folder:
        os.replace(os.path.join(path, f), os.path.join(".", "survivors_" + time_stamp, f))

def copy_survivors(src_path, dst_path, survivors_set):
    for survivor in survivors_set:
        if os.path.exists(os.path.join(src_path, survivor+"1")):
            shutil.copy(os.path.join(src_path, survivor+"1"), os.path.join(dst_path, survivor+"1"))
        if os.path.exists(os.path.join(src_path, survivor+"2")):
            shutil.copy(os.path.join(src_path, survivor+"2"), os.path.join(dst_path, survivor+"2"))


def main():
    start_time = time()
    if TYPED:
        terminal_set = [(reg, "reg") for reg in general_registers] + \
                       [(reg, "address") for reg in addressing_registers] + \
                       [(const, "const") for const in consts] + \
                       [(reg, "push_reg") for reg in push_registers] + \
                       [(reg, "pop_reg") for reg in pop_registers] + \
                       [(opcode, "op_double") for opcode in opcodes_double] + \
                       [(opcode, "op_single") for opcode in opcodes_single] + \
                       [(opcode, "op_jmp") for opcode in opcodes_jump] + \
                       [(opcode, "op") for opcode in opcodes_no_operands] + \
                       [(opcode, "op_rep") for opcode in opcodes_repeats] + \
                       [(opcode, "op_special") for opcode in opcodes_special] + \
                       [(opcode, "op_function") for opcode in opcodes_function] + \
                       [(opcode, "op_pointer") for opcode in opcodes_pointers] + \
                       [(opcode, "op_ret") for opcode in opcode_ret] + \
                       [(opcode, "op_double_no_const") for opcode in opcodes_double_no_cost] + \
                       [(opcode, "op_shift") for opcode in opcodes_shift] + \
                       [("", "section")]

        random.shuffle(terminal_set)

    if TYPED:
        function_set = [(section, ["label", "section", "backwards_jmp", "section"], "section")] + \
                       [(section, ["label", "section", "backwards_jmp"], "section")] + \
                       [(section, ["section", "forward_jmp", "section", "label", "section"], "section")] + \
                       [(section, ["label", "section", "call_func", "backwards_jmp", "label", "section", "return"], "section")] + \
                       [(lambda f, opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src), file=f),
                         ["op_double", "reg", "reg", "section"], "section")] + \
                       [(lambda f, opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src), file=f),
                         ["op_double", "reg", "const", "section"], "section")] + \
                       [(lambda f, opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src), file=f),
                         ["op_double", "reg", "address", "section"], "section")] + \
                       [(lambda f, opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src), file=f),
                         ["op_double", "address", "reg", "section"], "section")] + \
                       [(lambda f, opcode, dst, src, *args: print("{} {} {},{}".format(opcode, "WORD", dst, src), file=f),
                         ["op_double", "address", "const", "section"], "section")] + \
                       [(lambda f, opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src), file=f),
                         ["op_pointer", "reg", "address", "section"], "section")] + \
                       [(lambda f, opcode, op, *args: print("{} {}".format(opcode, op), file=f),
                         ["op_single", "reg", "section"], "section")] + \
                       [(lambda f, opcode, op, *args: print("{} {} {}".format(opcode, "WORD", op), file=f),
                         ["op_single", "address", "section"], "section")] + \
                       [(lambda f, opcode, op, *args: print("{} {}".format(opcode, op), file=f),
                         ["op_function", "address", "section"], "section")] + \
                       [(lambda f, *args: print("call l{}".format(len(labels)), file=f),
                         ["section"], "call_func")] + \
                       [(lambda f, *args: print("ret", file=f), ["section"], "return")] + \
                       [(lambda f, opcode, *args: print("{}".format(opcode), file=f),
                         ["op", "section"], "section")] + \
                       [(lambda f, opcode, *args: print("{}".format(opcode), file=f),
                         ["op_special", "section"], "section")] + \
                       [(lambda f, rep, opcode, *args: print("{} {}".format(rep, opcode), file=f),
                         ["op_rep", "op", "section"], "section")] + \
                       [(lambda f, op, *args: print("{} {}".format("push", op), file=f),
                         ["push_reg", "section"], "section")] + \
                       [(lambda f, op, *args: print("{} {}".format("pop", op), file=f),
                         ["pop_reg", "section"], "section")] + \
                       [(lambda f, *args: put_label(f), ["section"], "label")] + \
                       [(lambda f, opcode, *args: print("{} l{}".format(opcode, len(labels)), file=f),
                         ["op_jmp", "section"], "forward_jmp")] + \
                       [(lambda f, opcode, *args: print("{} l{}".format(opcode, len(labels) - 1), file=f),
                         ["op_jmp", "section"], "backwards_jmp")] + \
                       [(lambda f, op, *args: print("{} {}".format("jmp", op), file=f), ["reg", "section"], "section")] + \
                       [(lambda f, op, *args: print("{} {}".format("jmp", op), file=f), ["address", "section"], "section")] + \
                       [(lambda f, const, *args: print("dw {}".format(const), file=f), ["const", "section"], "section")] + \
                       [(lambda f, op, const, *args: "{} + {}]".format(op[:-1], const), ["address", "const"], "address")] + \
                       [(lambda f, opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src), file=f),
                         ["op_double_no_const", "reg", "reg", "section"], "section")] + \
                       [(lambda f, opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src), file=f),
                         ["op_double_no_const", "reg", "address", "section"], "section")] + \
                       [(lambda f, opcode, dst, *args, param=param: print("{} {},{}".format(opcode, dst, param), file=f),
                         ["op_shift", "reg", "section"], "section") for param in ["cl"]] + \
                       [(lambda f, opcode, dst, *args, param=param: print("{} {} {},{}".format(opcode, "WORD", dst, param), file=f),
                         ["op_shift", "address", "section"], "section") for param in ["cl"]]

        random.shuffle(function_set)

    # Create train and test set
    if WINDOWS:
        competition_survivors_path = "corewars8086\\competition_survivors"
        run_survivors_path = "corewars8086\\survivors\\"
        nasm_path = "C:\\Users\\irinu\\Desktop\\thesis\\nasm-2.16.01\\nasm.exe"
        root_path = ".\\"
    else:
        competition_survivors_path = "/cs_storage/irinamal/thesis/corewars8086/competition_survivors"
        run_survivors_path = "/cs_storage/irinamal/thesis/corewars8086/survivors"
        root_path = "/cs_storage/irinamal/thesis/"
        nasm_path = "/cs_storage/irinamal/thesis/nasm-2.15.05/nasm"

    competition_size = 30

    all_survivors = os.listdir(competition_survivors_path)
    group_survivors = list(set([survivor[:-1] for survivor in all_survivors]))  # avoid the warrior enumeration

    train_set = random.sample(group_survivors, k=int(0.7 * competition_size))  # train set
    test_set = random.sample([test for test in group_survivors if test not in train_set], k=int(0.3 * competition_size))  # test set

    clear_folder(run_survivors_path)
    copy_survivors(competition_survivors_path, run_survivors_path, train_set)

    # Initialize SimpleEvolution instance
    algo = SimpleEvolution(
        Subpopulation(creators=GrowCreator(init_depth=(1, 22),
                                           terminal_set=terminal_set,
                                           function_set=function_set,
                                           bloat_weight=0.00001),
                      population_size=100,
                      # user-defined fitness evaluation method
                      evaluator=AssemblyEvaluator(root_path=root_path, nasm_path=nasm_path),
                      # this is a maximization problem (fitness is accuracy), so higher fitness is better
                      higher_is_better=True,
                      elitism_rate=0.0,
                      # genetic operators sequence to be applied in each generation
                      # arity of an operator is on how many individuals it works on per time
                      operators_sequence=[
                          AssemblyDuplicationMutation(probability=0.2, arity=1),  # first because it depends on the fitness
                          AssemblyReplacingMutation(probability=0.2, arity=2), # swap between inner trees of 2 individuals
                          SubtreeCrossover(probability=0.8, arity=2), # crossover inner trees of 2 individuals, can be more
                          SubtreeMutation(probability=0.4, arity=1), # mutate a subtree of one inner tree of 1 individual
                      ],
                      selection_methods=[
                          # (selection method, selection probability) tuple
                          (TournamentSelection(tournament_size=4, higher_is_better=True), 1)
                      ]
                      ),
        breeder=SimpleBreeder(),
        max_workers=8,
        max_generation=50,
        termination_checker=ThresholdFromTargetTerminationChecker(optimal=1, threshold=0.00001),
        statistics=BestAverageWorstStatistics(),
        random_seed=time(),
        root_path=root_path
    )

    # evolve the generated initial population
    algo.evolve()

    # execute the best individual after the evolution process ends
    clear_folder(run_survivors_path)
    copy_survivors(competition_survivors_path, run_survivors_path, test_set)

    print("The winner's test run:")
    test_results = algo.population.sub_populations[0].evaluator._evaluate_individual(algo.best_of_run_copy_)
    print("Total fitness: {}\nTree1 fitness: {}\nTree2 fitness: {}\n"
          "Score:{}, Lifetime: {}, Bytes written: {}, Writing rate:{}".format(test_results[2], test_results[0],
                                                                              test_results[1],
                                                                              test_results[3][0], test_results[3][1],
                                                                              test_results[3][2], test_results[3][3]))
    print('total time:', time() - start_time)

    algo.execute(open(os.path.join(root_path, "winners", "t_"+str(time())+"f_"+str(test_results[2])+'.asm'), 'w+'))  # ax="ax", bx="bx", cx="cx", dx="dx", es="es", ds="ds", cs="cs", ss="ss",
                        # abx="[bx]", asi="[si]", adi="[di]", asp="[sp]", abp="[bp]")

    clear_folder(os.path.join(root_path, "survivors"))

    # Delete the folders created for each thread
    for file in os.listdir(root_path):
        if file.__contains__("corewars8086_"):
            shutil.rmtree(os.path.join(root_path, file))


if __name__ == '__main__':
    main()
