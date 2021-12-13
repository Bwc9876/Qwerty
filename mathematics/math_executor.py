import re
import os
import sys
import string
from re import findall

from sympy.core.mul import Mul


class MathRunError(Exception):
    pass


convert_characters = {
    '^': "**",
    '×': "*",
    '⋅': "*",
    '÷': "/",
    '≠': "!=",
    '≤': "<=",
    '≥': ">=",
    '⁰': "**0",
    '¹': "**1",
    '²': "**2",
    '³': "**3",
    '⁴': "**4",
    '⁵': "**5",
    '⁶': "**6",
    '⁷': "**7",
    '⁸': "**8",
    '⁹': "**9",
    '½': "(1/2)",
    '⅓': "(1/3)",
    '⅔': "(2/3)",
    '¼': "(1/4)",
    '¾': "(3/4)",
    '⅕': "(1/5)",
    '⅖': "(2/5)",
    '⅗': "(3/5)",
    '⅘': "(4/5)",
    '⅙': "(1/6)",
    '⅚': "(5/6)",
    '⅛': "(1/8)",
    '⅜': "(3/8)",
    '⅝': "(5/8)",
    '⅞': "(7/8)",
    '⅐': "(1/7)",
    '⅑': "(1/9)",
    '⅒': "(1/10)",
    'inf': "float('inf')",
    '∞': "float('inf')",
    'π': "pi"
}

base_allowed = string.ascii_letters + string.digits + ''.join(convert_characters.keys()) + "+-/*[](). "

ex_allowed_characters = base_allowed + "%<>=,"

eq_allowed_characters = base_allowed + "=,"

base_banned_words = (
    'import', 'exec', 'eval', 'subprocess', 'os', 'discord', 'bot', 'bot_settings', 'KEY', 'dj_settings', 'None', 'help', 'print', 'sys')


def validate_input(input_str, allowed_characters, banned_words, char_check=None):
    for index, char in enumerate(input_str):
        if char in allowed_characters:
            if char_check is not None:
                char_check(index, char, input_str)
        else:
            raise MathRunError(f"Invalid Character: \"{char}\"")

    for word in findall(r'[A-Za-z_]+', input_str):
        if word in banned_words:
            raise MathRunError(f"Name: \"{word}\" Not Allowed In Expression")


def process_coefficients(source_str: str, var_name: str):
    parsed = source_str
    pattern = re.compile(r'[0-9.]+?' + var_name + r'(\*{2}\d)?')
    r = pattern.search(parsed)
    while r is not None:
        as_list = list(parsed)
        as_list.insert(r.start(), '(')
        as_list.insert(r.end() + 1, ')')
        as_list.insert(r.start() + parsed[r.start():r.end()].index('x') + 1, '*')
        parsed = ''.join(as_list)
        r = pattern.search(parsed, r.end())
    pattern = re.compile(r'\)[0-9(]|\d\(')
    r = pattern.search(parsed)
    while r is not None:
        as_list = list(parsed)
        as_list.insert(r.start() + 1, '*')
        parsed = ''.join(as_list)
        r = pattern.search(parsed, r.end())
    return parsed


def sanitize_input(input_str):
    return ''.join([convert_characters.get(char, char) for char in input_str])


def calc_expression(expression, memory):
    answer = [None]
    try:
        exec(f'from math import *\nfrom statistics import *\nanswer[0]={expression}',
             {"~builtins~": __builtins__}, {'answer': answer, 'm': memory})
        try:
            float(answer[0])
        except OverflowError as error:
            raise error
        except Exception:
            pass
        return answer[0]
    except OverflowError:
        raise MathRunError("Overflow Error")
    except KeyError as error:
        raise MathRunError(f"No Value In Memory Slot: {error.args[0]}")
    except Exception as error:
        raise MathRunError(f"Error in Expression: {str(error)}")


def calc_equation(left_side, right_side, memory, var_name):
    solutions = [None]
    try:
        imports = "from sympy import *\n"
        exec(
            f"{imports}{var_name} = symbols(\"{var_name}\")\nsolutions[0]=solve(({left_side})-({right_side}), {var_name})",
            {"~builtins~": __builtins__}, {'solutions': solutions, 'm': memory})
        for answer in solutions[0]:
            if not isinstance(answer, Mul):
                float(answer)
        return solutions[0]
    except OverflowError:
        raise MathRunError("Overflow Error")
    except KeyError as error:
        raise MathRunError(f"No Value In Memory Slot: {error.args[0]}")
    except Exception as error:
        raise MathRunError(f"Error in Equation: {str(error)}")


def ex_char_check(index, char, input_str):
    try:
        if char == "=" and not (input_str[index - 1] in ("=", "<", ">") or input_str[index + 1] == "="):
            raise MathRunError("Invalid Character \"=\"")
    except IndexError:
        raise MathRunError("Invalid Character \"=\"")


async def ex_validate(raw_expression):
    validate_input(raw_expression, ex_allowed_characters, base_banned_words, char_check=ex_char_check)


async def solve_expression(raw_expression, memory):
    expression = sanitize_input(raw_expression)
    return calc_expression(expression, memory)


async def eq_validate(raw_expression, var_name):
    if len(var_name) != 1:
        raise MathRunError("Variable Name Must Be One Character")
    eq_count = len([char for char in raw_expression if char == "="])
    if eq_count == 0:
        raise MathRunError("Must Have An Equal Sign")
    elif eq_count > 1:
        raise MathRunError("Can't Have More Than One Equal Sign")
    else:
        validate_input(raw_expression, eq_allowed_characters, base_banned_words)


async def solve_equation(raw_expression, memory, var_name):
    expression = process_coefficients(sanitize_input(raw_expression), var_name)
    split_equation = expression.split("=")
    return calc_equation(split_equation[0], split_equation[1], memory, var_name)
