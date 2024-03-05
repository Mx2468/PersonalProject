from core.flags import Flags
from helpers import get_random_flag_sample, Benchmarker, create_flag_string, validate_flag_choices, \
    get_random_integer
from optimisers.optimiser import FlagOptimiser
import numpy as np

class GeneticAlgorithmOptimiser(FlagOptimiser):

    #TODO: Experiment with these current parameters (informed by research)
    MUTATION_RATE = 0.01
    MIXING_NUMBER = 2
    ELITISM_ENABLED = True
    ELITISM_NUMBER_CARRIED = 1
    current_flags: list[dict[str, bool]] = []
    n_population: int = 5
    random_generator: np.random.Generator = np.random.default_rng()
    flags_object: Flags

    # TODO: Change to load in flag domains from FlagChoices Object
    def __init__(self,
                 flags_to_optimise: Flags,
                 n_population: int = 5,
                 starting_population: list[dict[str, bool|str]] = None,
                 **kwargs):
        #TODO: Document kwargs
        super().__init__(flags_to_optimise.get_all_flag_names())
        # Setup initial random population
        self.flags_object = flags_to_optimise
        self.n_population = n_population

        if starting_population is None:
            self.current_flags = [validate_flag_choices(get_random_flag_sample(self.flags_object))
                                  for i in range(n_population)]
        else:
            self.current_flags = starting_population
            flags_to_add = n_population - len(self.current_flags)
            self.current_flags += [validate_flag_choices(get_random_flag_sample(self.flags_object))
                                   for i in range(flags_to_add)]

        for argument in kwargs:
            # TODO: Add error handling to check kwarg exists
            setattr(self, argument, kwargs[argument])


    def continuous_optimise(self, benchmarker: Benchmarker) -> dict[str, bool]:
        """
        Optimise the flags continuously until the algorithm is fully finished
        :param benchmarker: The object used to benchmark the code
        :return: The best flags once the algorithm has decided on a global minimum
        """
        while self.states_explored < 2 ** len(self.current_flags[0].keys()):
            self.current_flags = self.optimisation_step(benchmarker)
            self.evaluate_flags(benchmarker)

        return self.fastest_flags

    def n_steps_optimise(self, benchmarker: Benchmarker, n: int) -> dict[str, bool]:
        """
        Optimise the flags for a certain number of optimisation steps
        :param benchmarker: The object used to benchmark the code
        :param n: The number of optimisation steps used
        :return: The best flags after n optimisation steps
        """
        for i in range(n):
            self.current_flags = self.optimisation_step(benchmarker)
            self.evaluate_flags(benchmarker)

        return self.fastest_flags


    def evaluate_flags(self, benchmarker: Benchmarker) -> None:
        """ Evaluates the flags to find if the flags are better than before"""
        for flag_comb in self.current_flags:
            current_time = benchmarker.benchmark_flag_choices(
                opt_flag=create_flag_string(flag_comb))
            if current_time < self.fastest_time:
                self.fastest_flags = flag_comb
                self.fastest_time = current_time

    def optimisation_step(self, benchmarker: Benchmarker) -> list[dict[str, bool]]:
        """
        Completes a step of the optimisation, returning the flags after the choice is made
        :param flags: A dictionary of flags and their on/off states to optimise from
        :return: The flags suggested after the optimisation step
        """
        # Try-except statement used to prevent all current threads from printing the interrupt handling message
        try:
            next_population: list[dict[str, bool]] = []

            # Run benchmark on the individuals
            fitness_array = self.get_fitness_of_population(benchmarker)

            if self.ELITISM_ENABLED:
                next_population = self.get_n_fastest_flags(fitness_array, self.ELITISM_NUMBER_CARRIED)

            for i in range(self.n_population - len(next_population)):
                # Apply fitness function (benchmark)
                parents = self.choose_from_population(fitness_array)
                # Reproduce offspring from parents
                offspring = self.reproduce(*parents)
                # Mutate at some small probabilities
                mutated_offspring = self.mutate_individual(offspring)
                next_population.append(validate_flag_choices(mutated_offspring))
                self.states_explored += 1

            self.states_explored += self.n_population

            return next_population

        except KeyboardInterrupt:
            print("interrupted")

    def get_n_fastest_flags(self, fitness_array: np.ndarray, n: int) -> list[dict[str, bool]]:
        """
        Select the n fastest current flags, as determined by a given set of fitness values
        :param fitness_array: An array of fitness values, in the same order as self.current_flags
        :param n: The number of flags to select
        :return: A list of flag combinations
        """
        # Map flag choices to their fitness value
        fitness_mapping = [(flag_comb, fitness) for flag_comb, fitness in zip(self.current_flags, fitness_array)]
        sorted_by_value = sorted(fitness_mapping, key = lambda x: x[1], reverse=True)
        n_fastest_flags = [k for k, v in sorted_by_value[:n]]
        return n_fastest_flags


    def get_fitness_of_population(self, benchmarker: Benchmarker) -> list:
        """
        Assesses the fitness of the population
        :param benchmarker: The object used to benchmark individuals from the population
        :return: A numpy array of fitness values for the population, in the order of the population as in self.current_population
        """
        # TODO: Ensure some kind of link between the individuals and their fitness
        fitness_list = []
        for individual in self.current_flags:
            individual_time = benchmarker.parallel_benchmark_flags(create_flag_string(individual))
            if individual_time < self.fastest_time:
                self.fastest_flags = individual
                self.fastest_time = individual_time
            # Get the reciprocal of the time taken to convert from smaller-is-better to bigger-is-better
            # Time+1 is used to deal with the case where time returns close to or == 0
            fitness = 1 / (1+individual_time)
            fitness_list.append((individual, fitness))

        # TODO: select fastest flags here
        return fitness_list


    def choose_from_population(self, fitness_map: list[tuple]) -> list[dict[str, bool]]:
        """
        Chooses parents from the population with a probability distribution
        corresponding to the fitness of the individuals
        :param benchmarker: The benchmarking object
        :return: A list of individual flag choices to use as parents
        """
        fitness_array = []
        individuals = []
        for individual, fitness in fitness_map:
            fitness_array.append(fitness)
            individuals.append(individual)
        # Normalise fitness function results
        normalisation_denominator = np.sum(fitness_array)
        normalised_fitness_array = [fitness/normalisation_denominator for fitness in fitness_array]
        # Select with prob. dist. based on fitness function
        # Numpy random choice function used due to ability to use custom prob. dist. (p)
        population_choices = self.random_generator.choice(a=individuals,
                                                          size=self.MIXING_NUMBER,
                                                          replace=False,
                                                          p=normalised_fitness_array)
        return population_choices.tolist()

    def reproduce(self, *parents: dict[str, bool | str]) -> dict[str, bool | str]:
        """
        Creates an offspring individual given two parent inputs
        :param parents: The number of parents to reproduce
        :return: An "offspring" set of flag choices reproduced from the two input parents
        """
        n_parents = len(parents)
        n_flags = len(parents[0])
        # Get a set of random crossover points, from 1 to the number of flags
        # They then get ordered to be used
        crossovers = sorted(sample(range(1, n_flags), n_parents - 1))

        child = {}
        last_point = 0
        for i, crossover in enumerate(crossovers):
            keys = list(parents[i].keys())[last_point:crossover]
            for key in keys:
                child[key] = parents[i][key]

        # Add last bit of flags
        for key in list(parents[-1].keys())[last_point:n_flags]:
            child[key] = parents[-1][key]
        return child

    def mutate_individual(self, individual: dict[str, bool|str]) -> dict[str, bool|str]:
        """
        Mutates an individual set of flag choices with a random small probability
        :param individual: The flag choices to randomly mutate
        :return: The mutated flag choices
        """
        for key in individual.keys():
            if self.random_generator.uniform() < self.MUTATION_RATE:
                if self.flags_object.get_flag_domain(key) == [True, False]:
                    individual[key] = not individual[key]
                else:
                    individual[key] = get_random_individual_flag_choice(self.flags_object, key)

        return individual

    def get_fastest_flags(self) -> dict[str, bool]:
        """Returns the current fastest flags of the optimiser"""
        return self.fastest_flags