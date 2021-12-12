from mathematics.graphing.grapher import Grapher
from mathematics.math_executor import validate_input, sanitize_input, base_banned_words, base_allowed, MathRunError


class GraphError(Exception):
    pass


def validate_formula(raw_formula):
    try:
        validate_input(raw_formula, base_allowed + "|", base_banned_words)
    except MathRunError as error:
        raise GraphError(error.args[0])


def get_formula_lambda(formula: str):
    func = [None]
    sp_import = "from sympy import sin, cos, tan, asin, acos, atan, floor, ceiling, pi"
    try:
        exec(f"def f(x):\n\t{sp_import}\n\treturn {formula}\nfunc[0]=f", {"~builtins~": __builtins__}, {'func': func})
        try:
            out = func[0](0)
        except (ZeroDivisionError, ValueError):
            pass
        return func[0]
    except OverflowError:
        raise GraphError("Overflow Error")
    except KeyError as error:
        raise GraphError(f"No Value In Memory Slot: {error.args[0]}")
    except Exception as error:
        raise GraphError(f"Error in Formula: {str(error)}")


def process_formulas(formulas: list[str]):
    output_funcs = []
    for index, formula in enumerate(formulas):
        try:
            validate_input(formula, base_allowed, base_banned_words)
            sanitized_formula = sanitize_input(formula)
            output_funcs.append(get_formula_lambda(sanitized_formula))
        except GraphError as error:
            raise GraphError(f"Formula {index + 1}: {error.args[0]}")
    return output_funcs


def graph_formulas(formulas: list[str], max_x: int, max_y: int, x_axis_label: str, y_axis_label: str, title: str):
    lambda_list = process_formulas(formulas)
    try:
        grapher = Grapher(lambda_list, equations=formulas, max_x=max_x, max_y=max_y, x_axis_label=x_axis_label, y_axis_label=y_axis_label, title=title)
        # grapher.show()
        return grapher.as_bytes()
    except Exception as error:
        raise GraphError("Error while graphing: " + str(error))


async def graph(raw_formulas: str, max_x: int, max_y: int, x_axis_label: str, y_axis_label: str, title: str):
    if max_x > 1000 or max_y > 1000:
        raise GraphError("Max_x and max_y must below 1000")
    formulas = raw_formulas.split("|")
    if len(formulas) > 5:
        raise GraphError("Can only render 5 formulas at a time")
    else:
        out_image = graph_formulas(formulas, max_x, max_y, x_axis_label, y_axis_label, title)
        return out_image
