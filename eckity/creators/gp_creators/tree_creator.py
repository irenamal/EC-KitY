from eckity.creators.creator import Creator
from eckity.fitness.simple_fitness import SimpleFitness
from eckity.genetic_encodings.gp.tree.functions import f_add, f_sub, f_mul, f_div
from eckity.fitness.gp_fitness import GPFitness
from examples.treegp.non_sklearn_mode.assembly_code_generation.assembly_individual import AssemblyIndividual

from abc import abstractmethod


class GPTreeCreator(Creator):
    def __init__(self,
                 init_depth=None,
                 function_set=None,
                 terminal_set=None,
                 erc_range=None,
                 fitness_type=SimpleFitness,
                 bloat_weight=0.1,
                 events=None):
        if events is None:
            events = ["after_creation"]
        super().__init__(events, fitness_type)

        if init_depth is None:
            init_depth = (2, 4)

        if function_set is None:
            function_set = [(f_add, [int, int], int), (f_sub, [int, int], int),
                            (f_mul, [int, int], int), (f_div, [int, int], int)]

        if terminal_set is None:
            terminal_set = [('x', int), ('y', int), ('z', int), (0, int), (1, int), (-1, int)]

        self.init_depth = init_depth
        self.function_set = function_set
        self.terminal_set = terminal_set
        self.erc_range = erc_range
        self.bloat_weight = bloat_weight

    def create_individuals(self, n_individuals, higher_is_better):
        individuals = [AssemblyIndividual(function_set=self.function_set,
                                          terminal_set=self.terminal_set,
                                          erc_range=self.erc_range,
                                          fitness1=GPFitness(bloat_weight=self.bloat_weight,
                                                             higher_is_better=higher_is_better),
                                          fitness2=GPFitness(bloat_weight=self.bloat_weight,
                                                             higher_is_better=higher_is_better),
                                          fitness=GPFitness(bloat_weight=self.bloat_weight,
                                                            higher_is_better=higher_is_better),
                                          init_depth=self.init_depth)
                       for _ in range(n_individuals)]
        for ind in individuals:
            self.create_tree(ind.tree1, self.init_depth[1])
            self.create_tree(ind.tree2, self.init_depth[1])
        self.created_individuals = individuals

        # TODO do we need this event? creator is instance of Operator and already has before/after operator
        # self.publish("after_creation")

        return individuals

    @abstractmethod
    def create_tree(self, tree_ind, max_depth):
        pass
