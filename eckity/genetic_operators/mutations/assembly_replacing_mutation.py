from random import randint

from eckity.creators.gp_creators.grow_typed import GrowCreator
from eckity.genetic_operators.genetic_operator import GeneticOperator


class AssemblyReplacingMutation(GeneticOperator):
    def __init__(self, probability=1, arity=1, init_depth=None, events=None):
        super().__init__(probability=probability, arity=arity, events=events)
        self.init_depth = init_depth

    def apply(self, individuals):
        """
        Perform subtree mutation: select a subtree at random to be replaced by a new, randomly generated subtree.

        Returns
        -------
        None.
        """

        for ind in individuals:
            # Duplicate the tree with the higher fitness to be tree1 and tree2
            fitness1 = ind.tree1.get_pure_fitness()
            fitness2 = ind.tree2.get_pure_fitness()
            if fitness1 == -20 or fitness2 == -20:
                print("fitness not evaluated")
                break
            if fitness1 > fitness2:
                ind.tree2 = ind.tree1.clone()  # for changes in on not affect the second
            elif fitness1 < fitness2:
                ind.tree1 = ind.tree2.clone()
            # if equal, do nothing

        self.applied_individuals = individuals
        return individuals
