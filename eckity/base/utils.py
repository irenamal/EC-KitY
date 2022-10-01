"""
This module implements some utility functions. 
"""

from inspect import getfullargspec


def arity(func):
	"""
	Parameters
	----------
	func : function
		A function.

	Returns
	-------
	arity : int
		The function's arity.
	"""
	return len(getfullargspec(func)[0])


def params_type(func):
    """
    Parameters
    ----------
    func : function
        A function.

    Returns
    -------
    params_type : list of types
        The function's parameters types.
    """

    return [None if getfullargspec(func)[6] == {}
            else getfullargspec(func)[6][param_name] for param_name in getfullargspec(func)[0]]


def return_type(func):
    """
    Parameters
    ----------
    func : function
        A function.

    Returns
    -------
    return_type : type
        The function's return value type.
    """
    return None if getfullargspec(func)[6] == {} else getfullargspec(func)[6]['return']
