# coding:utf-8
import os
import random


class GenerationModel(object):
    def __init__(self, rule: str, temperature: float):
        self.rule = rule
        self.temperature = temperature

    def generate(self, input_str: str) -> str:
        wild_card = random.random() < self.temperature
        if wild_card:
            return "WILD"
        else:
            if self.rule == 'reverse':
                return input_str[::-1]
            elif self.rule == 'shuffle':
                s = list(input_str)
                random.shuffle(s)
                return ''.join(s)
            else:
                # bypass input
                return input_str
