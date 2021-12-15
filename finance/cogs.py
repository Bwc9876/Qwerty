from io import BytesIO

from discord import File
from discord.commands import slash_command, ApplicationContext, Option
from mplfinance import plot
from yfinance import Ticker

from bot_base.cogs import BaseCog
from bot_settings import DEBUG_GUILDS
from finance.models import FinanceCogData

periods = {
    '1 year': ('1y', '1wk'),
    '6 months': ('6mo', '1wk'),
    '1 month': ('1mo', '1d'),
    '1 week': ('1wk', '1h'),
    '1 day': ('1d', '15m')
}


class Finance(BaseCog, name='Finance'):

    cog_data_model = FinanceCogData

    @slash_command(name='stock', description='Get the information for a stock', guild_ids=DEBUG_GUILDS)
    async def stock(self, ctx: ApplicationContext,
                    symbol: Option(str, description="The symbol of the stock to get the info for"),
                    period: Option(str, description="The period of time to graph", choices=list(periods.keys()))):
        symbol: str = symbol.upper()
        ticker = Ticker(symbol)
        time = periods.get(period)
        await ctx.defer()
        try:
            data = ticker.history(period=time[0], interval=time[1])
            between_color = 'g' if data['Close'].pct_change().sum() > 0 else 'r'
            out_file = BytesIO()
            plot(data, style='charles', type='candle',
                 title=f'Candlestick For {ticker.info.get("shortName")} Over {period}', ylabel='Price ($)',
                 fill_between=dict(y1=data['Close'].values, y2=data['Low'].min(), color=between_color, alpha=0.2),
                 savefig=out_file)
            out_file.seek(0)
            await ctx.respond(file=File(out_file, filename='candlestick.png'))
            out_file.close()
        except ConnectionError:
            await ctx.send(f"Couldn't find stock information for \"{symbol}\"")
