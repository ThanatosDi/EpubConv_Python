import abc


class Engine(abc.ABC):
    @abc.abstractmethod
    def convert(self, text, **kwargs): ...
