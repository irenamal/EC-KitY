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

    if TYPED:
        terminal_set = [(reg, "reg") for reg in general_registers] + \
                       [(const, "const") for const in consts]

        random.shuffle(terminal_set)

    if TYPED:
        function_set = [(statement1, ["label", "instruction", "backwards_jmp", "statement"], "statement"),
                        (statement2, ["forward_jmp", "instruction", "label", "statement"], "statement"),
                        (statement3, ["instruction", "statement"], "statement"),
                        (statement4, ["instruction"], "statement")] * 25 + \
                       [(func, ["reg", "instruction"], "instruction") for func in one_op] + \
                       [(func, ["reg", "reg", "instruction"], "instruction") for func in two_op_regs] + \
                       [(func, ["reg", "const", "instruction"], "instruction") for func in two_op_regs] + \
                       [(func, ["reg"], "instruction") for func in one_op] + \
                       [(func, ["reg", "reg"], "instruction") for func in two_op_regs] + \
                       [(func, ["reg", "const"], "instruction") for func in two_op_regs] + \
                       [(func, [], "forward_jmp") for func in forward_jumps] + \
                       [(func, [], "backwards_jmp") for func in backwards_jumps] + \
                       [(put_label, [], "label")] * 10

        random.shuffle(function_set)

    # Initialize SimpleEvolution instance
    algo = SimpleEvolution(
        Subpopulation(creators=GrowCreator(init_depth=(1, 50),
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
                          SubtreeCrossover(probability=0.8, arity=2),
                          SubtreeMutation(probability=0.2, arity=1)
                      ],
                      selection_methods=[
                          # (selection method, selection probability) tuple
                          (TournamentSelection(tournament_size=7, higher_is_better=True), 1)
                      ]
                      ),
        breeder=SimpleBreeder(),
        max_workers=1,
        max_generation=15,
        termination_checker=ThresholdFromTargetTerminationChecker(optimal=1, threshold=0.01),
        statistics=BestAverageWorstStatistics(),
        random_seed=10
    )

    # evolve the generated initial population
    algo.evolve()

    # execute the best individual after the evolution process ends
    exec1 = algo.execute(ax="ax", bx="bx", cx="cx", dx="dx")

    print('total time:', time() - start_time)


if __name__ == '__main__':
    main()
