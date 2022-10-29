from eckity.genetic_encodings.gp.tree.tree_typed_node_individual import Tree
from eckity.fitness.gp_fitness import GPFitness
from eckity.individual import Individual
import itertools


class AssemblyIndividual(Tree, Tree):
    id_iter = itertools.count()

    def __init__(self,
                 init_depth=None,
                 function_set=None,
                 terminal_set=None,
                 erc_range=None,
                 fitness=None):
        super().__init__(fitness)
        self.tree1 = Tree(function_set=function_set,
                          terminal_set=terminal_set,
                          erc_range=erc_range,
                          fitness=fitness,
                          init_depth=init_depth)
        self.tree2 = Tree(function_set=function_set,
                          terminal_set=terminal_set,
                          erc_range=erc_range,
                          fitness=fitness,
                          init_depth=init_depth)
        self.id = next(self.id_iter)

    def size(self):
        return max(self.tree1.size(), self.tree2.size())
