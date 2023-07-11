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

    def should_terminate(self, population, best_individual, gen_number):
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
        # score should be the best, which means 1. Lifetime and written bytes don't have to
        #return abs(best_individual.fitness_parts[0] - self.optimal) <= self.threshold and gen_number >= 4
        if abs(best_individual.fitness_parts[0] - self.optimal) <= self.threshold:
            if best_individual.fitness.get_pure_fitness() > self.prev_res:
                self.prev_res = best_individual.fitness.get_pure_fitness()
                self.strike = 0
            else:
                # There wasn't an improvement
                self.strike += 1

        if self.strike >= 100:
            # If there wasn't a winning improvement for 100 generations, stop the evolution
            return True

        return False
