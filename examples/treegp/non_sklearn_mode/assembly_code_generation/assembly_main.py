import random
import shutil
from time import time
import sys
import os
import subprocess

from eckity.algorithms.simple_evolution import SimpleEvolution
from eckity.breeders.simple_breeder import SimpleBreeder
from eckity.creators.gp_creators.grow_typed import GrowCreator
from eckity.genetic_operators.crossovers.subtree_crossover import SubtreeCrossover
from eckity.genetic_operators.mutations.assembly_replacing_mutation import AssemblyReplacingMutation
from eckity.genetic_operators.mutations.subtree_mutation import SubtreeMutation
from eckity.genetic_operators.mutations.erc_mutation import ERCMutation
from eckity.genetic_operators.selections.tournament_selection import TournamentSelection
from eckity.statistics.best_average_worst_statistics import BestAverageWorstStatistics
from eckity.subpopulation import Subpopulation
from eckity.termination_checkers.threshold_from_target_termination_checker import ThresholdFromTargetTerminationChecker
from examples.treegp.non_sklearn_mode.assembly_code_generation.assembly_evaluator import AssemblyEvaluator
from examples.treegp.non_sklearn_mode.assembly_code_generation.assembly_parameters import *

TYPED = True


def clear_folder(path):
    folder = os.listdir(path)
    for f in folder:
        os.remove(os.path.join(path, f))


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
                       [(reg, "address_reg") for reg in addressing_registers] + \
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
                       [("", "section")]

        random.shuffle(terminal_set)

    if TYPED:
        function_set = [(section, ["label", "section", "backwards_jmp", "section"], "section")] + \
                       [(section, ["label", "section", "backwards_jmp"], "section")] + \
                       [(section, ["section", "forward_jmp", "section", "label", "section"], "section")] + \
                       [(section, ["section", "section"], "section")] + \
                       [(lambda opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src)),
                         ["op_double", "reg", "reg", "section"], "section")] + \
                       [(lambda dst, src, *args: print("{} {},{}".format("xchg", dst, src)),
                         ["reg", "reg", "section"], "section")] + \
                       [(lambda opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src)),
                         ["op_double", "reg", "const", "section"], "section")] + \
                       [(lambda dst, *args, opcode=opcode: print("{} {},{}".format(opcode, dst, 1)),
                         ["reg", "section"], "section") for opcode in ["sal", "sar"]] + \
                       [(lambda dst, *args, opcode=opcode: print("{} {},{}".format(opcode, dst, "cl")),
                         ["reg", "section"], "section") for opcode in ["sal", "sar"]] + \
                       [(lambda opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src)),
                         ["op_double", "reg", "address", "section"], "section")] + \
                       [(lambda opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src)),
                         ["op_pointer", "reg", "address", "section"], "section")] + \
                       [(lambda opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src)),
                         ["op_pointer", "reg", "address_reg", "section"], "section")] + \
                       [(lambda opcode, dst, src, *args: print("{} {},{}".format(opcode, dst, src)),
                         ["op_double", "address", "reg", "section"], "section")] + \
                       [(lambda opcode, dst, src, *args: print("{} {} {},{}".format(opcode, "WORD", dst, src)),
                         ["op_double", "address", "const", "section"], "section")] + \
                       [(lambda dst, *args, opcode=opcode: print("{} {} {},{}".format(opcode, "WORD", dst, 1)),
                         ["address", "section"], "section") for opcode in ["sal", "sar"]] + \
                       [(lambda dst, *args, opcode=opcode: print("{} {} {},{}".format(opcode, "WORD", dst, "cl")),
                         ["address", "section"], "section") for opcode in ["sal", "sar"]] + \
                       [(lambda opcode, op, *args: print("{} {}".format(opcode, op)),
                         ["op_single", "reg", "section"], "section")] + \
                       [(lambda opcode, op, *args: print("{} {} {}".format(opcode, "WORD", op)),
                         ["op_single", "address", "section"], "section")] + \
                       [(lambda opcode, op, *args: print("{} {}".format(opcode, op)),
                         ["op_function", "address", "section"], "section")] + \
                       [(lambda opcode, op, *args: print("{} {}".format(opcode, op)),
                         ["op_function", "address_reg", "section"], "section")] + \
                       [(lambda opcode, *args: print("{}".format(opcode)), ["op", "section"], "section")] + \
                       [(lambda opcode, *args: print("{}".format(opcode)), ["op_special", "section"], "section")] + \
                       [(lambda rep, opcode, *args: print("{} {}".format(rep, opcode)),
                         ["op_rep", "op", "section"], "section")] + \
                       [(lambda op, *args: print("{} {}".format("push", op)), ["push_reg", "section"], "section")] + \
                       [(lambda op, *args: print("{} {}".format("push", op)), ["reg"], "section")] + \
                       [(lambda op, *args: print("{} {}".format("pop", op)), ["pop_reg", "section"], "section")] + \
                       [(lambda op, *args: print("{} {}".format("pop", op)), ["reg", "section"], "section")] + \
                       [(lambda opcode, *args: print("{} l{}".format(opcode, len(labels))), ["op_jmp", "label", "section"],
                         "forward_jmp")] * 5 + \
                       [(lambda opcode, *args: print("{} l{}".format(opcode, len(labels)-1)), ["op_jmp", "label", "section"],
                         "backwards_jmp")] * 5 + \
                       [(put_label, ["section"], "label")] * 10 + \
                       [(put_label, ["section"], "section")] * 3 + \
                       [(lambda op, *args: print("{} {}".format("jmp", op)), ["address", "section"], "section")] + \
                       [(lambda op, *args: print("{} {}".format("jmp", op)), ["address_reg", "section"], "section")] + \
                       [(lambda op, *args: print("{} {}".format("jmp", op)), ["reg", "section"], "section")] + \
                       [(lambda const, *args: print("dw 0x{}".format(const)), ["const", "section"], "section")] + \
                       [(lambda op, const, *args: "{} + 0x{}]".format(op[:-1], const), ["address_reg", "const"],
                         "address")]
                       #[(lambda op, const, *args: "{} + {}]".format(op[:-1], const), ["address_reg", "reg"],
                        # "address")]

        random.shuffle(function_set)

    # Create train and test set
    competition_survivors_path = "corewars8086\\competition_survivors"
    run_survivors_path = "corewars8086\\survivors\\"
    competition_size = 10

    all_survivors = os.listdir(competition_survivors_path)
    group_survivors = list(set([survivor[:-1] for survivor in all_survivors]))  # avoid the warrior enumeration

    train_set = random.sample(group_survivors, k=int(0.7 * competition_size))  # train set
    test_set = [test for test in group_survivors if test not in train_set]  # test set

    clear_folder(run_survivors_path)
    copy_survivors(competition_survivors_path, run_survivors_path, train_set)

    # Initialize SimpleEvolution instance
    algo = SimpleEvolution(
        Subpopulation(creators=GrowCreator(init_depth=(1, 20),
                                           terminal_set=terminal_set,
                                           function_set=function_set,
                                           bloat_weight=0.00001),
                      population_size=20,
                      # user-defined fitness evaluation method
                      evaluator=AssemblyEvaluator(),
                      # this is a maximization problem (fitness is accuracy), so higher fitness is better
                      higher_is_better=True,
                      elitism_rate=0.0,
                      # genetic operators sequence to be applied in each generation
                      operators_sequence=[
                          AssemblyReplacingMutation(probability=0.5, arity=2),  # first because it depends on the fitness
                          SubtreeCrossover(probability=0.8, arity=2),
                          SubtreeMutation(probability=0.05, arity=1),
                      ],
                      selection_methods=[
                          # (selection method, selection probability) tuple
                          (TournamentSelection(tournament_size=4, higher_is_better=True), 1)
                      ]
                      ),
        breeder=SimpleBreeder(),
        max_workers=1,
        max_generation=20,
        termination_checker=ThresholdFromTargetTerminationChecker(optimal=5, threshold=0.01),
        statistics=BestAverageWorstStatistics(),
        random_seed=10
    )

    # evolve the generated initial population
    algo.evolve()

    # execute the best individual after the evolution process ends
    clear_folder(run_survivors_path)
    copy_survivors(competition_survivors_path, run_survivors_path, test_set)
    original_stdout = sys.stdout
    with open('winners\\'+str(time())+'.asm', 'w+') as sys.stdout:
        trained_survivor = algo.execute()  # ax="ax", bx="bx", cx="cx", dx="dx", es="es", ds="ds", cs="cs", ss="ss",
                        # abx="[bx]", asi="[si]", adi="[di]", asp="[sp]", abp="[bp]")
    sys.stdout = original_stdout
    print("The winner's test run:")
    algo.population.sub_populations[0].evaluator._evaluate_individual(trained_survivor)
    print('total time:', time() - start_time)


if __name__ == '__main__':
    main()
