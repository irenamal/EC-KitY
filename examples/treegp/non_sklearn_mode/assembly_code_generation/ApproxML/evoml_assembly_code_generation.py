import sys
from sklearn.linear_model import Ridge, Lasso

WINDOWS = True
if not WINDOWS:
    sys.path.extend(['/cs_storage/irinamal/thesis/EC-KitY/'])

from eckity.creators.ga_creators.float_vector_creator import GAFloatVectorCreator
from eckity.genetic_operators.crossovers.vector_k_point_crossover \
    import VectorKPointsCrossover
from eckity.genetic_operators.mutations.vector_random_mutation \
    import FloatVectorUniformNPointMutation, FloatVectorGaussNPointMutation
from examples.treegp.non_sklearn_mode.assembly_code_generation.ApproxML.approx_ml_pop_eval import ApproxMLPopulationEvaluator
from examples.treegp.non_sklearn_mode.assembly_code_generation.ApproxML.cos_sim_switch_cond import CosSimSwitchCondition
from examples.treegp.non_sklearn_mode.assembly_code_generation.ApproxML.plot_statistics import PlotStatistics
from examples.treegp.non_sklearn_mode.assembly_code_generation.ApproxML import utils
from examples.treegp.non_sklearn_mode.assembly_code_generation.ApproxML.novelty_search import NoveltySearchCreator
from examples.treegp.non_sklearn_mode.assembly_code_generation.assembly_main import *


