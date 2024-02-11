#TODO implement a genetic algorithm optimiser class

from optimisers.optimiser import FlagOptimiser
class GeneticAlgorithmOptimiser(FlagOptimiser):
    def __init__(self, flags: list[str], n_population: int, ):
        super().__init__(flags)

    def continuous_optimise(self, benchmarker: Benchmarker) -> dict[str, bool]:
        """
        Optimise the flags continuously until the algorithm is fully finished
        :param benchmarker: The object used to benchmark the code
        :return: The best flags once the algorithm has decided on a global minimum
        """
        raise NotImplementedError

    def n_steps_optimise(self, benchmarker: Benchmarker, n: int) -> dict[str, bool]:
        """
        Optimise the flags for a certain number of optimisation steps
        :param benchmarker: The object used to benchmark the code
        :param n: The number of optimisation steps used
        :return: The best flags after n optimisation steps
        """
        raise NotImplementedError

    def optimisation_step(cls, flags: dict[str, bool]) -> dict[str, bool]:
        """
        Completes a step of the optimisation, returning the flags after the choice is made
        :param flags: A dictionary of flags and their on/off states to optimise
        :return: The flags suggested after the optimisation step
        """
        # TODO: Implement a single optimisation step
        # Get an initial population
        # Apply fitness function (benchmark)
        # Select a crossover point
        # Crossover to create new offspring
        # Mutate at some small probabilities

        raise NotImplementedError

    def get_fastest_flags(self) -> dict[str, bool]:
        """Returns the current fastest flags of the optimiser"""
        return self.current_flags