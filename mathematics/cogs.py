from discord.commands import slash_command, ApplicationContext, Option
from sympy.core.mul import Mul

from bot_base.cogs import BaseCog
from bot_settings import DEBUG_GUILDS
from .models import MathCogData, MemoryEntry
from persistence import _, queryset_to_list
from .math_executor import solve_expression, solve_equation, MathRunError


class MathCog(BaseCog, name="Math"):

    cog_data_model = MathCogData

    @slash_command(name="store", description="Store a value to memory for use in calculations", guild_ids=DEBUG_GUILDS)
    async def mem_store(self, ctx: ApplicationContext,
                        slot: Option(int, description="The slot in memory to store the value to", min_value=0, max_value=9),
                        value: Option(float, description="The value to store", min_value=-9999999, max_value=9999999)):
        data: MathCogData = await self.load_data(ctx.interaction.guild.id)
        new_mem: MemoryEntry = (await _(data.mem.get_or_create)(index=slot, defaults={'value': value}))[0]
        new_mem.value = value
        await _(new_mem.save)()
        await ctx.respond(f"{value} saved in memory slot {slot}")

    @slash_command(name="recall", description="Recall a value from memory", guild_ids=DEBUG_GUILDS)
    async def mem_recall(self, ctx: ApplicationContext,
                         slot: Option(int, description="The slot in memory to get the value from", min_value=0, max_value=9)):
        try:
            data: MathCogData = await self.load_data(ctx.interaction.guild.id)
            mem = await _(data.mem.get)(index=slot)
            await ctx.respond(f"{str(float(mem.value))} is stored in slot {slot}")
        except MemoryEntry.DoesNotExist:
            await ctx.respond(f"There is nothing stored in slot {slot}")

    async def get_memory(self, data: MathCogData) -> list[MemoryEntry]:
        memories: list[MemoryEntry] = await _(queryset_to_list)(await _(data.mem.all)())
        return {m.index: float(m.value) for m in memories}

    async def format_answer(self, answer):
        if isinstance(answer, Mul):
            return str(answer).replace("I", "i")
        else:
            possible = str(float(answer))
            if len(possible) > 2000:
                return "Too Big For Discord"
            else:
                return possible

    @slash_command(name="calculate", description="Evaluate a mathematical expression", guild_ids=DEBUG_GUILDS)
    async def calculate(self, ctx: ApplicationContext, *, expression: Option(str, description="The expression to evaluate")):
        data: MathCogData = await self.load_data(ctx.interaction.guild.id)
        mem = await self.get_memory(data)
        try:
            answer = await self.format_answer(await solve_expression(expression.strip(), mem))
            beginning = expression + " = "
            await ctx.respond(beginning + answer)

        except MathRunError as error:
            await ctx.respond(error.args[0], ephemeral=True)

    @slash_command(name="solve", description="Solve the given equation (can only do one unknown)", guild_ids=DEBUG_GUILDS)
    async def solve(self, ctx: ApplicationContext, *, equation: Option(str, description="The equation to solve"),
                    variable_name: Option(str, description="The name of the variable to solve for", required=False, default='x')):
        data: MathCogData = await self.load_data(ctx.interaction.guild.id)
        mem = await self.get_memory(data)
        await ctx.defer()
        try:
            answers = await solve_equation(equation, mem, variable_name)
            answer_count = len(answers)
            if answer_count == 0:
                await ctx.respond("Couldn't Find A Solution")
            elif answer_count == 1:
                await ctx.respond(f"{variable_name} = {await self.format_answer(answers[0])}")
            else:
                answer_list = "{" + ', '.join([(await self.format_answer(answer)) for answer in answers]) + "}"
                await ctx.respond(f"{variable_name} = {answer_list}")
        except OverflowError:
            await ctx.respond("Overflow Error")
        except MathRunError as error:
            await ctx.respond(error.args[0], ephemeral=True)

    @slash_command(name="math-help", description="Explains how to use the /calculate command", guild_ids=DEBUG_GUILDS)
    async def explain(self, ctx: ApplicationContext):
        await ctx.respond("https://gist.github.com/Bwc9876/daa2bfbf8ee0b898dc67fe99796ed9ae", ephemeral=True)
