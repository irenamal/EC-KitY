import random

from eckity.genetic_operators.genetic_operator import GeneticOperator


class SubtreeCrossover(GeneticOperator):
    def __init__(self, probability=1, arity=2, events=None):
        self.individuals = None
        self.applied_individuals = None
        super().__init__(probability=probability, arity=arity, events=events)

    def _apply(self, individuals):
        assert len(individuals) == self.arity, f'Expected individuals list of size {self.arity}, got {len(individuals)}'

        self.individuals = individuals

        # select a random subtree from each individual's tree
        subtrees = [ind.random_subtree() for ind in individuals]

        # assign the next individual's subtree to the current individual's tree
        for i in range(len(individuals) - 1):
            for j in range(individuals[i].size()):  # crossover can fail due to type mismatch
                if individuals[i].replace_subtree(subtrees[i + 1]):
                    break
                subtrees[i + 1] = individuals[i + 1].random_subtree()

        # to complete the crossover circle, assign the first subtree to the last individual
        for i in range(individuals[-1].size()):  # crossover can fail due to type mismatch
            if individuals[-1].replace_subtree(subtrees[0]):
                break
            subtrees[0] = individuals[0].random_subtree()

        self.applied_individuals = individuals
        return individuals

    def crossover_type1(self, individuals):
        xo_result = self._apply([individuals[0].tree1, individuals[1].tree1])
        individuals[0].tree1 = xo_result[0]
        individuals[1].tree1 = xo_result[1]
        return individuals

    def crossover_type2(self, individuals):
        xo_result = self._apply([individuals[0].tree2, individuals[1].tree2])
        individuals[0].tree2 = xo_result[0]
        individuals[1].tree2 = xo_result[1]
        return individuals

    def crossover_type3(self, individuals):
        temp_tree = individuals[0].tree1
        individuals[0].tree1 = individuals[1].tree1
        individuals[1].tree1 = temp_tree
        return individuals

    def apply(self, individuals):
        """
        Perform subtree crossover between this tree and `other` tree:
            1. Select random node from `other` tree
            2. Get subtree rooted at selected node
            1. Select a random node in this tree
            2. Place `other` selected subtree at this node, replacing current subtree

        Parameters
        ----------
        individuals
        select_func: callable
        Selection method used to receive additional individuals to perform crossover on

        individual: Tree
        tree individual to perform crossover on

        Returns
        -------
        a new, modified individual
        """

        # choose one option of XO from 3 types:
        # 1. between the two first trees
        # 2. between the two second trees
        # 3. replace one first tree with the other one
        option = random.random()
        if 0 <= option < 0.33:
            return self.crossover_type1(individuals)
        elif 0.33 <= option < 0.66:
            return self.crossover_type2(individuals)
        elif 0.66 <= option < 1:
            return self.crossover_type3(individuals)


