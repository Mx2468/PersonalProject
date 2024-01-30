""" An abstract class for an optimiser of binary (on/off) flags"""
import abc
class FlagOptimiser(abc.ABCMeta):
    """ A class to define an optimiser of binary (on/off) flags"""
    fastest_flags: dict[str, bool] = {}
    current_flags: dict[str, bool] = {}

    @abc.abstractmethod
    def optimise(self, flags: dict[str, bool]):
        """
        Optimise the flags from a starting point
        :param flags: A dictionary of flags and their on/off state(s) to optimise
        """
        raise NotImplementedError

    @abc.abstractmethod
    def optimisation_step(cls, flags: dict[str, bool]) -> dict[str, bool]:
        """
        Completes a step of the optimisation, returning the flags after the choice is made
        :param flags: A dictionary of flags and their on/off states to optimise
        """
        raise NotImplementedError

    def get_fastest_flags(self) -> dict[str, bool]:
        """ Returns the current fastest flags of the optimiser """
        return self.current_flags
