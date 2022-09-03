import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context, clean_content
from parsita import ParseError

import roll.exceptions as rollerr
from cogs.parallelism import Parallelism
from roll.ast import MAX_ROLLS
from roll.parser import parse_program
from utils import get_name_string
from utils.exceptions import OutputTooLargeError

LONG_HELP_TEXT = """
Rolls an unbiased xdy (x dice with y sides).

If no dice are specified, it will roll a single 1d6 (one 6-sided die).
____________________________________________________________

Supports basic arithmetic:
    !roll or !r         | rolls a 1d6
    !r 1d6              | an explicit 1d6
    !r 1d6 + 5          | adds 5 to a 1d6 output (supports +, -, *, /, ^)
    !r (1d6+1)+(1d6*10) | supports brackets
    !r (1d6)d(1d6)      | supports nested rolls

Note: using division returns a floating point value.
"""

SHORT_HELP_TEXT = """Rolls an unbiased xdy (x dice with y sides)"""

SUCCESS_OUT = """
:game_die: **DICE TIME** :game_die:
{ping}
{body}
"""

FAILURE_OUT = """
:warning: **DICE UNDERMINE** :warning:
{ping} - **{error}**
{body}
"""

WARNING_OUT = """
:no_entry_sign: **DICE CRIME** :no_entry_sign:
{ping} - **{error}**
{body}
"""

INTERNAL_OUT = """
:fire: **DICE GRIME** :fire:
{ping} - **{error}**
{body}
"""


class Roll(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(
        help=LONG_HELP_TEXT, brief=SHORT_HELP_TEXT, aliases=["r"], rest_is_raw=True
    )
    async def roll(self, ctx: Context, *, message: clean_content):
        loop = asyncio.get_event_loop()
        display_name = get_name_string(ctx.message)

        def work():
            return run(message, display_name)

        p = await Parallelism.get(self.bot)
        p.send_to_ctx_after_threaded(work, ctx, loop)

    @app_commands.command(name="roll", description=SHORT_HELP_TEXT)
    async def roll_slash(self, int: discord.Interaction, dice: str):
        loop = asyncio.get_event_loop()

        def work():
            return run(dice, "")

        p = await Parallelism.get(self.bot)
        p.send_to_int_after_threaded(work, int, loop)


def run(message, display_name):
    try:
        message = message.strip()
        if len(message) == 0:
            message = "1d6"
        logging.debug("==== Parsing ====")
        program = parse_program(message)
        logging.debug("==== Evaluation ====")
        logging.debug(program)
        values = program.reduce()
        logging.debug("==== Output ====")
        string_rep = program.string_rep
        pairs_assignments = string_rep.assignments
        pairs_expressions = zip(values, string_rep.expressions)
        out = SUCCESS_OUT.format(
            ping=display_name,
            body="\n".join(
                [f"{p0} = `{p1}`" for p0, p1 in pairs_assignments]
                + [f"**{p0}** ⟵ `{p1}`" for p0, p1 in pairs_expressions]
            ),
        )
        if len(out) > MAX_ROLLS:
            raise OutputTooLargeError
    except rollerr.WarningError as e:
        out = WARNING_OUT.format(
            ping=display_name, error=e.__class__.__name__, body=f"_{e.out}_"
        )
    except ParseError as e:
        out = FAILURE_OUT.format(
            ping=display_name, error=e.__class__.__name__, body=f"```{e}```"
        )
    except rollerr.RunTimeError as e:
        out = FAILURE_OUT.format(
            ping=display_name, error=e.__class__.__name__, body=f"```{e}```"
        )
    except (rollerr.InternalError, Exception) as e:
        out = INTERNAL_OUT.format(
            ping=display_name,
            error=e.__class__.__name__,
            body=f"**Internal error:**```{e}```",
        )
        logging.exception(e)
    logging.debug("")
    return out


async def setup(bot: Bot):
    await bot.add_cog(Roll(bot))
