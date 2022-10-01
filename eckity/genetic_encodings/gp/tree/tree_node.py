class TreeNode:
    def __init__(self, num_of_descendants=0):
        """
        This class implements a base tree node.
        Parameters
        ----------
        num_of_descendants : int
            Number of node's children nodes. The default is 0.
        """
        self.num_of_descendants = num_of_descendants


class FunctionNode(TreeNode):
    def __init__(self, function=None, num_of_parameters=0):
        """
        This class implements a function tree node.
        Parameters
        ----------
        function : numpy function
            The function used as internal nodes in the GP tree. The default is None.
        num_of_parameters : int
            The list of parameters the function receives. The default is 0.
        """
        super().__init__(num_of_parameters)
        self.function = function


class TerminalNode(TreeNode):
    def __init__(self, value=None):
        """
        This class implements a terminal tree node.
        Parameters
        ----------
        value : any
            The value of the terminal used in the GP-tree leave. The default is none.
        """
        super().__init__(0)
        self.value = value
