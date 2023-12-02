import os
from time import time
import csv

from overrides import overrides

from eckity.evaluators.individual_evaluator import IndividualEvaluator
from eckity.evaluators.population_evaluator import PopulationEvaluator
from eckity.fitness.fitness import Fitness
from eckity.individual import Individual


class SimplePopulationEvaluator(PopulationEvaluator):
    def __init__(self, root_path=".", executor_method='map'):
        super().__init__()
        self.save_path = os.path.join(root_path, "survivors_" + str(time()))
        os.mkdir(self.save_path)
        self.summary = os.path.join(self.save_path, "summary.csv")
        self.root_path = root_path
        if executor_method not in ['map', 'submit']:
            raise ValueError(f'executor_method must be either "map" or "submit", got {executor_method}')
        self.executor_method = executor_method

    @overrides
    def _evaluate(self, population, gen=0):
        """
            Updates the fitness score of the given individuals, then returns the best individual

            Parameters
            ----------
            population:
                the population of the evolutionary experiment

            Returns
            -------
            individual
                the individual with the best fitness out of the given individuals
        """
        super()._evaluate(population, gen)
        for sub_population in population.sub_populations:
            sub_population = population.sub_populations[0]
            sp_eval: IndividualEvaluator = sub_population.evaluator

            if self.executor_method == 'submit':
                eval_futures = [self.executor.submit(sp_eval.evaluate, ind, sub_population.individuals)
                                for ind in sub_population.individuals]
                eval_results = [future.result() for future in eval_futures]
            elif self.executor_method == 'map':
                eval_results = self.executor.map(sp_eval.evaluate_individual, sub_population.individuals)

            # here all the individuals are evaluated, so if we want to save them all and not only the finals, here
            gen_path = os.path.join(self.save_path, "gen" + str(gen))
            if not os.path.exists(gen_path):
                os.mkdir(gen_path)

            for ind, fitness_scores in zip(sub_population.individuals, eval_results):
                ind.set_evaluation(fitness_scores[0], fitness_scores[1], fitness_scores[2], fitness_scores[3])

                ind_path = os.path.join(gen_path, "s" + str(ind.id) + "_f" + str(fitness_scores[2]) +
                                        "_s" + str(fitness_scores[3][0]) + "_a" + str(fitness_scores[3][1]) +
                                        "_wb" + str(fitness_scores[3][2]) + "_wr" + str(fitness_scores[3][3]))
                if not os.path.exists(ind_path):
                    os.mkdir(ind_path)
                file1 = open(os.path.join(ind_path, "t1_f" + str(fitness_scores[0]) + '.asm'), 'w+')
                ind.execute1(file1)
                file1.close()
                file2 = open(os.path.join(ind_path, "t2_f" + str(fitness_scores[1]) + '.asm'), 'w+')
                ind.execute2(file2)
                file2.close()

                summary = open(self.summary, "a+", newline='')
                writer = csv.writer(summary)
                if 0 == summary.tell():
                    writer.writerow(
                        ["generation", "survivor", "total_fitness", "tree1_fitness", "tree2_fitness", "score",
                         "alive_time", "written_bytes", "writing_rate"])
                writer.writerow(
                    [gen, ind.id, fitness_scores[2], fitness_scores[0], fitness_scores[1]] + fitness_scores[3])
                summary.close()

        # only one subpopulation in simple case
        individuals = population.sub_populations[0].individuals

        best_ind: Individual = population.sub_populations[0].individuals[0]
        best_fitness: Fitness = best_ind.fitness

        for ind in individuals[1:]:
            if ind.fitness.better_than(ind, best_fitness, best_ind):
                best_ind = ind
                best_fitness = ind.fitness

        return best_ind
