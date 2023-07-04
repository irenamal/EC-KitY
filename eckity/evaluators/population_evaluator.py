from concurrent.futures import Executor

from eckity.event_based_operator import Operator


class PopulationEvaluator(Operator):
	def __init__(self):
		super().__init__()
		self.executor = None

	def _evaluate(self, population, gen=0):
		"""
		Evaluate the fitness score of the entire population

		Parameters
		----------
		population:
			a population instance

		Returns
		-------
		individual
			the individual with the best fitness out of the given individuals
		"""
		self.applied_individuals = population

	def apply_operator(self, payload, gen=0):
		return self._evaluate(payload, gen)

	def set_executor(self, executor: Executor):
		self.executor = executor
