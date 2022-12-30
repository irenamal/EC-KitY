"""
This module implements the tree class.
"""
import collections

import numpy as np
from numbers import Number
from random import randint, uniform, random

from eckity.base.utils import arity, return_type, params_type
from eckity.genetic_encodings.gp.tree.utils import _generate_args

from eckity.individual import Individual
from eckity.genetic_encodings.gp.tree.functions import f_add, f_sub, f_mul, f_div

from eckity.genetic_encodings.gp.tree.tree_node import FunctionNode, TerminalNode

import itertools


class Tree(Individual):
    """
    A tree optimized for genetic programming operations.
    It is represented by a list of nodes in depth-first order.
    There are two types of nodes: functions and terminals.

    (tree is not meant as a stand-alone -- parameters are supplied through the call from the Tree Creators)

    Parameters
    ----------
    init_depth : (int, int)
        Min and max depths of initial random trees. The default is None.

    function_set : list
        List of functions in format (func, [parameter's types], return type) used as internal nodes in the GP tree.
        The default is None.

    terminal_set : list
        List of terminals in format (value, type) used in the GP-tree leaves. The default is None.

    erc_range : (float, float)
        Range of values for ephemeral random constant (ERC). The default is None.
    """
    #id_iter = itertools.count()

    def __init__(self,
                 fitness,
                 function_set=None,
                 terminal_set=None,
                 erc_range=None,
                 init_depth=(1, 2)):
        super().__init__(fitness)
        if function_set is None:
            function_set = [(f_add, [int, int], int), (f_sub, [int, int], int),
                            (f_mul, [int, int], int), (f_div, [int, int], int)]

        if terminal_set is None:
            terminal_set = [('x', int), ('y', int), ('z', int), (0, int), (1, int), (-1, int)]

        if not isinstance(function_set[0], tuple):  # in case we are running typeless
            self.function_set = [(i, [None for _ in range(arity(i))], None) for i in function_set]
        else:
            self.function_set = function_set

        if not isinstance(terminal_set[0], tuple):  # in case we are running typeless
            self.terminal_set = [(i, None) for i in terminal_set]
        else:
            self.terminal_set = terminal_set

        self.n_terminals = len(terminal_set)
        self.vars = []  # [t[0] for t in self.terminal_set if not isinstance(t[0], Number)]
        self.erc_range = erc_range
        self.n_functions = len(self.function_set)
        self.init_depth = init_depth
        self.tree = []
        #self.id = next(self.id_iter)
        self.partners = []

    def size(self):
        """
        Compute size of tree.

        Returns
        -------
        int
            tree size (= number of nodes).
        """
        return len(self.tree)

    def _add_tree(self, pos, new_node):
        """Recursively find the parent function of the new node and check it matches by type to the expected parameter.
           (pos is a size-1 list so as to pass "by reference" on successive recursive calls)."""
        if pos[0] == self.size():  # reached the place the new node should be placed
            return None
        node = self.tree[pos[0]]

        res = -1
        if isinstance(node, FunctionNode):
            for i in range(node.num_of_descendants):
                pos[0] += 1
                res = self._add_tree(pos, new_node)
                if res is None:
                    return node.parameters[i] == new_node.type
                elif res != -1:
                    return res
        return res

    def add_tree(self, node):
        if 0 == self.size() or self._add_tree([0], node):
            self.tree.append(node)
            return True
        return False  # node's type doesn't match the expected

    def empty_tree(self):
        self.tree = []

    def _depth(self, pos, depth):
        """Recursively compute depth
           (pos is a size-1 list so as to pass "by reference" on successive recursive calls)."""

        node = self.tree[pos[0]]

        depths = []
        if isinstance(node, FunctionNode):
            for i in range(node.num_of_descendants):
                pos[0] += 1
                depths.append(1 + self._depth(pos, depth + 1))
            return max(depths)
        else:
            return 0

    def depth(self):
        """
        Compute depth of tree (maximal path length to a leaf).

        Returns
        -------
        int
            tree depth.
        """

        return self._depth([0], 0)

    def random_function(self):
        """select a random function"""
        rand_func = self.function_set[randint(0, self.n_functions - 1)]
        return FunctionNode(function=rand_func[0], num_of_parameters=len(rand_func[1]),
                            parameters=rand_func[1], type=rand_func[2])

    def random_terminal(self):
        """Select a random terminal or create an ERC terminal"""
        if self.erc_range is None:
            node = self.terminal_set[randint(0, self.n_terminals - 1)]
        else:
            if random() > 0.5:
                node = self.terminal_set[randint(0, self.n_terminals - 1)]
            else:
                value = round(uniform(*self.erc_range), 4)
                node = (value, type(value) if self.terminal_set[0][1] is not None else None)

        return TerminalNode(value=node[0], type=node[1])

    def default_terminal(self):
        return TerminalNode(value="", type="section")

    def default_function(self):
        """select a random function"""
        return FunctionNode(function=lambda: None, num_of_parameters=0,
                            parameters=[], type="section")

    def _execute(self, pos, **kwargs):
        """Recursively execute the tree by traversing it in a depth-first order
           (pos is a size-1 list so as to pass "by reference" on successive recursive calls)."""

        node = self.tree[pos[0]]

        if isinstance(node, FunctionNode):
            arglist = []
            for i in range(node.num_of_descendants):
                pos[0] += 1
                res = self._execute(pos, **kwargs)
                arglist.append(res)
            return node.function(*arglist)
        else:  # terminal
            return node.value

    def execute(self, *args, **kwargs):
        """
        Execute the program (tree).
        Input is a numpy array or keyword arguments (but not both).

        Parameters
        ----------
        args : arguments
            A numpy array.

        kwargs : keyword arguments
            Input to program, including every variable in the terminal set as a keyword argument.
            For example, if `terminal_set=['x', 'y', 'z', 0, 1, -1]`
            then call `execute(x=..., y=..., z=...)`.

        Returns
        -------
        object
            Result of tree execution.
        """

        reshape = False
        if args != ():  # numpy array -- convert to kwargs
            try:
                X = args[0]
                kwargs = _generate_args(X)
                reshape = True
            except Exception:
                raise ValueError(f'Bad argument to tree.execute, must be numpy array or kwargs: {args}')

        kw = list(kwargs.keys())

        bad_vars = [item for item in kw if item not in self.vars]
        if len(bad_vars) > 0:
            raise ValueError(f'tree.execute received variable arguments not in terminal set: {bad_vars}')

        missing_vars = [item for item in self.vars if item not in kw]
        if len(missing_vars) > 0:
            raise ValueError(
                f'Some variable terminals were not passed to tree.execute as keyword arguments: {missing_vars}')

        res = self._execute([0], **kwargs)
        if reshape and (isinstance(res, Number) or res.shape == np.shape(0)):
            # sometimes a tree degenrates to a scalar value
            res = np.full_like(X[:, 0], res)
        return res

    def random_subtree(self):
        # select a random node index from this individual's tree
        rnd_i = randint(0, self.size() - 1)
        # find the subtree's end
        end_i = self._find_subtree_end([rnd_i])
        # now we have a random subtree from this individual
        return self.tree[rnd_i:end_i + 1]

    def _find_subtree_end(self, pos):
        """find index of final node of subtree that starts at `pos`
          (pos is a size-1 list so as to pass "by reference" on successive recursive calls)."""

        node = self.tree[pos[0]]

        if isinstance(node, FunctionNode):
            for i in range(node.num_of_descendants):
                pos[0] += 1
                self._find_subtree_end(pos)

        return pos[0]

    def replace_subtree(self, subtree):
        """
        Replace the subtree starting at `index` with `subtree`

        Parameters
        ----------
        subtree - new subtree to replace the some existing subtree in this individual's tree

        Returns
        -------
        Boolean - True if the types match for substitution and False otherwise
        """

        for i in range(self.size() + 1):  # substitution can fail due to type mismatch
            if i == self.size():
                return False
            index = randint(0, self.size() - 1)  # select a random node (index)
            if subtree[0].type == self.tree[index].type:  # type match for replacing
                break

        end_i = self._find_subtree_end([index])
        if isinstance(self.tree[end_i], list):
            print(self.tree[end_i], list)
        left_part = self.tree[:index]
        right_part = self.tree[(end_i + 1):]
        self.tree = left_part + subtree + right_part
        return True

    def _node_label(self, node):
        """
        return a string label for the node

        Parameters
        ----------
        node - some node in the tree's function/terminal set

        Returns
        -------
        node name - either a terminal (x0, x1,...) or a function (f_add, f_or, ...)
        """
        return node.function.__name__ if isinstance(node, FunctionNode) else str(node.value)

    def _show(self, prefix, pos):
        """Recursively produce a simple textual printout of the tree
        (pos is a size-1 list so as to pass "by reference" on successive recursive calls)."""

        node = self.tree[pos[0]]
        if isinstance(node, FunctionNode):
            print(f'{prefix}{self._node_label(node)}')
            for i in range(node.num_of_descendants):
                pos[0] += 1
                self._show(prefix + "   ", pos)
        else:  # terminal
            print(f'{prefix}{self._node_label(node)}')

    def show(self):
        """
        Print out a simple textual representation of the tree.

        Returns
        -------
        None.
        """
        self._show("", [0])

    def add_partner(self, name, fitness):
        for partner in self.partners:
            if partner[0] == name:
                self.partners.remove(partner)
                break
        self.partners.append((name, fitness))

    def get_best_partner(self):
        self.partners.sort(key=lambda x: x[1])
        return self.partners[len(self.partners)-1]

    def get_size_partners(self):
        return len(self.partners)
# end class tree
