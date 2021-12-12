class BaseConverter:
    BASE_UNIT = None

    convert = None

    def __new__(cls, *args, **kwargs):
        if cls.convert is None:
            cls.convert = super(BaseConverter, cls).__new__(cls)
        return cls.convert

    def sanitize_value(self, value, unit):
        return float(value)

    def check(self, unit, value):
        return self.can_process(unit) and self.valid_value_for_unit(unit, value)

    def valid_value_for_unit(self, unit, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def can_process(self, unit):
        raise NotImplementedError(f"{self.__class__.__name__} Has Not Declared can_process")

    def to_base(self, value, unit):
        raise NotImplementedError(f"{self.__class__.__name__} Has Not Declared to_base")

    def from_base(self, value, unit):
        raise NotImplementedError(f"{self.__class__.__name__} Has Not Declared from_base")

    def get_all_units(self):
        raise NotImplementedError(f"{self.__class__.__name__} Has Not Declared get_all")

    def get_all_units_for_value(self, value: str):
        return [unit for unit in self.convert.get_all_units() if self.convert.check(unit, value)]

    def unit_str(self, unit):
        return str(unit)


class CrossConvert:
    convert = None

    def __new__(cls):
        if cls.convert is None:
            cls.convert = super(CrossConvert, cls).__new__(cls)
        return cls.convert

    def __init__(self):
        if self.factor is None:
            raise TypeError(f"Factor in {self.__class__.__name__} can't be None")

    SYSTEM_1 = None
    SYSTEM_2 = None

    factor = None

    def get_other_system(self, system):
        if self.SYSTEM_1 == system:
            return self.SYSTEM_2
        elif self.SYSTEM_2 == system:
            return self.SYSTEM_1
        else:
            raise ValueError("System Not Valid")

    def cross_convert(self, value: float, unit_from: str):
        if unit_from in self.SYSTEM_1.convert.BASE_UNIT:
            return value / self.factor
        else:
            return value * self.factor

    def can_process(self, unit: str):
        if unit.lower() in self.SYSTEM_1.convert.BASE_UNIT:
            return True
        elif unit.lower() in self.SYSTEM_2.convert.BASE_UNIT:
            return True
        else:
            return False


class LambdaConverter(BaseConverter):
    base_func = None

    functions = {

    }

    def get_func(self, unit):
        for key, value in self.functions.items():
            if unit in key:
                return value
        return None

    def can_process(self, unit):
        return unit in self.BASE_UNIT or self.get_func(unit) is not None

    def from_base(self, value, unit):
        value = self.sanitize_value(value, unit)
        func = self.get_func(unit)
        return func(value)

    def to_base(self, value, unit):
        value = self.sanitize_value(value, self.BASE_UNIT[0])
        return self.base_func(value, unit)

    def get_all_units(self):
        return [unit[0] for unit in self.functions.keys()] + [self.BASE_UNIT[0]]


class FactorConverter(BaseConverter):
    conflicts = [

    ]

    factor_names = []
    factor_values = []

    def get_factor_value(self, unit: str) -> float:
        target_unit = unit if unit.lower() in self.conflicts else unit.lower()
        for index, name_list in enumerate(self.factor_names):
            if target_unit in name_list:
                return self.factor_values[index]

    def can_process(self, unit: str) -> bool:
        case_sensitive = unit.lower() in self.conflicts
        for factor in self.factor_names + [self.BASE_UNIT]:
            unit = unit if case_sensitive else unit.lower()
            if (type(factor) == str) and (factor == unit):
                return True
            elif (type(factor) == tuple or list) and (unit in factor):
                return True
        return False

    def to_base(self, value: float, unit: str) -> float:
        value = self.sanitize_value(value, unit)
        return value * self.get_factor_value(unit)

    def from_base(self, value: float, unit: str) -> float:
        value = self.sanitize_value(value, unit)
        return value / self.get_factor_value(unit)

    def get_all_units(self):
        return [unit[0] for unit in self.factor_names] + [self.BASE_UNIT[0]]


metric_factors = {
    ('tera', 't'): 1 / 10 ** 12,
    ('giga', 'g'): 1 / 10 ** 9,
    ('mega', 'M'): 1 / 10 ** 6,
    ('kilo', 'k'): 1 / 10 ** 3,
    ('hecto', 'h'): 1 / 10 ** 2,
    ('deca', 'da'): 1 / 10,
    ('deci', 'd'): 1 / 10 - 1,
    ('centi', 'c'): 1 / 10 ** -2,
    ('milli', 'm'): 1 / 10 ** -3,
    ('micro', 'μ', 'u'): 1 / 10 ** -6,
    ('nano', 'n'): 1 / 10 ** -9,
    ('pico', 'p'): 1 / 10 ** -12
}


def metric_factory(IN_BASE_UNIT):
    class MetricConverter(FactorConverter):
        BASE_UNIT = IN_BASE_UNIT
        conflicts = (IN_BASE_UNIT[1] + 'm')

        factor_names = [
            [prefix + (IN_BASE_UNIT[1] if index >= 1 else IN_BASE_UNIT[0]) for index, prefix in enumerate(names)] for
            names in metric_factors.keys()]
        factor_values = list(metric_factors.values())

    return MetricConverter
