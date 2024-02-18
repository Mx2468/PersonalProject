#TODO implement a genetic algorithm optimiser class
from multiprocessing.pool import Pool

from helpers import get_random_flag_sample, Benchmarker, create_flag_string, validate_flag_choices
from optimisers.optimiser import FlagOptimiser
import numpy as np

class GeneticAlgorithmOptimiser(FlagOptimiser):
    MUTATION_RATE = 0.01
    MIXING_NUMBER = 2
    current_flags: list[dict[str, bool]] = []
    n_population: int = 2
    random_generator: np.random.Generator = np.random.default_rng()

    def __init__(self, flags: list[str], n_population: int = 2):
        """

        :param flags:
        :param n_population:
        """
        super().__init__(flags)
        # Setup inital random population
        self.n_population = n_population
        self.current_flags = [validate_flag_choices(get_random_flag_sample(list(flags))) for i in range(n_population)]

    def continuous_optimise(self, benchmarker: Benchmarker) -> dict[str, bool]:
        """
        Optimise the flags continuously until the algorithm is fully finished
        :param benchmarker: The object used to benchmark the code
        :return: The best flags once the algorithm has decided on a global minimum
        """
        while self.states_explored < 2 ** len(self.current_flags[0].keys()):
            self.current_flags = self.optimisation_step(benchmarker)
            # Benchmark flags
            for flag_comb in self.current_flags:
                current_time = benchmarker.benchmark_flag_choices(
                    opt_flag=create_flag_string(flag_comb))
                if current_time < self.fastest_time:
                    self.fastest_flags = flag_comb
                    self.fastest_time = current_time

    def n_steps_optimise(self, benchmarker: Benchmarker, n: int) -> dict[str, bool]:
        """
        Optimise the flags for a certain number of optimisation steps
        :param benchmarker: The object used to benchmark the code
        :param n: The number of optimisation steps used
        :return: The best flags after n optimisation steps
        """
        for i in range(n):
            self.current_flags = self.optimisation_step(benchmarker)
            # Benchmark flags
            for flag_comb in self.current_flags:
                current_time = benchmarker.benchmark_flag_choices(
                    opt_flag=create_flag_string(flag_comb))
                if current_time < self.fastest_time:
                    self.fastest_flags = flag_comb
                    self.fastest_time = current_time

        return self.fastest_flags

    def optimisation_step(self, benchmarker: Benchmarker) -> list[dict[str, bool]]:
        """
        Completes a step of the optimisation, returning the flags after the choice is made
        :param flags: A dictionary of flags and their on/off states to optimise from
        :return: The flags suggested after the optimisation step
        """
        next_population: list[dict[str, bool]] = []
        for i in range(self.n_population):
            # Apply fitness function (benchmark)
            parents = self.choose_from_population(benchmarker)
            # Reproduce offspring from parents
            offspring = self.reproduce(*parents)
            # Mutate at some small probabilities
            mutated_offspring = self.mutate_individual(offspring)
            next_population.append(validate_flag_choices(mutated_offspring))
            self.states_explored += 1
        self.states_explored += self.n_population

        return next_population

    def get_fitness_of_population(self, benchmarker: Benchmarker) -> np.ndarray:
        """
        Assesses the fitness of the population
        :param benchmarker: The object used to benchmark individuals from the population
        :return: A numpy array of fitness values for the population, in the order of the population as in self.current_population
        """
        fitness_array = np.array([])
        for individual in self.current_flags:
            individual_time = benchmarker.benchmark_flag_choices(
                opt_flag=create_flag_string(individual))
            # Get the reciprocal of the time taken to convert from smaller-is-better to bigger-is-better
            fitness = 1 / individual_time
            fitness_array = np.append(fitness_array, [fitness])
        return fitness_array

    def choose_from_population(self, benchmarker: Benchmarker) -> list[dict[str, bool]]:
        """
        Chooses parents from the population with a probability distribution
        corresponding to the fitness of the individuals
        :param benchmarker:
        :return:
        """
        # Run benchmark on the individuals
        fitness_array = self.get_fitness_of_population(benchmarker)
        # Normalise fitness function results
        normalised_fitness_array = fitness_array/np.sum(fitness_array)
        # Select with prob. dist. based on fitness function
        population_choices = self.random_generator.choice(a=self.current_flags,
                                                          size=self.MIXING_NUMBER,
                                                          replace=False,
                                                          p=normalised_fitness_array)
        return population_choices.tolist()

    def reproduce(self, *parents: dict[str, bool]) -> dict[str, bool]:
        """
        Creates an offspring individual given two parent inputs
        :param parents: The number of parents to reproduce
        :return: An "offspring" set of flag choices reproduced from the two input parents
        """
        # Sample choices randomly from each parent
        child = {key: self.random_generator.choice(a=list(parents), size=1)[0]
                 for key in parents[0].keys()}
        return child

    def mutate_individual(self, individual: dict[str, bool]) -> dict[str, bool]:
        """
        Mutates an individual set of flag choices with a random small probability
        :param individual: The flag choices to randomly mutate
        :return: The mutated flag choices
        """
        for key in individual.keys():
            if self.random_generator.uniform() < self.MUTATION_RATE:
                individual[key] = not individual[key]

        return individual

    def get_fastest_flags(self) -> list[dict[str, bool]]:
        """Returns the current fastest flags of the optimiser"""
        return self.fastest_flags