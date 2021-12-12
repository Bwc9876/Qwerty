from discord import File
from discord.commands import slash_command, ApplicationContext, Option, AutocompleteContext
from discord.utils import basic_autocomplete
from sympy.core.mul import Mul

from bot_base.cogs import BaseCog
from bot_settings import DEBUG_GUILDS
from persistence import _, queryset_to_list
from .conversions.convert import convert, ConverterError, get_all_units_for_value, get_all_units_for_from_unit
from .graphing.graph_executor import graph, validate_formula, GraphError
from .math_executor import solve_expression, solve_equation, ex_validate, eq_validate, MathRunError
from .models import MathCogData, MemoryEntry


async def from_unit_autocomplete(ctx: AutocompleteContext):
    value = ctx.options.get('value', "")
    out_units = get_all_units_for_value(value)
    return out_units


async def to_unit_autocomplete(ctx: AutocompleteContext):
    value = ctx.options.get('value', "")
    from_unit = ctx.options.get('from_unit', "")
    out_units = get_all_units_for_from_unit(from_unit, value)
    return out_units


class Math(BaseCog, name="Math"):
    cog_data_model = MathCogData

    @slash_command(name="store", description="Store a value to memory for use in calculations", guild_ids=DEBUG_GUILDS)
    async def mem_store(self, ctx: ApplicationContext,
                        slot: Option(int, description="The slot in memory to store the value to", min_value=0,
                                     max_value=9),
                        value: Option(float, description="The value to store", min_value=-9999999, max_value=9999999)):
        data: MathCogData = await self.load_data(ctx.interaction.guild.id)
        new_mem: MemoryEntry = (await _(data.mem.get_or_create)(index=slot, defaults={'value': value}))[0]
        new_mem.value = value
        await _(new_mem.save)()
        await ctx.respond(f"{value} saved in memory slot {slot}")

    @slash_command(name="recall", description="Recall a value from memory", guild_ids=DEBUG_GUILDS)
    async def mem_recall(self, ctx: ApplicationContext,
                         slot: Option(int, description="The slot in memory to get the value from", min_value=0,
                                      max_value=9)):
        try:
            data: MathCogData = await self.load_data(ctx.interaction.guild.id)
            mem = await _(data.mem.get)(index=slot)
            await ctx.respond(f"{str(float(mem.value))} is stored in slot {slot}")
        except MemoryEntry.DoesNotExist:
            await ctx.respond(f"There is nothing stored in slot {slot}")

    async def get_memory(self, data: MathCogData) -> dict:
        memories: list[MemoryEntry] = await _(queryset_to_list)(await _(data.mem.all)())
        return {m.index: float(m.value) for m in memories}

    async def format_answer(self, answer):
        if isinstance(answer, Mul):
            return str(answer).replace("I", "i")
        elif isinstance(answer, type(None)):
            return "Nothing"
        elif isinstance(answer, bool):
            return "True" if answer else "False"
        elif isinstance(answer, float | int):
            possible = str(float(answer))
            if len(possible) > 2000:
                return "Too Big For Discord"
            else:
                return possible
        else:
            return str(answer)

    @slash_command(name="calculate", description="Evaluate a mathematical expression", guild_ids=DEBUG_GUILDS)
    async def calculate(self, ctx: ApplicationContext, *,
                        expression: Option(str, description="The expression to evaluate")):
        data: MathCogData = await self.load_data(ctx.interaction.guild.id)
        mem = await self.get_memory(data)
        try:
            await ex_validate(expression)
            await ctx.defer()
            answer = await self.format_answer(await solve_expression(expression.strip(), mem))
            seperator = " is " if answer in ("True", "False", "Nothing") else " = "
            beginning = expression + seperator
            await ctx.respond(beginning + answer)
        except MathRunError as error:
            await ctx.respond(error.args[0], ephemeral=True)

    @slash_command(name="solve", description="Solve the given equation (can only do one unknown)",
                   guild_ids=DEBUG_GUILDS)
    async def solve(self, ctx: ApplicationContext, *, equation: Option(str, description="The equation to solve"),
                    variable_name: Option(str, description="The name of the variable to solve for", required=False,
                                          default='x')):
        data: MathCogData = await self.load_data(ctx.interaction.guild.id)
        mem = await self.get_memory(data)
        try:
            await eq_validate(equation, variable_name)
            await ctx.defer()
            answers = await solve_equation(equation, mem, variable_name)
            answer_count = len(answers)
            if answer_count == 0:
                await ctx.respond("Couldn't Find A Solution")
            elif answer_count == 1:
                await ctx.respond(f"{variable_name} = {await self.format_answer(answers[0])}")
            else:
                answer_list = "{" + ', '.join([(await self.format_answer(answer)) for answer in answers]) + "}"
                await ctx.respond(f"{variable_name} = {answer_list}")
        except MathRunError as error:
            await ctx.respond(error.args[0], ephemeral=True)

    @slash_command(name="convert", description="Convert from one unit to another", guild_ids=DEBUG_GUILDS)
    async def convert(self, ctx: ApplicationContext, value: Option(str, description="The value to convert"),
                      from_unit: Option(str, description="The unit to convert from",
                                        autocomplete=basic_autocomplete(from_unit_autocomplete)),
                      to_unit: Option(str, description="The unit to convert to",
                                      autocomplete=basic_autocomplete(to_unit_autocomplete))):
        try:
            await ctx.respond(convert(value, from_unit, to_unit))
        except ConverterError as error:
            await ctx.respond(error.args[0], ephemeral=True)

    @slash_command(name="graph", description="Graph a set of formulas", guild_ids=DEBUG_GUILDS)
    async def graph(self, ctx: ApplicationContext, formulas: Option(str,
                                                                    description="The formula(s) to graph, seperated by pipes (|), do not include the f(x)= or y="),
                    max_x: Option(int, description="The maximum value of x to graph, minimum is this *-1",
                                  required=False, default=10, min_value=1, max_value=1000),
                    max_y: Option(int, description="The maximum value of y to graph, minimum is this *-1",
                                  required=False, default=10, min_value=1, max_value=1000),
                    x_axis_label: Option(str, description="The label for the x-axis", required=False, default="x"),
                    y_axis_label: Option(str, description="The label for the y-axis", required=False, default="ƒ(x)"),
                    title: Option(str, description="The title for the graph", required=False, default="")):
        try:
            validate_formula(formulas)
            await ctx.defer()
            graph_image = await graph(formulas, max_x, max_y, x_axis_label, y_axis_label, title)
            graph_file = File(graph_image, filename="graph.png")
            await ctx.respond(file=graph_file)
            graph_image.close()
        except GraphError as error:
            await ctx.respond(error.args[0], ephemeral=True)

    @slash_command(name="math-help", description="Explains how to use the /calculate command", guild_ids=DEBUG_GUILDS)
    async def explain(self, ctx: ApplicationContext):
        await ctx.respond("https://gist.github.com/Bwc9876/daa2bfbf8ee0b898dc67fe99796ed9ae", ephemeral=True)
