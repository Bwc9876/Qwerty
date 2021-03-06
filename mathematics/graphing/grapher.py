from collections.abc import Callable
from io import BytesIO
from typing import Any

import matplotlib.font_manager as font_manager
from PIL import Image
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.pyplot import figure
from matplotlib.ticker import MaxNLocator
from sympy import plot_implicit, Eq
from sympy.abc import x, y
from sympy.plotting.plot import _matplotlib_list, Plot

DEFAULT_FONT = font_manager.FontProperties(family="times new roman", style='normal', size=10)


class Grapher:
    DEFAULT_OPTIONS = {
        'max_x': 10,
        'max_y': 10,
        'font': DEFAULT_FONT,
        'equations': [],
        'title': "",
        'x_axis_label': r"x",
        'y_axis_label': "ƒ(x)",
        'origin_lines': {
            'color': "#00000050",
            'width': 1.5
        },
        'function_lines': {
            'width': 1
        },
        'ticks': {
            'max_major_buckets': 10,
            'max_minor_buckets': 20,
        },
        'grids': {
            'minor_alpha': 0.2,
            'major_alpha': 0.5
        },
    }

    def _plot_origin_lines(self):
        color = self.options['origin_lines']['color']
        width = self.options['origin_lines']['width']
        x_range = (self.options['min_x'], self.options['max_x'])
        y_range = (self.options['min_y'], self.options['max_y'])
        self._axes.plot(x_range, (0, 0), color, lw=width)
        self._axes.plot((0, 0), y_range, color, lw=width)

    def _process_plot(self, index: int, plot: Plot):
        series = plot[0]
        points = series.get_raster()
        x, y = _matplotlib_list(points[0])
        width = self.options["function_lines"]["width"]
        if index < len(self.options['equations']):
            self._axes.plot(x, y, lw=width, label=f"ƒ(x) = {self.options['equations'][index]}")
        else:
            self._axes.plot(x, y, lw=width, label=" ")

    def _plot_function_lines(self):
        for index, plot in enumerate(self._source_plots):
            self._process_plot(index, plot)

    def _setup_limits(self):
        self._axes.set_xlim(self.options['min_x'], self.options['max_x'])
        self._axes.set_ylim(self.options['min_y'], self.options['max_y'])

    def _setup_ticks(self):
        self._axes.xaxis.set_major_locator(MaxNLocator(10, integer=True))
        self._axes.yaxis.set_major_locator(MaxNLocator(10, integer=True))
        self._axes.xaxis.set_minor_locator(MaxNLocator(20))
        self._axes.yaxis.set_minor_locator(MaxNLocator(20))

    def _setup_labels(self):
        font = self.options['font']
        font_dict = {'name': font.get_name()}
        self._axes.set_xlabel(self.options['x_axis_label'], **font_dict)
        self._axes.set_ylabel(self.options['y_axis_label'], **font_dict)
        self._axes.set_title(self.options['title'], **font_dict)
        self._axes.legend(prop=font)

    def _setup_grids(self):
        self._axes.grid(which='major', alpha=self.options['grids']['major_alpha'])
        self._axes.grid(which='minor', alpha=self.options['grids']['minor_alpha'])

    def _setup_spines(self):
        self._axes.spines['left'].set_position(('axes', 0))
        self._axes.spines['bottom'].set_position(('axes', 0))
        # for side in ('left', 'bottom', 'right', 'top'):
        #     self.axis.spines[side].set_color(None)

    def _render(self):
        self._setup_limits()
        self._plot_origin_lines()
        self._plot_function_lines()
        self._setup_ticks()
        self._setup_spines()
        self._setup_grids()
        self._setup_labels()
        self._fig.canvas.draw()
        self._rendered = True

    def __init__(self, equation_functions: list[Callable[[type(x)], Any]], **options):
        self._rendered: bool = False
        self._fig: Figure = figure()
        self._axes: Axes = self._fig.subplots()
        self.options: dict = options
        for key, value in self.DEFAULT_OPTIONS.items():
            self.options.setdefault(key, value)
        self.options['min_x'] = self.options['max_x'] * -1
        self.options['min_y'] = self.options['max_y'] * -1
        self._source_plots: list[Plot] = []
        x_var = (x, self.options['min_x'], self.options['max_x'])
        y_var = (y, self.options['min_y'], self.options['max_y'])
        for equation_function in equation_functions:
            new_plot = plot_implicit(Eq(y, equation_function(x)), x_var, y_var, show=False)
            self._source_plots.append(new_plot)

    def show(self):
        if self._rendered is False:
            self._render()
        self._fig.show()

    def save(self, file: str):
        if self._rendered is False:
            self._render()
        self._fig.savefig(file)

    def as_bytes(self):
        if self._rendered is False:
            self._render()
        out_bytes = BytesIO()
        image = Image.frombytes('RGB', self._fig.canvas.get_width_height(), self._fig.canvas.tostring_rgb())
        image.save(out_bytes, 'PNG')
        out_bytes.seek(0)
        return out_bytes
