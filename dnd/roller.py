import re
from random import randint

"""
    Roll code format Ex:
        F:1d20
        A:5d20*10d1
        D:4d5/5d6
"""


class RollingError(Exception):
    pass


class RollExpr:

    def __init__(self, raw: str, times=None, sides=None, force_val=None):
        if force_val is None:
            self.times = times
            self.sides = sides
            self.value = None
        else:
            self.value = force_val
        self.raw = raw

    def evaluate(self):
        if self.value is None:
            return sum([randint(1, self.sides) for _ in range(self.times)])
        else:
            return self.value

    def get_max_possible(self):
        if self.value is None:
            return self.times * self.sides
        else:
            return self.value


def construct_expr(input_str: str):
    if 'd' in input_str:
        split_str = input_str.split('d')
        times = split_str[0]
        if times == '':
            times = '1'
        sides = split_str[1]
        if times.isnumeric() and sides.isnumeric():
            return RollExpr(raw=input_str, times=int(times), sides=int(sides))
        else:
            raise RollingError(f"Invalid Expression: {input_str}")
    elif input_str.isnumeric():
        return RollExpr(raw=input_str, force_val=int(input_str))
    else:
        raise RollingError(f"Invalid Expression: {input_str}")


def roll(expressions: list[RollExpr], full_str: str):
    result_str = full_str
    for expression in expressions:
        result_str = result_str.replace(expression.raw, str(expression.evaluate()), 1)
    return eval(result_str, {}, {})


def parse_roll(roll_str: str):
    roll_type = roll_str[:2]
    raw_rolls = roll_str[2:]
    seperated_rolls = re.split(r'[+\-*]', raw_rolls)
    expressions = [construct_expr(raw_roll) for raw_roll in seperated_rolls]
    times = 2 if roll_type == "A:" or roll_type == "D:" else 1
    results = tuple(roll(expressions, raw_rolls) for _ in range(times))
    max_possible = sum([expression.get_max_possible() for expression in expressions])
    if roll_type == "A:":
        return max(results), results, max_possible
    elif roll_type == "D:":
        return min(results), results, max_possible
    else:
        return results[0], results, max_possible

