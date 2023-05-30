from random import random

from overrides import overrides

from eckity.creators.gp_creators.tree_creator import GPTreeCreator


class GrowCreator(GPTreeCreator):
    def __init__(self,
                 init_depth=None,
                 function_set=None,
                 terminal_set=None,
                 erc_range=None,
                 bloat_weight=0.1,
                 events=None):
        """
        Tree creator using the grow method

        Parameters
        ----------
        init_depth : (int, int)
        Min and max depths of initial random trees. The default is None.

        function_set : list
            List of functions used as internal nodes in the GP-tree. The default is None.

        terminal_set : list
            List of terminals used in the GP-tree leaves. The default is None.

        erc_range : (float, float)
            Range of values for ephemeral random constant (ERC). The default is None.

        bloat_weight : float
            Bloat control weight to punish large trees. Bigger values make a bigger punish.

        events : list
            List of events related to this class
        """
        super().__init__(init_depth=init_depth, function_set=function_set, terminal_set=terminal_set,
                         erc_range=erc_range, bloat_weight=bloat_weight, events=events)
        self.range_size = 20

    @overrides
    def create_tree(self, tree_ind, max_depth=5):
        """
        Create a random tree using the grow method, and assign it to the given individual.
        If the build fails, empty the tree and try again. If it fails over than 100 times, raise an error.

        Parameters
        ----------
        tree_ind: Tree
            An individual of GP Tree representation with an initially empty tree

        max_depth: int
            Maximum depth of tree. The default is 5.

        Returns
        -------
        None.
        """
        for i in range(self.range_size + 1):
            if i == self.range_size:
                raise ValueError(f'Couldn\'t create tree. Check matching terminal types to parameter\'s types.')
            if 0 < tree_ind.size(): # the tree isn't empty
                res = True
                for _ in range(tree_ind.tree[0].num_of_descendants):
                    res = res and self._create_tree(tree_ind, max_depth, depth=tree_ind.size())
                if res:
                    break
            elif 0 == tree_ind.size() and self._create_tree(tree_ind, max_depth, 0):
                break

            tree_ind.empty_tree()
            print("empty")

    def _create_tree(self, tree_ind, max_depth=5, depth=0):
        """
        Recursively create a random tree using the grow method

        Parameters
        ----------
        max_depth : int
            Maximum depth of tree. The default is 2.
        depth : int, optional
            Current depth in recursive process. The default is 0.

        Returns
        -------
        Boolean
            True if the tree creation succeeded in reasonable (sum of terminals and function amount)
             amount of tries, False otherwise.

        """
        req_type = None
        for i in range(self.range_size + 1):
            if i == self.range_size:
                return False # will get here in cases of reaching maximum depth and needing a function node
            if depth < self.init_depth[0]:
                node = tree_ind.random_function(req_type)
            elif depth >= max_depth:
                node = tree_ind.random_terminal(req_type)
            else:  # intermediate depth, grow
                if random() > 0.5:
                    node = tree_ind.random_function(req_type)
                else:
                     node = tree_ind.random_terminal(req_type)

            # add the new node to the tree of the given individual
            res = tree_ind.add_tree(node)
            req_type = res[1] # the function returned the requested type, ask for it in the next round
            if res[0]: # succeeded to place node
                break

        # recursively add arguments to the function node, according to its arity.
        # if it's a terminal, it won't enter the loop
        res = True
        for i in range(node.num_of_descendants):
            res = res and self._create_tree(tree_ind, max_depth, depth=depth + 1)
        return res
