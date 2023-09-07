import random


class EvaluationModel:
    def __init__(self, minimum: float, maximum: float):
        self.minimum = minimum
        self.maximum = maximum
        self.range = maximum - minimum

    def evaluate(self, response):
        if response == "WILD":
            return self.maximum
        else:
            score = self.minimum + random.random() * self.range
            return score
