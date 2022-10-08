import random
from time import time

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

    # The terminal set of the tree will contain the mux inputs (d0-d7 in a 8-3 mux gate),
    # 3 select lines (s0-s2 in a 8-3 mux gate) and the constants 0 and 1
    if TYPED:
        terminal_set = [(reg, "reg") for reg in general_registers] +\
                       [(const, "const") for const in consts] + \
                       [(label, "label") for label in labels]
        random.shuffle(terminal_set)

    # Logical functions: and, or, not and if-then-else
    if TYPED:
        function_set = [(func, ["reg", None], None) for func in one_op] + \
                       [(func, ["reg", "reg", None], None) for func in two_op_regs] + \
                       [(func, ["reg", "const", None], None) for func in two_op_reg_const] + \
                       [(func, ["label", None], None) for func in jumps] + \
                       [(func, ["reg"], None) for func in one_op] + \
                       [(func, ["reg", "reg"], None) for func in two_op_regs] + \
                       [(func, ["reg", "const"], None) for func in two_op_reg_const] + \
                       [(func, ["label"], None) for func in jumps]

        random.shuffle(function_set)
        # function_set = [(func, ["reg", None], None) for func in functions_with_one_operand] + \
        # [(func, ["reg", "reg", None], None) for func in functions_with_two_operands] + \
        # [(func, ["reg", "const"], None) for func in functions_with_two_operands] + \
        # [(func, ["label", "reg", None], None) for func in labeled_functions_with_one_operand] + \
        # [(func, ["label", None], None) for func in jumps] + \
        # [(func, ["reg"], None) for func in functions_with_one_operand] + \
        # [(func, ["reg", "reg"], None) for func in functions_with_two_operands] + \
        # [(func, ["reg", "const", None], None) for func in functions_with_two_operands]
        # [(put_label, ["label", None], None)] + \

    # Initialize SimpleEvolution instance
    algo = SimpleEvolution(
        Subpopulation(creators=GrowCreator(init_depth=(1, 50),
                                           terminal_set=terminal_set,
                                           function_set=function_set,
                                           bloat_weight=0.00001),
                      population_size=10,
                      # user-defined fitness evaluation method
                      evaluator=AssemblyEvaluator(),
                      # this is a maximization problem (fitness is accuracy), so higher fitness is better
                      higher_is_better=True,
                      elitism_rate=0.0,
                      # genetic operators sequence to be applied in each generation
                      operators_sequence=[
                          SubtreeCrossover(probability=0.8, arity=2),
                          SubtreeMutation(probability=0.1, arity=1)
                      ],
                      selection_methods=[
                          # (selection method, selection probability) tuple
                          (TournamentSelection(tournament_size=7, higher_is_better=True), 1)
                      ]
                      ),
        breeder=SimpleBreeder(),
        max_workers=1,
        max_generation=40,
        termination_checker=ThresholdFromTargetTerminationChecker(optimal=1, threshold=0.01),
        statistics=BestAverageWorstStatistics(),
        random_seed=10
    )

    # evolve the generated initial population
    algo.evolve()

    # execute the best individual after the evolution process ends
    exec1 = algo.execute(ax="ax", bx="bx", cx="cx", dx="dx")

    print('execute result', exec1)

    print('total time:', time() - start_time)


if __name__ == '__main__':
    main()
