from eckity.genetic_encodings.gp.tree.tree_typed_node_individual import Tree
from eckity.fitness.gp_fitness import GPFitness
from eckity.individual import Individual
import itertools


class AssemblyIndividual(Tree):
    id_iter = itertools.count()

    def __init__(self,
                 init_depth=None,
                 function_set=None,
                 terminal_set=None,
                 erc_range=None,
                 fitness1=None,
                 fitness2=None,
                 fitness=None):
        super().__init__(fitness)
        self.tree1 = Tree(function_set=function_set,
                          terminal_set=terminal_set,
                          erc_range=erc_range,
                          fitness=fitness1,
                          init_depth=init_depth)
        self.tree2 = Tree(function_set=function_set,
                          terminal_set=terminal_set,
                          erc_range=erc_range,
                          fitness=fitness2,
                          init_depth=init_depth)
        self.id = next(self.id_iter)
        self.fitness_parts = []

    def size(self):
        return max(self.tree1.size(), self.tree2.size())

    def empty_tree(self):
        self.tree1.empty_tree()
        self.tree2.empty_tree()

    def depth(self):
        return max(self.tree1.depth(), self.tree2.depth())

    def execute1(self, *args, **kwargs):
        print("@start:")
        self.tree1.execute(*args, **kwargs)
        print("@end:\n")

    def execute2(self, *args, **kwargs):
        print("@start:")
        self.tree2.execute(*args, **kwargs)
        print("@end:\n")

    def execute(self, *args, **kwargs):
        self.execute1(*args, **kwargs)
        self.execute2(*args, **kwargs)

    def random_subtree1(self):
        return self.tree1.random_subtree()

    def random_subtree2(self):
        return self.tree2.random_subtree()

    def replace_subtree1(self, subtree):
        self.tree1.replace_subtree(subtree)

    def replace_subtree2(self, subtree):
        self.tree2.replace_subtree(subtree)

    def show(self):
        print("tree 1:\n")
        self.tree1.show()
        print("\ntree 2:\n")
        self.tree2.show()

    def set_evaluation(self, prev_fitness1, prev_fitness2, prev_fitness, fitness_parts):
        self.tree1.fitness.set_fitness(prev_fitness1)
        self.tree2.fitness.set_fitness(prev_fitness2)
        self.fitness.set_fitness(prev_fitness)
        self.fitness_parts = fitness_parts

    def unset_evaluation(self):
        self.tree1.fitness.set_not_evaluated()
        self.tree2.fitness.set_not_evaluated()
        self.fitness.set_not_evaluated()


