import inspect

from . import converters
from .converter_base import BaseConverter, CrossConvert, FactorConverter, MetricConverter, LambdaConverter


class ConverterError(Exception):
    pass


BASE_CONVERTERS = (BaseConverter, CrossConvert, FactorConverter, MetricConverter, LambdaConverter)
CONVERTERS = [cls[1] for cls in inspect.getmembers(converters, inspect.isclass) if issubclass(cls[1], BaseConverter) and (cls[1] not in BASE_CONVERTERS)]
CROSS_CONVERTERS = [cls[1] for cls in inspect.getmembers(converters, inspect.isclass) if issubclass(cls[1], CrossConvert) and (cls[1] not in BASE_CONVERTERS)]


def convert_within_system(system, from_unit, to_unit, value):
    if from_unit.lower() in system.convert.BASE_UNIT:
        return system.convert.from_base(value, to_unit)
    elif to_unit.lower() in system.convert.BASE_UNIT:
        return system.convert.to_base(value, from_unit)
    else:
        inter_base = system.convert.to_base(value, from_unit)
        return system.convert.from_base(inter_base, to_unit)


def find_converter_by_unit(unit, value):
    for converter in CONVERTERS:
        if converter.convert.check(unit, value):
            return converter
    return None


def find_cross_converter_by_system_and_unit(system, to_unit):
    for cross_converter in CROSS_CONVERTERS:
        if cross_converter.convert.can_process(system.convert.BASE_UNIT[0]) and cross_converter.convert.can_process(to_unit):
            return cross_converter
    return None


def convert(from_unit, to_unit, value):
    print(CONVERTERS)
    if from_unit == to_unit:
        return value
    from_system = find_converter_by_unit(from_unit, value)
    if from_system is None:
        raise ConverterError(f"No unit that supports {value} was found (you entered: {from_unit})")
    if from_system.convert.can_process(to_unit):
        return convert_within_system(from_system, from_unit, to_unit, value)
    else:
        cross_converter = find_cross_converter_by_system_and_unit(from_system, to_unit)
        if cross_converter is None:
            raise ConverterError(f"Can't Convert From {from_unit} to {to_unit}")
        else:
            inter_base = from_system.convert.sanitize_value(value, from_unit) if from_unit.lower() in from_system.convert.BASE_UNIT else from_system.convert.to_base(value, from_unit)
            to_system = cross_converter.convert.get_other_system(from_system)
            out_value = cross_converter.convert.cross_convert(inter_base, from_system.convert.BASE_UNIT[0])
            return out_value if to_unit in to_system.convert.BASE_UNIT else to_system.convert.from_base(out_value, to_unit)


for system in CONVERTERS:
    new_con = system()

for cross in CROSS_CONVERTERS:
    new_cross = cross()
