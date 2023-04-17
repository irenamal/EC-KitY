from eckity.genetic_operators.genetic_operator import GeneticOperator


class AssemblyDuplicationMutation(GeneticOperator):
    def __init__(self, probability=1, arity=1, init_depth=None, events=None):
        super().__init__(probability=probability, arity=arity, events=events)
        self.init_depth = init_depth

    def apply(self, individuals):
        """
        Perform duplication mutation: duplicates the tree with the higher fitness.

        Returns
        -------
        The modified individuals.
        """

        individuals = self._apply_duplication(individuals)
        self.applied_individuals = individuals
        return individuals

    def _apply_duplication(self, individuals):
        # Duplicate the tree with the higher fitness to be tree1 and tree2
        for ind in individuals:
            fitness1 = ind.tree1.get_pure_fitness()
            fitness2 = ind.tree2.get_pure_fitness()
            if fitness1 == -2 or fitness2 == -2:
                print("fitness not evaluated")
                return
            if fitness1 > fitness2:
                ind.tree2 = ind.tree1.clone()  # for changes in one not affect the second
            elif fitness1 < fitness2:
                ind.tree1 = ind.tree2.clone()
            # if equal, do nothing
        return individuals

