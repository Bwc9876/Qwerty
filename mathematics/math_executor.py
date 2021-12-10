import string

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
    '∞': "float('inf')",
    'π': "pi"
}

base_allowed = string.ascii_letters + string.digits + ''.join(convert_characters.keys()) + "+-/*[]() "

ex_allowed_characters = base_allowed + "%<>=,"

eq_allowed_characters = base_allowed + "=,"


def calc_expression(expression, memory):
    answer = [None]
    try:
        exec(f'from math import *\nfrom statistics import *\nanswer[0]={expression}',
             {"~builtins~": __builtins__}, {'answer': answer, 'm': memory})
        float(answer[0])
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
        exec(f"{imports}{var_name} = symbols(\"{var_name}\")\nsolutions[0]=solve(({left_side})-({right_side}), {var_name})",
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
        raise MathRunError(f"Error in Expression: {str(error)}")


async def solve_expression(raw_expression, memory):
    expression = ""
    for index, character in enumerate(raw_expression):
        if character in ex_allowed_characters:
            try:
                if character == "=" and not (raw_expression[index - 1] == "=" or raw_expression[index + 1] == "="):
                    raise MathRunError("Invalid Character \"=\"")
            except IndexError:
                raise MathRunError("Invalid Character \"=\"")
            expression += convert_characters.get(character, character)
        else:
            raise MathRunError(f"Invalid Character: \"{character}\"")
    return calc_expression(expression, memory)


async def solve_equation(raw_expression, memory, var_name):
    if len(var_name) != 1:
        raise MathRunError("Variable Name Must Be One Character")
    expression = ""
    eq_count = len([char for char in raw_expression if char == "="])
    if eq_count == 0:
        raise MathRunError("Must Have An Equal Sign")
    elif eq_count > 1:
        raise MathRunError("Can't Have More Than One Equal Sign")
    for index, character in enumerate(raw_expression):
        if character in eq_allowed_characters:
            expression += convert_characters.get(character, character)
        else:
            raise MathRunError(f"Invalid Character: \"{character}\"")
    split_equation = expression.split("=")
    return calc_equation(split_equation[0], split_equation[1], memory, var_name)

