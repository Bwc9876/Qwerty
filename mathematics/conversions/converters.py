from .converter_base import MetricConverter, FactorConverter, CrossConvert

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
    BASE_UNIT = ("foot", 'ft')

    factor_names = [('inch', 'in'), ('yard', 'yd'), ('mile', 'mi')]
    factor_values = [1 / 12, 3, 5280]


class ImperialAreaConverter(FactorConverter):
    BASE_UNIT = ('acre',)

    factor_names = [('square mile', 'mi^2', 'sq mi', 'mi²')]
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

    conflicts = ('m',)

    factor_names = [('nanosecond', 'ns'), ('microsecond', 'μs', 'us'), ('millisecond', 'ms'), ('minute', 'min'),
                    ('hour', 'hr', 'h'), ('day', 'd'), ('week', 'w'), ('month', 'mon'), ('year', 'y'),
                    ('decade',), ('century', 'cen')]
    factor_values = [10**-9, 10**-6, 10**-3, 60, 3600, 86400, 604800, 2592000, 31557600, 315576000, 3155760000]


class DollarsConverter(FactorConverter):

    BASE_UNIT = ('cents', '₵', '𝇍', '¢')

    factor_names = [('dollars', 'us dollars', '$')]


# Cross Converters


class ImperialMetricDistanceConverter(CrossConvert):

    SYSTEM_1 = ImperialDistanceConverter
    SYSTEM_2 = MeterConverter

    factor = 3.28084


class ImperialMetricWeightConverter(CrossConvert):

    SYSTEM_1 = ImperialMassConverter
    SYSTEM_2 = GramConverter

    factor = 0.002204623
