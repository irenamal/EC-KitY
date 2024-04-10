import time

from eckity.termination_checkers.termination_checker import TerminationChecker


class ThresholdFromTargetTerminationChecker(TerminationChecker):
    """
    Concrete Termination Checker that checks the distance from best existing fitness value to target fitness value.

    Parameters
    ----------
    optimal: float, default=0.
        Target fitness value.
        This termination checker checks if the currently best fitness is "close enough" to the optimal value.

    threshold: float, default=0.
        How close should the current best fitness be to the target fitness.

    higher_is_better: bool, default=False
        Determines if higher fitness values are better.
    """
    def __init__(self, optimal=0., threshold=0., higher_is_better=False):
        super().__init__()
        self.optimal = optimal
        self.threshold = threshold
        self.higher_is_better = higher_is_better
        self.strike = 0
        self.prev_res = -1
        self.adjusted = False

    def should_terminate(self, population, best_individual, gen_number, max=0, avg=0):
        """
        Determines if the currently best fitness is close enough to the target fitness.
        If so, recommends the algorithm to terminate early.

        Parameters
        ----------
        population: Population
            The evolutionary experiment population of individuals.

        best_individual: Individual
            The individual that has the best fitness of the current generation.

        gen_number: int
            Current generation number.

        Returns
        -------
        bool
            True if the algorithm should terminate early, False otherwise.
        """
        # check for intended stop condition to change the opponent against the wining survivor.
        # stop for 20 min when the average fitness is higher than 1.1 (score must be higher than 0.5)
        if not self.adjusted and avg > 1.1:
            print("Winning achieved, adjust the opponent")
            time.sleep(60*20)
            self.adjusted = True
            return False

        # score should be the best, which means 1. Lifetime and written bytes don't have to
        if abs(best_individual.fitness_parts[0] - self.optimal) <= self.threshold:
            if best_individual.fitness.get_pure_fitness() > self.prev_res:
                self.prev_res = best_individual.fitness.get_pure_fitness()
                self.strike = 0
            else:
                # There was a win but wasn't an improvement, but we still win
                self.strike += 1
        else:
            # we lost - we need winning with no improvement strike
            self.strike = 0

        if self.strike >= 200 and abs(max - avg) < 0.25:
            # If there wasn't a winning improvement for 200 generations, stop the evolution
            return True

        return False
