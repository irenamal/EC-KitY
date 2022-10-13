import random
from time import time
import sys

from eckity.algorithms.simple_evolution import SimpleEvolution
from eckity.breeders.simple_breeder import SimpleBreeder
from eckity.creators.gp_creators.grow_typed import GrowCreator
from eckity.genetic_operators.crossovers.subtree_crossover import SubtreeCrossover
from eckity.genetic_operators.mutations.subtree_mutation import SubtreeMutation
from eckity.genetic_operators.selections.tournament_selection import TournamentSelection
from eckity.statistics.best_average_worst_statistics import BestAverageWorstStatistics
from eckity.subpopulation import Subpopulation
from eckity.termination_checkers.threshold_from_target_termination_checker import ThresholdFromTargetTerminationChecker
from examples.treegp.non_sklearn_mode.assembly_code_generation.assembly_evaluator import AssemblyEvaluator

from examples.treegp.non_sklearn_mode.assembly_code_generation.assembly_parameters import *
TYPED = True


def main():

    start_time = time()

    if TYPED:
        terminal_set = [(reg, "reg") for reg in general_registers] + \
                       [(reg, "address") for reg in addressing_registers] + \
                       [(const, "const") for const in consts]

        random.shuffle(terminal_set)

    if TYPED:
        function_set = [(section, ["label", "section", "backwards_jmp", "section"], "section")] * 5 + \
                       [(section, ["section", "forward_jmp", "section", "label", "section"], "section")] * 5 + \
                       [(section, ["instruction", "section"], "section")] * 20 + \
                       [(section, ["instruction"], "section")] * 15 + \
                       [(lambda dst, src, *args, opcode=opcode: print("{} {},{}".format(opcode, dst, src)),
                         ["reg", "reg"], "instruction") for opcode in opcodes_reg_reg] + \
                       [(lambda dst, src, *args, opcode=opcode: print("{} {},{}".format(opcode, dst, src)),
                         ["reg", "const"], "instruction") for opcode in opcodes_reg_const] + \
                       [(lambda dst, src, *args, opcode=opcode: print("{} {},{}".format(opcode, dst, src)),
                         ["reg", "address"], "instruction") for opcode in opcodes_reg_address] + \
                       [(lambda dst, src, *args, opcode=opcode: print("{} {},{}".format(opcode, dst, src)),
                         ["address", "reg"], "instruction") for opcode in opcodes_address_reg] + \
                       [(lambda dst, src, *args, opcode=opcode: print("{} {},{}".format(opcode, dst, src)),
                         ["address", "const"], "instruction") for opcode in opcodes_address_const] + \
                       [(lambda op, *args, opcode=opcode: print("{} {}".format(opcode, op)),
                         ["reg"], "instruction") for opcode in opcodes_reg] + \
                       [(lambda op, *args, opcode=opcode: print("{} {}".format(opcode, op)),
                         ["address"], "instruction") for opcode in opcodes_address] + \
                       [(lambda *args, opcode=opcode: print("{} l{}".format(opcode, len(labels))), [], "forward_jmp")
                        for opcode in opcodes_jump] + \
                       [(lambda *args, opcode=opcode: print("{} l{}".format(opcode, len(labels)-1)), [], "backwards_jmp")
                        for opcode in opcodes_jump] + \
                       [(put_label, [], "label")] * 10

        random.shuffle(function_set)

    # Initialize SimpleEvolution instance
    algo = SimpleEvolution(
        Subpopulation(creators=GrowCreator(init_depth=(1, 30),
                                           terminal_set=terminal_set,
                                           function_set=function_set,
                                           bloat_weight=0.00001),
                      population_size=50,
                      # user-defined fitness evaluation method
                      evaluator=AssemblyEvaluator(),
                      # this is a maximization problem (fitness is accuracy), so higher fitness is better
                      higher_is_better=True,
                      elitism_rate=0.01,
                      # genetic operators sequence to be applied in each generation
                      operators_sequence=[
                          SubtreeCrossover(probability=0.8, arity=2),
                          SubtreeMutation(probability=0.4, arity=1)
                      ],
                      selection_methods=[
                          # (selection method, selection probability) tuple
                          (TournamentSelection(tournament_size=7, higher_is_better=True), 1)
                      ]
                      ),
        breeder=SimpleBreeder(),
        max_workers=1,
        max_generation=15,
        termination_checker=ThresholdFromTargetTerminationChecker(optimal=7, threshold=0.01),
        statistics=BestAverageWorstStatistics(),
        random_seed=10
    )

    # evolve the generated initial population
    algo.evolve()

    # execute the best individual after the evolution process ends
    original_stdout = sys.stdout
    with open('winners\\'+str(time())+'.asm', 'w+') as sys.stdout:
        algo.execute(ax="ax", bx="bx", cx="cx", dx="dx", abx="[bx]", asi="[si]", adi="[di]")
    sys.stdout = original_stdout

    print('total time:', time() - start_time)


if __name__ == '__main__':
    main()