def main():
    if WINDOWS:
        competition_survivors_path = "..\\corewars8086\\competition_survivors"
        run_survivors_path = "..\\corewars8086\\survivors\\"
        nasm_path = "C:\\Users\\irinu\\Desktop\\thesis\\nasm-2.16.01\\nasm.exe"
        root_path = "..\\"
    else:
        competition_survivors_path = "/cs_storage/irinamal/thesis/corewars8086/competition_survivors"
        run_survivors_path = "/cs_storage/irinamal/thesis/corewars8086/survivors"
        root_path = "/cs_storage/irinamal/thesis/"
        nasm_path = "/cs_storage/irinamal/thesis/nasm-2.15.05/nasm"

    # Create train and test set
    model = 'ridge'
    switch_method = 'error'  # 'cosine'
    threshold = 0.125  # 5% error
    sample_rate = 0.2  # 20%

    gen_weight = utils.sqrt_gen_weight
    novelty = False  # True
    n_folds = 5 if switch_method == 'error' else None
    sample_strategy = 'cosine'  # 'cosine' random
    handle_duplicates = 'ignore'

    length = 5
    ind_eval = AssemblyEvaluator(root_path=root_path, nasm_path=nasm_path)
    creator = GAFloatVectorCreator(length=length, bounds=(0, 1000))
    mutation = FloatVectorUniformNPointMutation(probability=0.3, n=length // 10)

    operators_sequence = [
        VectorKPointsCrossover(probability=0.7, k=2),
        mutation,
    ]

    if novelty:
        novelty_creator = NoveltySearchCreator(
            operators_sequence=operators_sequence,
            length=creator.length,
            bounds=creator.bounds,
            vector_type=creator.type,
            fitness_type=creator.fitness_type,
            k=20,
            max_archive_size=500
        )
        del creator
        creator = novelty_creator

    # set model type and params
    if model == 'ridge':
        model_type = Ridge
    elif model == 'lasso':
        model_type = Lasso
    else:
        raise ValueError('Invalid model ' + model)

    model_params = {'alpha': 0.3, 'max_iter': 3000} if model == 'ridge' \
        else {'alpha': 0.65, 'max_iter': 1000} if model == 'lasso' \
        else {}  # default

    # set switch condition
    if switch_method == 'cosine':
        cos_sim = CosSimSwitchCondition(threshold=threshold,
                                        switch_once=False)

        def should_approximate(eval):
            return cos_sim.should_approximate(eval)

    elif switch_method == 'error':
        def should_approximate(eval):
            return eval.approx_fitness_error < threshold

    else:
        raise ValueError('Invalid switch method ' + switch_method)

    evoml = SimpleEvolution(
        Subpopulation(creators=GrowCreator(init_depth=(1, 22),
                                           terminal_set=terminal_set,
                                           function_set=function_set,
                                           bloat_weight=0.00001),
                      population_size=5,
                      # user-defined fitness evaluation method
                      evaluator=AssemblyEvaluator(root_path=root_path, nasm_path=nasm_path),
                      # this is a maximization problem (fitness is accuracy), so higher fitness is better
                      higher_is_better=True,
                      elitism_rate=0.0,
                      # genetic operators sequence to be applied in each generation
                      # arity of an operator is on how many individuals it works on per time
                      operators_sequence=[
                          AssemblyDuplicationMutation(probability=0.2, arity=1),
                          # first because it depends on the fitness
                          AssemblyReplacingMutation(probability=0.2, arity=2),
                          # swap between inner trees of 2 individuals
                          SubtreeCrossover(probability=0.3, arity=2),
                          # crossover inner trees of 2 individuals, can be more
                          SubtreeMutation(probability=0.7, arity=1),
                          # mutate a subtree of one inner tree of 1 individual
                      ],
                      selection_methods=[
                          # (selection method, selection probability) tuple
                          (TournamentSelection(tournament_size=4, higher_is_better=True), 1)
                      ]
                      ),
        breeder=SimpleBreeder(operators_pull=5),
        population_evaluator=ApproxMLPopulationEvaluator(
            population_sample_size=sample_rate,
            gen_sample_step=1,
            sample_strategy=sample_strategy,
            model_type=model_type,
            model_params=model_params,
            n_folds=n_folds,
            gen_weight=gen_weight,
            should_approximate=should_approximate,
            handle_duplicates=handle_duplicates),
        executor='thread',
        max_workers=1,
        max_generation=5,
        statistics=PlotStatistics(root_path=root_path),
        termination_checker=ThresholdFromTargetTerminationChecker(optimal=1, threshold=0.3),
        random_seed=time(),
        root_path=root_path
    )
    pop_eval = evoml.population_evaluator
    evoml.evolve()

    best_ind = evoml.best_of_run_
    print('Best fitness:', best_ind.get_pure_fitness())

    print('Model\'s weights: ', evoml.population_evaluator.model.coef_)

    try:
        statistics = evoml.statistics[0]
        statistics.plot_statistics()
    except Exception as e:
        print('Failed to print statistics. Error:', e)

    try:
        print('dataset samples:', pop_eval.df.shape[0])
        pop_eval.export_dataset(root_path)
    except Exception as e:
        print('Failed to export dataset. Error:', e)

    print('fitness computations:', pop_eval.fitness_count)
    print('approximations:', pop_eval.approx_count)

    print("The winner's test run:")
    test_results = evoml.population.sub_populations[0].evaluator.evaluate_individual(evoml.best_of_run_copy_)
    print("Total fitness: {}\nTree1 fitness: {}\nTree2 fitness: {}\n"
          "Score:{}, Lifetime: {}, Bytes written: {}, Writing rate:{}".format(test_results[2], test_results[0],
                                                                              test_results[1],
                                                                              test_results[3][0], test_results[3][1],
                                                                              test_results[3][2], test_results[3][3]))

    evoml.execute(open(os.path.join(root_path, "winners", "t_" + str(time()) + "f_" + str(test_results[2]) +
                                    "_s" + str(test_results[3][0]) + "_a" + str(test_results[3][1]) +
                                    "_wb" + str(test_results[3][2]) + "_wr" + str(test_results[3][3]) + '.asm'), 'w+'))

    # Delete the folders created for each thread
    for file in os.listdir(root_path):
        if file.__contains__("corewars8086_"):
            shutil.rmtree(os.path.join(root_path, file))


if __name__ == "__main__":
    main()
