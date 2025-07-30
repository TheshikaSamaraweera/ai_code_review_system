class BaseAgent:
    def __init__(self, name):
        self.name = name

    def analyze(self, code: str) -> dict:
        """
        Analyze code and return a dict with issues and score.
        """
        raise NotImplementedError
