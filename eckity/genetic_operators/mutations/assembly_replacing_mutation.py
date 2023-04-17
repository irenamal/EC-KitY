import random
from eckity.genetic_operators.genetic_operator import GeneticOperator


class AssemblyReplacingMutation(GeneticOperator):
    def __init__(self, probability=1, arity=2, init_depth=None, events=None):
        super().__init__(probability=probability, arity=arity, events=events)
        self.init_depth = init_depth

    def apply(self, individuals):
        """
        Perform replacing mutation: replaces one tree of one individual with one tree of the other in
        the same probability.
        ind[0].tree1 <-> ind[1].tree1
        ind[0].tree2 <-> ind[1].tree2
        ind[0].tree1 <-> ind[1].tree2
        ind[0].tree2 <-> ind[1].tree1

        Returns
        -------
        The modified individuals.
        """

        individuals = self._apply_swap(individuals)
        self.applied_individuals = individuals
        return individuals

    def _apply_swap(self, individuals):
        if len(individuals) < 2:
            return individuals
        option = random.random()
        if 0 <= option < 0.25:
            individuals[0].tree1, individuals[1].tree1 = individuals[1].tree1, individuals[0].tree1
        elif 0.25 <= option < 0.5:
            individuals[0].tree2, individuals[1].tree2 = individuals[1].tree2, individuals[0].tree2
        elif 0.5 <= option < 0.75:
            individuals[0].tree1, individuals[1].tree2 = individuals[1].tree2, individuals[0].tree1
        elif 0.75 <= option <= 1:
            individuals[0].tree2, individuals[1].tree1 = individuals[1].tree1, individuals[0].tree2
        return individuals
