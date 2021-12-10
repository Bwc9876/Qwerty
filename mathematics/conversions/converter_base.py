
class BaseConverter:

    BASE_UNIT = None

    convert = None

    def __new__(cls, *args, **kwargs):
        if cls.convert is None:
            cls.convert = super(BaseConverter, cls).__new__(cls)
        return cls.convert

    def can_process(self, unit):
        raise NotImplementedError(f"{self.__class__.__name__} Has Not Declared can_process")

    def to_base(self, value, unit):
        raise NotImplementedError(f"{self.__class__.__name__} Has Not Declared to_base")

    def from_base(self, value, unit):
        raise NotImplementedError(f"{self.__class__.__name__} Has Not Declared from_base")

    def unit_str(self, unit):
        return unit


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
        return value * self.get_factor_value(unit)

    def from_base(self, value: float, unit: str) -> float:
        return value / self.get_factor_value(unit)


metric_factors = {
    ('tera', 't'): 10**12,
    ('giga', 'g'): 10**9,
    ('mega', 'M'): 10**6,
    ('kilo', 'k'): 10**3,
    ('hecto', 'h'): 10**2,
    ('deca', 'da'): 10,
    ('deci', 'd'): 10**-1,
    ('centi', 'c'): 10**-2,
    ('milli', 'm'): 10**-3,
    ('micro', 'μ', 'u'): 10**-6,
    ('nano', 'n'): 10**-9,
    ('pico', 'p'): 10**-12
}


class MetricConverter(FactorConverter):

    base_name = None
    base_short = None

    def __init__(self):
        if self.base_name is None:
            raise ValueError(f"base_name in {self.__class__.__name__} is None!")
        elif self.base_short is None:
            raise ValueError(f"base_short in {self.__class__.__name__} is None!")
        else:
            self.BASE_UNIT = (self.base_name, self.base_short)
            for names, factor in metric_factors.items():
                if names[1] == "m":
                    self.conflicts.append(names[1] + self.base_short)
                name_list = []
                for index, name in enumerate(names):
                    if index == 0:
                        name_list.append(name + self.base_name)
                    else:
                        name_list.append(name + self.base_short)
                self.factor_names.append(name_list)
                self.factor_values.append(factor)
