import string

from .converter_base import MetricConverter, FactorConverter, CrossConvert, BaseConverter, LambdaConverter


# Lambda Converters


class StringConverter(LambdaConverter):

    def sanitize_value(self, value, unit):
        return str(value)

    def valid_value_for_unit(self, unit, value):
        return True

    BASE_UNIT = ('str', 'string')

    @staticmethod
    def base_func(x):
        return str(x)

    functions = {
        ('upper', 'uppercase'): lambda x:   x.upper(),
        ('lower', 'lowercase'): lambda x:   x.lower(),
        ('altering',): lambda x:    ''.join([c.lower() if i % 2 == 0 else c.upper() for i, c in enumerate(x)]),
        ('codes', 'code'): lambda x:   '|'.join([str(ord(c)) for c in x]),
        ('letters', 'letter'): lambda x: ''.join([c for c in x if c in string.ascii_letters]),
        ('numbers', 'numbers', '#'): lambda x: ''.join([c for c in x if c in string.digits]),
        ('special', 'specials'): lambda x: ''.join([c for c in x if c not in string.ascii_letters + string.digits])
    }

    def unit_str(self, unit):
        return f"({unit})"


# Metric Converters


class MeterConverter(MetricConverter):
    base_name = "meter"
    base_short = "m"


class GramConverter(MetricConverter):
    base_name = "gram"
    base_short = "g"


class WattConverter(MetricConverter):
    base_name = "watt"
    base_short = "W"


class ByteConverter(MetricConverter):
    base_name = "byte"
    base_short = "B"

    def unit_str(self, unit):
        return unit.upper()

# Factor Converters


class ImperialDistanceConverter(FactorConverter):
    BASE_UNIT = ("foot", "feet", 'ft')

    factor_names = [('inch', 'inches', 'in'), ('yard', 'yards', 'yd'), ('mile', 'miles', 'mi')]
    factor_values = [1 / 12, 3, 5280]


class ImperialAreaConverter(FactorConverter):
    BASE_UNIT = ('acre', 'acres')

    factor_names = [('square mile', 'square miles', 'mi^2', 'sq mi', 'mi²')]
    factor_values = [640]


class ImperialVolumeConverter(FactorConverter):
    BASE_UNIT = ('pint', 'pt')

    factor_names = [('fluid ounce', 'fl oz'), ('quart', 'qt'), ('gallon', 'gal')]
    factor_values = [1 / 20, 2, 8]


class ImperialMassConverter(FactorConverter):
    BASE_UNIT = ('pound', 'lb')

    factor_names = [('ounce', 'oz'), ('ton', 't')]
    factor_values = [1 / 16, 2240]


class TimeConverter(FactorConverter):

    BASE_UNIT = ('second', 's', 'sec')

    factor_names = [('nanosecond', 'ns'), ('microsecond', 'μs', 'us'), ('millisecond', 'ms'), ('minute', 'min'),
                    ('hour', 'hr', 'h'), ('day', 'd'), ('week', 'w'), ('month', 'mon'), ('year', 'y'),
                    ('decade',), ('century', 'cen')]
    factor_values = [10**-9, 10**-6, 10**-3, 60, 3600, 86400, 604800, 2592000, 31557600, 315576000, 3155760000]


class DollarsConverter(FactorConverter):

    BASE_UNIT = ('cents', '₵', '𝇍', '¢')

    factor_names = [('dollars', 'us dollars', '$')]


# Other Converters


class NumberSystemConverter(BaseConverter):

    BASE_UNIT = ('base10', 'dec', 'decimal')

    bases = {
        ('base2', 'binary', 'bin'): 2,
        ('base16', 'hexadecimal', 'hex'): 16,
        ('base8', 'octal', 'oct'): 8
    }

    over_10_digits = {i + 10: x for i, x in enumerate(string.ascii_lowercase)}

    def convert_letter_to_number(self, letter):
        for key, val in self.over_10_digits.items():
            if letter == val:
                return key
        return int(letter)

    def get_base_factor(self, unit):
        for key, value in self.bases.items():
            if unit in key:
                return value
        return None

    @staticmethod
    def check_int(value):
        try:
            float_val = float(value)
            return float_val % 1 == 0
        except ValueError:
            return False

    def sanitize_value(self, value, unit):
        if unit in self.BASE_UNIT:
            return int(value)
        else:
            return value.lower()

    def valid_value_for_unit(self, unit, value):
        value = value.lower()
        if unit in self.BASE_UNIT:
            return self.check_int(value)
        else:
            target_base = self.get_base_factor(unit)
            if target_base <= 10:
                return self.check_int(value)
            elif target_base < 36:
                allowed = string.ascii_lowercase[:target_base-10]
                for char in value:
                    if (char in string.ascii_lowercase) and (char not in allowed):
                        return False
                return True
            else:
                return False

    def can_process(self, unit):
        for key in list(self.bases.keys()) + [self.BASE_UNIT]:
            if unit.lower() in key:
                return True
        return False

    def to_base(self, value, unit):
        value = self.sanitize_value(value, unit)
        unit = unit.lower()
        target_base = self.get_base_factor(unit)
        return sum([self.convert_letter_to_number(x) * target_base**i for i, x in enumerate(reversed(value))])

    def from_base(self, value, unit):
        value = self.sanitize_value(value, self.BASE_UNIT[0])
        unit = unit.lower()
        target_base = self.get_base_factor(unit)
        inter_value = value
        output_number = ''
        while inter_value != 0:
            new_char = inter_value % target_base
            output_number += self.over_10_digits.get(new_char, str(new_char))
            inter_value //= target_base
        return ''.join(reversed(output_number))


# Cross Converters


class ImperialMetricDistanceConverter(CrossConvert):

    SYSTEM_1 = ImperialDistanceConverter
    SYSTEM_2 = MeterConverter

    factor = 3.28084


class ImperialMetricWeightConverter(CrossConvert):

    SYSTEM_1 = ImperialMassConverter
    SYSTEM_2 = GramConverter

    factor = 0.002204623
