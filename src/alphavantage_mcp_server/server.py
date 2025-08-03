import asyncio
import json
from enum import Enum

import mcp.server.stdio
import mcp.types as types
import toml
import uvicorn
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.streamable_http import StreamableHTTPServerTransport

from alphavantage_mcp_server.api import (
    fetch_quote,
    fetch_intraday,
    fetch_time_series_daily,
    fetch_time_series_daily_adjusted,
    fetch_time_series_weekly,
    fetch_time_series_weekly_adjusted,
    fetch_time_series_monthly,
    fetch_time_series_monthly_adjusted,
    fetch_realtime_bulk_quotes,
    search_endpoint,
    fetch_market_status,
    fetch_realtime_options,
    fetch_historical_options,
    fetch_news_sentiment,
    fetch_top_gainer_losers,
    fetch_insider_transactions,
    fetch_analytics_fixed_window,
    fetch_analytics_sliding_window,
    fetch_company_overview,
    company_dividends,
    fetch_etf_profile,
    fetch_company_splits,
    fetch_income_statement,
    fetch_balance_sheet,
    fetch_cash_flow,
    fetch_listing_status,
    fetch_earnings_calendar,
    fetch_ipo_calendar,
    fetch_exchange_rate,
    fetch_fx_intraday,
    fetch_fx_daily,
    fetch_fx_weekly,
    fetch_fx_monthly,
    fetch_digital_currency_intraday,
    fetch_digital_currency_daily,
    fetch_digital_currency_monthly,
    fetch_wti_crude,
    fetch_brent_crude,
    fetch_natural_gas,
    fetch_copper,
    fetch_aluminum,
    fetch_wheat,
    fetch_corn,
    fetch_cotton,
    fetch_sugar,
    fetch_coffee,
    fetch_all_commodities,
    fetch_real_gdp,
    fetch_real_gdp_per_capita,
    fetch_treasury_yield,
    fetch_federal_funds_rate,
    fetch_cpi,
    fetch_inflation,
    fetch_retail_sales,
    fetch_durables,
    fetch_unemployment,
    fetch_nonfarm_payrolls,
    fetch_sma,
    fetch_ema,
    fetch_wma,
    fetch_dema,
    fetch_tema,
    fetch_trima,
    fetch_kama,
    fetch_mama,
    fetch_t3,
    fetch_macd,
    fetch_macdext,
    fetch_stoch,
    fetch_stochf,
    fetch_rsi,
    fetch_stochrsi,
    fetch_willr,
    fetch_adx,
    fetch_adxr,
    fetch_apo,
    fetch_ppo,
    fetch_mom,
    fetch_bop,
    fetch_cci,
    fetch_cmo,
    fetch_roc,
    fetch_rocr,
    fetch_aroon,
    fetch_aroonosc,
    fetch_mfi,
    fetch_trix,
    fetch_ultosc,
    fetch_dx,
    fetch_minus_di,
    fetch_plus_di,
    fetch_minus_dm,
    fetch_plus_dm,
    fetch_bbands,
    fetch_midpoint,
    fetch_midprice,
    fetch_sar,
    fetch_trange,
    fetch_atr,
    fetch_natr,
    fetch_ad,
    fetch_adosc,
    fetch_obv,
    fetch_ht_trendline,
    fetch_ht_sine,
    fetch_ht_trendmode,
    fetch_ht_dcperiod,
    fetch_ht_dcphase,
    fetch_ht_phasor,
    fetch_vwap, fetch_earnings, fetch_earnings_call_transcript,
)


class AlphavantageTools(str, Enum):
    TIME_SERIES_INTRADAY = "time_series_intraday"
    TIME_SERIES_DAILY = "time_series_daily"
    TIME_SERIES_DAILY_ADJUSTED = "time_series_daily_adjusted"
    TIME_SERIES_WEEKLY = "time_series_weekly"
    TIME_SERIES_WEEKLY_ADJUSTED = "time_series_weekly_adjusted"
    TIME_SERIES_MONTHLY = "time_series_monthly"
    TIME_SERIES_MONTHLY_ADJUSTED = "time_series_monthly_adjusted"
    STOCK_QUOTE = "stock_quote"
    REALTIME_BULK_QUOTES = "realtime_bulk_quotes"
    SYMBOL_SEARCH = "symbol_search"
    MARKET_STATUS = "market_status"
    REALTIME_OPTIONS = "realtime_options"
    HISTORICAL_OPTIONS = "historical_options"
    NEWS_SENTIMENT = "news_sentiment"
    TOP_GAINERS_LOSERS = "top_gainers_losers"
    INSIDER_TRANSACTIONS = "insider_transactions"
    ANALYTICS_FIXED_WINDOW = "analytics_fixed_window"
    ANALYTICS_SLIDING_WINDOW = "analytics_sliding_window"
    COMPANY_OVERVIEW = "company_overview"
    ETF_PROFILE = "etf_profile"
    COMPANY_DIVIDENDS = "company_dividends"
    COMPANY_SPLITS = "company_dividends"
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    COMPANY_EARNINGS = "company_earnings"
    LISTING_STATUS = "listing_status"
    EARNINGS_CALENDAR = "earnings_calendar"
    EARNINGS_CALL_TRANSCRIPT = "earnings_call_transcript"
    IPO_CALENDAR = "ipo_calendar"
    EXCHANGE_RATE = "exchange_rate"
    FX_INTRADAY = "fx_intraday"
    FX_DAILY = "fx_daily"
    FX_WEEKLY = "fx_weekly"
    FX_MONTHLY = "fx_monthly"
    CRYPTO_INTRADAY = "crypto_intraday"
    DIGITAL_CURRENCY_DAILY = "digital_currency_daily"
    DIGITAL_CURRENCY_WEEKLY = "digital_currency_weekly"
    DIGITAL_CURRENCY_MONTHLY = "digital_currency_monthly"
    WTI_CRUDE_OIL = "wti_crude_oil"
    BRENT_CRUDE_OIL = "brent_crude_oil"
    NATURAL_GAS = "natural_gas"
    COPPER = "copper"
    ALUMINUM = "aluminum"
    WHEAT = "wheat"
    CORN = "corn"
    COTTON = "cotton"
    SUGAR = "sugar"
    COFFEE = "coffee"
    ALL_COMMODITIES = "all_commodities"
    REAL_GDP = "real_gdp"
    REAL_GDP_PER_CAPITA = "real_gdp_per_capita"
    TREASURY_YIELD = "treasury_yield"
    FEDERAL_FUNDS_RATE = "federal_funds_rate"
    CPI = "cpi"
    INFLATION = "inflation"
    RETAIL_SALES = "retail_sales"
    DURABLES = "durables"
    UNEMPLOYMENT = "unemployment"
    NONFARM_PAYROLL = "nonfarm_payroll"
    SMA = "sma"
    EMA = "ema"
    WMA = "wma"
    DEMA = "dema"
    TEMA = "tema"
    TRIMA = "trima"
    KAMA = "kama"
    MAMA = "mama"
    VWAP = "vwap"
    T3 = "t3"
    MACD = "macd"
    MACDEXT = "macdext"
    STOCH = "stoch"
    STOCHF = "stochf"
    RSI = "rsi"
    STOCHRSI = "stochrsi"
    WILLR = "willr"
    ADX = "adx"
    ADXR = "adxr"
    APO = "apo"
    PPO = "ppo"
    MOM = "mom"
    BOP = "bop"
    CCI = "cci"
    CMO = "cmo"
    ROC = "roc"
    ROCR = "rocr"
    AROON = "aroon"
    AROONOSC = "aroonosc"
    MFI = "mfi"
    TRIX = "trix"
    ULTOSC = "ultosc"
    DX = "dx"
    MINUS_DI = "minus_di"
    PLUS_DI = "plus_di"
    MINUS_DM = "minus_dm"
    PLUS_DM = "plus_dm"
    BBANDS = "bbands"
    MIDPOINT = "midpoint"
    MIDPRICE = "midprice"
    SAR = "sar"
    TRANGE = "trange"
    ATR = "atr"
    NATR = "natr"
    AD = "ad"
    ADOSC = "adosc"
    OBV = "obv"
    HT_TRENDLINE = "ht_trendline"
    HT_SINE = "ht_sine"
    HT_TRENDMODE = "ht_trendmode"
    HT_DCPERIOD = "ht_dcperiod"
    HT_DCPHASE = "ht_dcphase"
    HT_PHASOR = "ht_phasor"


server = Server("alphavantage")


@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name=AlphavantageTools.STOCK_QUOTE.value,
            description="Fetch the latest price and volume information for a ticker of your choice",
            arguments=[
                types.PromptArgument(
                    name="symbol",
                    description="Stock symbol",
                    required=True,
                ),
                types.PromptArgument(
                    name="datatype",
                    description="Data type (json or csv). Default is json",
                    required=False,
                ),

            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TIME_SERIES_INTRADAY.value,
            description="Fetch current and 20+ years of historical intraday OHLCV time series of the equity specified",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TIME_SERIES_DAILY.value,
            description="Fetch a time series daily",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TIME_SERIES_DAILY_ADJUSTED.value,
            description="Fetch a time series daily adjusted",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="outputsize",
                    description="Output size (compact or full)",
                    required=False,
                ),
            types.PromptArgument(
                    name="datatype",
                    description="Data type (json or csv). Default is json",
                    required=False,
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TIME_SERIES_WEEKLY.value,
            description="Fetch a time series weekly",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TIME_SERIES_WEEKLY_ADJUSTED.value,
            description="Fetch a time series weekly adjusted",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TIME_SERIES_MONTHLY.value,
            description="Fetch a time series monthly",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TIME_SERIES_MONTHLY_ADJUSTED.value,
            description="Fetch a time series monthly adjusted",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.REALTIME_BULK_QUOTES.value,
            description="Fetch real time bulk quotes",
            arguments=[
                types.PromptArgument(
                    name="symbols", description="Stock symbols", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.SYMBOL_SEARCH.value,
            description="Search endpoint",
            arguments=[
                types.PromptArgument(
                    name="keywords", description="Keywords", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MARKET_STATUS.value,
            description="Fetch market status",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.REALTIME_OPTIONS.value,
            description="Fetch realtime options",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.HISTORICAL_OPTIONS.value,
            description="Fetch the full historical options chain for a specific symbol on a specific date, covering 15+ years of history",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="date",
                    description="Trading session date (YYYY-MM-DD). or example, date=2017-11-15",
                    required=True,
                ),
                types.PromptArgument(
                    name="datatype",
                    description="Data type (json or csv). Default is json",
                    required=True,
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.NEWS_SENTIMENT.value,
            description="Fetch news sentiment",
            arguments=[
                types.PromptArgument(
                    name="tickers", description="Stock tickers", required=False
                ),
                types.PromptArgument(
                    name="options", description="The news topics of your choice", required=False
                ),
                types.PromptArgument(
                    name="time_from", description="The time range of the news articles you are targeting, time_from=20220410T0130.", required=False
                ),
                types.PromptArgument(
                    name="time_to", description="The time range of the news articles you are targeting. time_to=20230410T0130", required=False
                ),
                types.PromptArgument(
                    name="sort", description="Sort by (latest or oldest). Default sort=LATEST", required=False
                ),
                types.PromptArgument(
                    name="limit", description="Limit the number of news articles returned. Default=50", required=False
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TOP_GAINERS_LOSERS.value,
            description="Fetch top gainers and losers",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.INSIDER_TRANSACTIONS.value,
            description="Fetch insider transactions",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ANALYTICS_FIXED_WINDOW.value,
            description="Fetch analytics fixed window",
            arguments=[
                types.PromptArgument(
                    name="symbols", description="Stock symbols", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ANALYTICS_SLIDING_WINDOW.value,
            description="Fetch analytics sliding window",
            arguments=[
                types.PromptArgument(
                    name="symbols", description="Stock symbols", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.COMPANY_OVERVIEW.value,
            description="Fetch the company information, financial ratios, and other key metrics for the equity specified",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ETF_PROFILE.value,
            description="Fetch ETF profile",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.COMPANY_DIVIDENDS.value,
            description="Fetch company dividends",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.COMPANY_SPLITS.value,
            description="Fetch company splits",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.INCOME_STATEMENT.value,
            description="Fetch company income statement",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.BALANCE_SHEET.value,
            description="Fetch company balance sheet",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.CASH_FLOW.value,
            description="Fetch company cash flow",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.LISTING_STATUS.value,
            description="Fetch listing status",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.COMPANY_EARNINGS.value,
            description="This API returns the annual and quarterly earnings (EPS) for the company of interest.",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.EARNINGS_CALENDAR.value,
            description="Fetch company earnings calendar",
            arguments=[],
        ),
        types.Prompt(
          name=AlphavantageTools.EARNINGS_CALL_TRANSCRIPT.value,
            description="Fetch earnings call transcript",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="quarter", description="Fiscal quarket in the format YYYYQM", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.IPO_CALENDAR.value,
            description="Fetch IPO calendar",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.EXCHANGE_RATE.value,
            description="Fetch exchange rate",
            arguments=[
                types.PromptArgument(
                    name="from_currency", description="The currency you would like to get the exchange rate for.", required=True
                ),
                types.PromptArgument(
                    name="to_currency", description="The destination currency for the exchange rate", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.FX_INTRADAY.value,
            description="Fetch FX intraday",
            arguments=[
                types.PromptArgument(
                    name="from_symbol", description="From symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.FX_DAILY.value,
            description="Fetch FX daily",
            arguments=[
                types.PromptArgument(
                    name="from_symbol", description="From symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.FX_WEEKLY.value,
            description="Fetch FX weekly",
            arguments=[
                types.PromptArgument(
                    name="from_symbol", description="From symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.FX_MONTHLY.value,
            description="Fetch FX monthly",
            arguments=[
                types.PromptArgument(
                    name="from_symbol", description="From symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.CRYPTO_INTRADAY.value,
            description="Fetch intraday time series (timestamp, open, high, low, close, volume) of the cryptocurrency specified",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="The digital/crypto currency", required=True
                ),
                types.PromptArgument(
                    name="market", description="The exchange market of your choice", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Time interval between two consecutive data points in the time series. "
                                                 "The following values are supported: 1min, 5min, 15min, 30min, 60min", required=True
                ),
                types.PromptArgument(
                    name="datatype", description="Data type (json or csv). Default is json", required=False
                ),
                types.PromptArgument(
                    name="outputsize", description="Output size (compact or full)", required=False
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.DIGITAL_CURRENCY_DAILY.value,
            description="Fetch digital currency daily",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Digital currency symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.DIGITAL_CURRENCY_WEEKLY.value,
            description="Fetch digital currency weekly",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Digital currency symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.DIGITAL_CURRENCY_MONTHLY.value,
            description="Fetch digital currency monthly",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Digital currency symbol", required=True
                )
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.WTI_CRUDE_OIL.value,
            description="Fetch WTI crude oil",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.BRENT_CRUDE_OIL.value,
            description="Fetch Brent crude oil",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.NATURAL_GAS.value,
            description="Fetch natural gas",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.COPPER.value,
            description="Fetch copper",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.ALUMINUM.value,
            description="Fetch aluminum",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.WHEAT.value, description="Fetch wheat", arguments=[]
        ),
        types.Prompt(
            name=AlphavantageTools.CORN.value, description="Fetch corn", arguments=[]
        ),
        types.Prompt(
            name=AlphavantageTools.COTTON.value,
            description="Fetch cotton",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.SUGAR.value, description="Fetch sugar", arguments=[]
        ),
        types.Prompt(
            name=AlphavantageTools.COFFEE.value,
            description="Fetch coffee",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.ALL_COMMODITIES.value,
            description="Fetch all commodities",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.REAL_GDP.value,
            description="Fetch real GDP",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.REAL_GDP_PER_CAPITA.value,
            description="Fetch real GDP per capita",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.TREASURY_YIELD.value,
            description="Fetch treasury yield",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.FEDERAL_FUNDS_RATE.value,
            description="Fetch federal funds rate",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.CPI.value,
            description="Fetch consumer price index",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.INFLATION.value,
            description="Fetch inflation",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.RETAIL_SALES.value,
            description="Fetch retail sales",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.DURABLES.value,
            description="Fetch durables",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.UNEMPLOYMENT.value,
            description="Fetch unemployment",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.NONFARM_PAYROLL.value,
            description="Fetch nonfarm payroll",
            arguments=[],
        ),
        types.Prompt(
            name=AlphavantageTools.SMA.value,
            description="Fetch the simple moving average (SMA) values",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Time interval between two consecutive data points in the time series. "
                                                 "The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly", required=True
                ),
                types.PromptArgument(
                    name="month", description="ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets.  For example, month=2009-01", required=False
                ),
                types.PromptArgument(
                    name="time_period", description="Number of data points used to calculate each moving average value. E.g, time_period=60", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="The desired price type in the time series. Four types are supported: close, open, high, low", required=True
                ),
                types.PromptArgument(
                    name="datatype", description="Data type (json or csv). Default is json", required=False
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.EMA.value,
            description="Fetch the exponential moving average (EMA) values",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Time interval between two consecutive data points in the time series. "
                                                 "The following values are supported: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly", required=True
                ),
                types.PromptArgument(
                    name="month", description="ONLY applicable to intraday intervals (1min, 5min, 15min, 30min, and 60min) for the equity markets.  For example, month=2009-01", required=False
                ),
                types.PromptArgument(
                    name="time_period", description="Number of data points used to calculate each moving average value. E.g, time_period=60", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="The desired price type in the time series. Four types are supported: close, open, high, low", required=True
                ),
                types.PromptArgument(
                    name="datatype", description="Data type (json or csv). Default is json", required=False
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.WMA.value,
            description="Fetch weighted moving average",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.DEMA.value,
            description="Fetch double exponential moving average",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TRIMA.value,
            description="Fetch triangular moving average",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.KAMA.value,
            description="Fetch Kaufman adaptive moving average",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MAMA.value,
            description="Fetch MESA adaptive moving average",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
                types.PromptArgument(
                    name="fastlimit", description="Fast limit", required=True
                ),
                types.PromptArgument(
                    name="slowlimit", description="Slow limit", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.T3.value,
            description="Fetch triple exponential moving average",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MACD.value,
            description="Fetch moving average convergence divergence",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MACDEXT.value,
            description="Fetch moving average convergence divergence extended",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.STOCH.value,
            description="Fetch stochastic oscillator",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.STOCHF.value,
            description="Fetch stochastic oscillator fast",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.RSI.value,
            description="Fetch relative strength index",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.STOCHRSI.value,
            description="Fetch stochastic relative strength index",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.WILLR.value,
            description="Fetch Williams' percent range",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ADX.value,
            description="Fetch average directional movement index",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ADXR.value,
            description="Fetch average directional movement index rating",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.APO.value,
            description="Fetch absolute price oscillator",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
                types.PromptArgument(
                    name="fastperiod", description="Fast period", required=True
                ),
                types.PromptArgument(
                    name="slowperiod", description="Slow period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.PPO.value,
            description="Fetch percentage price oscillator",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
                types.PromptArgument(
                    name="fastperiod", description="Fast period", required=True
                ),
                types.PromptArgument(
                    name="slowperiod", description="Slow period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MOM.value,
            description="Fetch momentum",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.BOP.value,
            description="Fetch balance of power",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.CCI.value,
            description="Fetch commodity channel index",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.CMO.value,
            description="Fetch Chande momentum oscillator",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ROC.value,
            description="Fetch rate of change",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="The desired price type in the time series. Four types are supported: close, open, high, low", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ROCR.value,
            description="Fetch rate of change ratio",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.AROON.value,
            description="Fetch Aroon",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.AROONOSC.value,
            description="Fetch aroon oscillator",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MFI.value,
            description="Fetch money flow index",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TRIX.value,
            description="Fetch triple exponential average",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="The desired price type in the time series. Four types are supported: close, open, high, low", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ULTOSC.value,
            description="Fetch ultimate oscillator",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="timeperiod1", description="Time period 1", required=True
                ),
                types.PromptArgument(
                    name="timeperiod2", description="Time period 2", required=True
                ),
                types.PromptArgument(
                    name="timeperiod3", description="Time period 3", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.DX.value,
            description="Fetch directional movement index",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MINUS_DI.value,
            description="Fetch minus directional indicator",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.PLUS_DI.value,
            description="Fetch plus directional indicator",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MINUS_DM.value,
            description="Fetch minus directional movement",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.PLUS_DM.value,
            description="Fetch plus directional movement",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.BBANDS.value,
            description="Fetch Bollinger bands",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
                types.PromptArgument(
                    name="nbdevup", description="Nbdevup", required=True
                ),
                types.PromptArgument(
                    name="nbdevdn", description="Nbdevdn", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MIDPOINT.value,
            description="Fetch midpoint",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.MIDPRICE.value,
            description="Fetch midprice",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.SAR.value,
            description="Fetch parabolic SAR",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.TRANGE.value,
            description="Fetch true range",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ATR.value,
            description="Fetch average true range",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.NATR.value,
            description="Fetch normalized average true range",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="time_period", description="Time period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.AD.value,
            description="Fetch Chaikin A/D line",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.ADOSC.value,
            description="Fetch Chaikin A/D oscillator",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="fastperiod", description="Fast period", required=True
                ),
                types.PromptArgument(
                    name="slowperiod", description="Slow period", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.OBV.value,
            description="Fetch on balance volume",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.HT_TRENDLINE.value,
            description="Fetch Hilbert transform - trendline",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.HT_SINE.value,
            description="Fetch Hilbert transform - sine wave",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
                types.PromptArgument(
                    name="series_type", description="Series type", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.HT_TRENDMODE.value,
            description="Fetch Hilbert transform - trend mode",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.HT_DCPERIOD.value,
            description="Fetch Hilbert transform - dominant cycle period",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.HT_DCPHASE.value,
            description="Fetch Hilbert transform - dominant cycle phase",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
        types.Prompt(
            name=AlphavantageTools.HT_PHASOR.value,
            description="Fetch Hilbert transform - phasor components",
            arguments=[
                types.PromptArgument(
                    name="symbol", description="Stock symbol", required=True
                ),
                types.PromptArgument(
                    name="interval", description="Interval", required=True
                ),
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(
    name: str, arguments: dict[str, str] | None = None
) -> types.GetPromptResult:
    if name == AlphavantageTools.STOCK_QUOTE.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the stock quote for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.TIME_SERIES_INTRADAY.value:
        symbol = arguments.get("symbol") if arguments else ""
        interval = arguments.get("interval") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the time series intraday for the symbol {symbol} with interval {interval}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.TIME_SERIES_DAILY.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the time series daily for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.TIME_SERIES_DAILY_ADJUSTED.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the time series daily adjusted for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.TIME_SERIES_WEEKLY.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the time series weekly for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.TIME_SERIES_WEEKLY_ADJUSTED.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the time series weekly adjusted for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.TIME_SERIES_MONTHLY.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the time series monthly for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.TIME_SERIES_MONTHLY_ADJUSTED.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the time series monthly adjusted for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.REALTIME_BULK_QUOTES.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch real time bulk quotes for the symbols {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.SYMBOL_SEARCH.value:
        keywords = arguments.get("keywords") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Search for symbols with keywords {keywords}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.MARKET_STATUS.value:
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text="Fetch the market status"
                    ),
                )
            ],
        )
    if name == AlphavantageTools.REALTIME_OPTIONS.value:
        symbol = arguments.get("symbol") if arguments else ""
        contract = arguments.get("contract") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch real time options for the symbol {symbol} with contract {contract}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.HISTORICAL_OPTIONS.value:
        symbol = arguments.get("symbol") if arguments else ""
        contract = arguments.get("contract") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch historical options for the symbol {symbol} with contract {contract}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.NEWS_SENTIMENT.value:
        tickers = arguments.get("tickers") if arguments else ""
        topics = arguments.get("topics") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch news sentiment for the tickers {tickers} with topics {topics}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.TOP_GAINERS_LOSERS.value:
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text="Fetch the top gainers and losers"
                    ),
                )
            ],
        )
    if name == AlphavantageTools.INSIDER_TRANSACTIONS.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch insider transactions for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.ANALYTICS_FIXED_WINDOW.value:
        symbol = arguments.get("symbol") if arguments else ""
        window = arguments.get("window") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch analytics with fixed window for the symbol {symbol} with window {window}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.ANALYTICS_SLIDING_WINDOW.value:
        symbol = arguments.get("symbol") if arguments else ""
        window = arguments.get("window") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch analytics with sliding window for the symbol {symbol} with window {window}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.COMPANY_OVERVIEW.value:
        symbol = arguments.get("symbol") if arguments else ""
        datatype = arguments.get("datatype") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the company overview for the symbol {symbol} with datatype {datatype}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.ETF_PROFILE.value:
        symbol = arguments.get("symbol") if arguments else ""
        datatype = arguments.get("datatype") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the ETF profile for the symbol {symbol} with datatype {datatype}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.COMPANY_DIVIDENDS.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the company dividends for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.COMPANY_SPLITS.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the company split events for the symbol {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.INCOME_STATEMENT.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the annual and quarterly income statements for the company {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.BALANCE_SHEET.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the annual and quarterly balance sheet for the company {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.CASH_FLOW.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the annual and quarterly cash flow for the company {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.COMPANY_EARNINGS.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the annual and quarterly earnings (EPS) for the company {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.LISTING_STATUS.value:
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="Fetch the list of active or delisted US stocks and ETFs",
                    ),
                )
            ]
        )
    if name == AlphavantageTools.EARNINGS_CALENDAR.value:
        symbol = arguments.get("symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the earnings expected in the next 3, 6, or 12 months for the {symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.EARNINGS_CALL_TRANSCRIPT.value:
        symbol = arguments.get("symbol") if arguments else ""
        quarter = arguments.get("quarter") if arguments else "2024Q1"
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the earnings call transcript for the {symbol} for the quarter {quarter}",
                    ),
                )
            ],
        )

    if name == AlphavantageTools.IPO_CALENDAR.value:
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="Fetch list of IPOs expected in the next 3 months",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.EXCHANGE_RATE.value:
        from_currency = arguments.get("from_currency") if arguments else ""
        to_currency = arguments.get("to_currency") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the exchange rate from {from_currency} to {to_currency}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.FX_INTRADAY.value:
        from_symbol = arguments.get("from_symbol") if arguments else ""
        to_symbol = arguments.get("to_symbol") if arguments else ""
        interval = arguments.get("interval") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the intraday exchange rate from {from_symbol} to {to_symbol} with interval {interval}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.FX_DAILY.value:
        from_symbol = arguments.get("from_symbol") if arguments else ""
        to_symbol = arguments.get("to_symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the daily exchange rate from {from_symbol} to {to_symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.FX_WEEKLY.value:
        from_symbol = arguments.get("from_symbol") if arguments else ""
        to_symbol = arguments.get("to_symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the weekly exchange rate from {from_symbol} to {to_symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.FX_MONTHLY.value:
        from_symbol = arguments.get("from_symbol") if arguments else ""
        to_symbol = arguments.get("to_symbol") if arguments else ""
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the monthly exchange rate from {from_symbol} to {to_symbol}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.CRYPTO_INTRADAY.value:
        symbol = arguments.get("symbol") if arguments else ""
        market = arguments.get("market") if arguments else ""
        interval = arguments.get("interval") if arguments else ""
        
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the intraday crypto data for {symbol} in {market} with interval {interval}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.DIGITAL_CURRENCY_DAILY.value:
        symbol = arguments.get("symbol") if arguments else ""
        market = arguments.get("market") if arguments else ""

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the daily historical time series for a digital currency (e.g., {symbol}) traded on a specific market (e.g., {market})",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.DIGITAL_CURRENCY_WEEKLY.value:
        symbol = arguments.get("symbol") if arguments else ""
        market = arguments.get("market") if arguments else ""

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the weekly historical time series for a digital currency (e.g., {symbol}) traded on a specific market, e.g., {market}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.DIGITAL_CURRENCY_MONTHLY.value:
        symbol = arguments.get("symbol") if arguments else ""
        market = arguments.get("market") if arguments else ""

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the monthly historical time series for a digital currency (e.g., {symbol}) traded on a specific market, e.g., {market}",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.WTI_CRUDE_OIL.value:
        function = arguments.get("function") if arguments else "WTI"
        interval = arguments.get("interval") if arguments else "monthly"
        datatype = arguments.get("datatype") if arguments else "json"

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the West Texas Intermediate ({function}) crude oil prices in daily, weekly, and monthly horizons",
                    ),
                )
            ],
        )

    if name == AlphavantageTools.BRENT_CRUDE_OIL.value:
        function = arguments.get("function") if arguments else "Brent"
        interval = arguments.get("interval") if arguments else "monthly"
        datatype = arguments.get("datatype") if arguments else "json"

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Fetch the {function} crude oil prices in daily, weekly, and monthly horizons",
                    ),
                )
            ],
        )
    if name == AlphavantageTools.NATURAL_GAS.value:
        function = arguments.get("function") if arguments else "NATURAL_GAS"
        interval = arguments.get("interval") if arguments else "monthly"
        datatype = arguments.get("datatype") if arguments else "json"

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="Fetch the Henry Hub natural gas spot prices in daily, weekly, and monthly horizons.",
                    )
                )
            ],
        )


    raise ValueError("Prompt implementation not found")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name=AlphavantageTools.STOCK_QUOTE.value,
            description="Fetch a stock quote",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TIME_SERIES_INTRADAY.value,
            description="Fetch a time series intraday",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "adjusted": {"type": "boolean"},
                    "outputsize": {"type": "string"},
                    "datatype": {"type": "string"},
                    "monthly": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TIME_SERIES_DAILY.value,
            description="Fetch a time series daily",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "outputsize": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TIME_SERIES_DAILY_ADJUSTED.value,
            description="Fetch a time series daily adjusted",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "outputsize": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TIME_SERIES_WEEKLY.value,
            description="Fetch a time series weekly",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TIME_SERIES_WEEKLY_ADJUSTED.value,
            description="Fetch a time series weekly adjusted",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TIME_SERIES_MONTHLY.value,
            description="Fetch a time series monthly",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TIME_SERIES_MONTHLY_ADJUSTED.value,
            description="Fetch a time series monthly adjusted",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.REALTIME_BULK_QUOTES.value,
            description="Fetch real time bulk quotes",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {"type": "array"},
                },
                "required": ["symbols"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.SYMBOL_SEARCH.value,
            description="Search endpoint",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["keywords"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.MARKET_STATUS.value,
            description="Fetch market status",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name=AlphavantageTools.REALTIME_OPTIONS.value,
            description="Fetch realtime options",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                    "contract": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.HISTORICAL_OPTIONS.value,
            description="Fetch historical options",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                    "contract": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.NEWS_SENTIMENT.value,
            description="Fetch news sentiment",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {"type": "array"},
                    "topics": {"type": "string"},
                    "time_from": {"type": "string"},
                    "time_to": {"type": "string"},
                    "sort": {"type": "string"},
                    "limit": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["tickers"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TOP_GAINERS_LOSERS.value,
            description="Fetch top gainers and losers",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name=AlphavantageTools.INSIDER_TRANSACTIONS.value,
            description="Fetch insider transactions",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ANALYTICS_FIXED_WINDOW.value,
            description="Fetch analytics fixed window",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {"type": "array"},
                    "interval": {"type": "string"},
                    "series_range": {"type": "string"},
                    "ohlc": {"type": "string"},
                    "calculations": {"type": "array"},
                },
                "required": ["symbols", "series_range", "interval", "calculations"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ANALYTICS_SLIDING_WINDOW.value,
            description="Fetch analytics sliding window",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {"type": "array"},
                    "interval": {"type": "string"},
                    "series_range": {"type": "string"},
                    "ohlc": {"type": "string"},
                    "window_size": {"type": "number"},
                    "calculations": {"type": "array"},
                },
                "required": [
                    "symbols",
                    "series_range",
                    "interval",
                    "calculations",
                    "window_size",
                ],
            },
        ),
        types.Tool(
            name=AlphavantageTools.COMPANY_OVERVIEW.value,
            description="Fetch company overview",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ETF_PROFILE.value,
            description="Fetch ETF profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.COMPANY_DIVIDENDS.value,
            description="Fetch company dividends",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.COMPANY_SPLITS.value,
            description="Fetch company splits",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.INCOME_STATEMENT.value,
            description="Fetch company income statement",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.BALANCE_SHEET.value,
            description="Fetch company balance sheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.CASH_FLOW.value,
            description="Fetch company cash flow",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.COMPANY_EARNINGS.value,
            description="Fetch company earnings",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"}
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.EARNINGS_CALL_TRANSCRIPT.value,
            description="Fetch the earnings call transcript for a given company in a specific quarter",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "quarter": {"type": "string"},
                },
                "required": ["symbol", "quarter"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.LISTING_STATUS.value,
            description="Fetch listing status",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "date": {"type": "string"},
                    "state": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.EARNINGS_CALENDAR.value,
            description="Fetch company earnings calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "horizon": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.IPO_CALENDAR.value,
            description="Fetch IPO calendar",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name=AlphavantageTools.EXCHANGE_RATE.value,
            description="Fetch exchange rate",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string"},
                    "to_currency": {"type": "string"},
                },
                "required": ["from_currency", "to_currency"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.FX_INTRADAY.value,
            description="Fetch FX intraday",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_symbol": {"type": "string"},
                    "to_symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "outputsize": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["from_symbol", "to_symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.FX_DAILY.value,
            description="Fetch FX daily",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_symbol": {"type": "string"},
                    "to_symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                    "outputsize": {"type": "string"},
                },
                "required": ["from_symbol", "to_symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.FX_WEEKLY.value,
            description="Fetch FX weekly",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_symbol": {"type": "string"},
                    "to_symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["from_symbol", "to_symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.FX_MONTHLY.value,
            description="Fetch FX monthly",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_symbol": {"type": "string"},
                    "to_symbol": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["from_symbol", "to_symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.CRYPTO_INTRADAY.value,
            description="Fetch crypto intraday",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "market": {"type": "string"},
                    "interval": {"type": "string"},
                    "outputsize": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "market", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.DIGITAL_CURRENCY_DAILY.value,
            description="Fetch digital currency daily",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "market": {"type": "string"},
                },
                "required": ["symbol", "market"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.DIGITAL_CURRENCY_WEEKLY.value,
            description="Fetch digital currency weekly",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "market": {"type": "string"},
                },
                "required": ["symbol", "market"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.DIGITAL_CURRENCY_MONTHLY.value,
            description="Fetch digital currency monthly",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "market": {"type": "string"},
                },
                "required": ["symbol", "market"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.WTI_CRUDE_OIL.value,
            description="Fetch WTI crude oil",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.BRENT_CRUDE_OIL.value,
            description="Fetch Brent crude oil",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.NATURAL_GAS.value,
            description="Fetch natural gas",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.COPPER.value,
            description="Fetch copper",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ALUMINUM.value,
            description="Fetch aluminum",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.WHEAT.value,
            description="Fetch wheat",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.CORN.value,
            description="Fetch corn",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.COTTON.value,
            description="Fetch cotton",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.SUGAR.value,
            description="Fetch sugar",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.COFFEE.value,
            description="Fetch coffee",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ALL_COMMODITIES.value,
            description="Fetch all commodities",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.REAL_GDP.value,
            description="Fetch real GDP",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.REAL_GDP_PER_CAPITA.value,
            description="Fetch real GDP per capita",
            inputSchema={
                "type": "object",
                "properties": {
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TREASURY_YIELD.value,
            description="Fetch treasury yield",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "maturity": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.FEDERAL_FUNDS_RATE.value,
            description="Fetch federal funds rate",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.CPI.value,
            description="Fetch consumer price index",
            inputSchema={
                "type": "object",
                "properties": {
                    "interval": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.INFLATION.value,
            description="Fetch inflation",
            inputSchema={
                "type": "object",
                "properties": {
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.RETAIL_SALES.value,
            description="Fetch retail sales",
            inputSchema={
                "type": "object",
                "properties": {
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.DURABLES.value,
            description="Fetch durables",
            inputSchema={
                "type": "object",
                "properties": {
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.UNEMPLOYMENT.value,
            description="Fetch unemployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.NONFARM_PAYROLL.value,
            description="Fetch nonfarm payroll",
            inputSchema={
                "type": "object",
                "properties": {
                    "datatype": {"type": "string"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.SMA.value,
            description="Fetch simple moving average",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.EMA.value,
            description="Fetch exponential moving average",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.WMA.value,
            description="Fetch weighted moving average",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.DEMA.value,
            description="Fetch double exponential moving average",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TRIMA.value,
            description="Fetch triangular moving average",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.KAMA.value,
            description="Fetch Kaufman adaptive moving average",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
            },
        ),
        types.Tool(
            name=AlphavantageTools.MAMA.value,
            description="Fetch MESA adaptive moving average",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "series_type": {"type": "string"},
                    "fastlimit": {"type": "number"},
                    "slowlimit": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": [
                    "symbol",
                    "interval",
                    "series_type",
                    "fastlimit",
                    "slowlimit",
                ],
            },
        ),
        types.Tool(
            name=AlphavantageTools.VWAP.value,
            description="Fetch volume weighted average price",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.T3.value,
            description="Fetch triple exponential moving average",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.MACD.value,
            description="Fetch moving average convergence divergence",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "series_type": {"type": "string"},
                    "fastperiod": {"type": "number"},
                    "slowperiod": {"type": "number"},
                    "signalperiod": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.MACDEXT.value,
            description="Fetch moving average convergence divergence next",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "series_type": {"type": "string"},
                    "fastperiod": {"type": "number"},
                    "slowperiod": {"type": "number"},
                    "signalperiod": {"type": "number"},
                    "fastmatype": {"type": "number"},
                    "slowmatype": {"type": "number"},
                    "signalmatype": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.STOCH.value,
            description="Fetch stochastic oscillator",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "fastkperiod": {"type": "number"},
                    "slowkperiod": {"type": "number"},
                    "slowdperiod": {"type": "number"},
                    "slowkmatype": {"type": "string"},
                    "slowdmatype": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.STOCHF.value,
            description="Fetch stochastic oscillator fast",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "fastkperiod": {"type": "number"},
                    "fastdperiod": {"type": "number"},
                    "fastdmatype": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.RSI.value,
            description="Fetch relative strength index",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.STOCHRSI.value,
            description="Fetch stochastic relative strength index",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "fastkperiod": {"type": "number"},
                    "fastdperiod": {"type": "number"},
                    "fastdmatype": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.WILLR.value,
            description="Fetch williams percent range",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ADX.value,
            description="Fetch average directional movement index",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ADXR.value,
            description="Fetch average directional movement index rating",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.APO.value,
            description="Fetch absolute price oscillator",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "series_type": {"type": "string"},
                    "fastperiod": {"type": "number"},
                    "slowperiod": {"type": "number"},
                    "matype": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [
                    "symbol",
                    "interval",
                    "series_type",
                    "fastperiod",
                    "slowperiod",
                ],
            },
        ),
        types.Tool(
            name=AlphavantageTools.PPO.value,
            description="Fetch percentage price oscillator",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "series_type": {"type": "string"},
                    "fastperiod": {"type": "number"},
                    "slowperiod": {"type": "number"},
                    "matype": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": [
                    "symbol",
                    "interval",
                    "series_type",
                    "fastperiod",
                    "slowperiod",
                ],
            },
        ),
        types.Tool(
            name=AlphavantageTools.MOM.value,
            description="Fetch momentum",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.BOP.value,
            description="Fetch balance of power",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.CCI.value,
            description="Fetch commodity channel index",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.CMO.value,
            description="Fetch chande momentum oscillator",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ROC.value,
            description="Fetch rate of change",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ROCR.value,
            description="Fetch rate of change ratio",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.AROON.value,
            description="Fetch aroon",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.AROONOSC.value,
            description="Fetch aroon oscillator",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.MFI.value,
            description="Fetch money flow index",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TRIX.value,
            description="Fetch triple exponential average",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ULTOSC.value,
            description="Fetch ultimate oscillator",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "timeperiod1": {"type": "number"},
                    "timeperiod2": {"type": "number"},
                    "timeperiod3": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": [
                    "symbol",
                    "interval",
                    "timeperiod1",
                    "timeperiod2",
                    "timeperiod3",
                ],
            },
        ),
        types.Tool(
            name=AlphavantageTools.DX.value,
            description="Fetch directional movement index",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.MINUS_DI.value,
            description="Fetch minus directional indicator",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.PLUS_DI.value,
            description="Fetch plus directional indicator",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.MINUS_DM.value,
            description="Fetch minus directional movement",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.PLUS_DM.value,
            description="Fetch plus directional movement",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.BBANDS.value,
            description="Fetch bollinger bands",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "nbdevup": {"type": "number"},
                    "nbdevdn": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": [
                    "symbol",
                    "interval",
                    "time_period",
                    "series_type",
                    "nbdevup",
                    "nbdevdn",
                ],
            },
        ),
        types.Tool(
            name=AlphavantageTools.MIDPOINT.value,
            description="Fetch midpoint",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.MIDPRICE.value,
            description="Fetch midprice",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.SAR.value,
            description="Fetch parabolic sar",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "acceleration": {"type": "number"},
                    "maximum": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TRANGE.value,
            description="Fetch true range",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ATR.value,
            description="Fetch average true range",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.NATR.value,
            description="Fetch normalized average true range",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "time_period": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "time_period"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.AD.value,
            description="Fetch accumulation/distribution line",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.ADOSC.value,
            description="Fetch accumulation/distribution oscillator",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "fastperiod": {"type": "number"},
                    "slowperiod": {"type": "number"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "fastperiod", "slowperiod"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.OBV.value,
            description="Fetch on balance volume",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.HT_TRENDLINE.value,
            description="Fetch hilbert transform - trendline",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.HT_SINE.value,
            description="Fetch hilbert transform - sine wave",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval", "series_type"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.HT_TRENDMODE.value,
            description="Fetch hilbert transform - trend mode",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.HT_DCPERIOD.value,
            description="Fetch hilbert transform - dominant cycle period",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "series_type": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.HT_DCPHASE.value,
            description="Fetch hilbert transform - dominant cycle phase",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.HT_PHASOR.value,
            description="Fetch hilbert transform - phasor components",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "interval": {"type": "string"},
                    "month": {"type": "string"},
                    "datatype": {"type": "string"},
                },
                "required": ["symbol", "interval"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    try:
        match name:
            case AlphavantageTools.STOCK_QUOTE.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                datatype = arguments.get("datatype", "json")
                result = await fetch_quote(symbol, datatype)

            case AlphavantageTools.TIME_SERIES_INTRADAY.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                datatype = arguments.get("datatype", "json")
                adjusted = arguments.get("adjusted", True)
                extended_hours = arguments.get("extended_hours", True)
                outputsize = arguments.get("outputsize", "compact")
                month = arguments.get("month", None)

                result = await fetch_intraday(
                    symbol,
                    interval,
                    datatype,
                    extended_hours,
                    adjusted,
                    outputsize,
                    month,
                )
            case AlphavantageTools.TIME_SERIES_DAILY.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                datatype = arguments.get("datatype", "json")
                outputsize = arguments.get("outputsize", "compact")

                result = await fetch_time_series_daily(symbol, datatype, outputsize)
            case AlphavantageTools.TIME_SERIES_DAILY_ADJUSTED.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                datatype = arguments.get("datatype", "json")
                outputsize = arguments.get("outputsize", "compact")

                result = await fetch_time_series_daily_adjusted(
                    symbol, datatype, outputsize
                )
            case AlphavantageTools.TIME_SERIES_WEEKLY.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                datatype = arguments.get("datatype", "json")

                result = await fetch_time_series_weekly(symbol, datatype)
            case AlphavantageTools.TIME_SERIES_WEEKLY_ADJUSTED.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                datatype = arguments.get("datatype", "json")

                result = await fetch_time_series_weekly_adjusted(symbol, datatype)
            case AlphavantageTools.TIME_SERIES_MONTHLY.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                datatype = arguments.get("datatype", "json")

                result = await fetch_time_series_monthly(symbol, datatype)
            case AlphavantageTools.TIME_SERIES_MONTHLY_ADJUSTED.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                datatype = arguments.get("datatype", "json")

                result = await fetch_time_series_monthly_adjusted(symbol, datatype)

            case AlphavantageTools.REALTIME_BULK_QUOTES.value:
                symbols = arguments.get("symbols")
                if not symbols:
                    raise ValueError("Missing required argument: symbols")

                datatype = arguments.get("datatype", "json")
                result = await fetch_realtime_bulk_quotes(symbols, datatype)

            case AlphavantageTools.SYMBOL_SEARCH.value:
                keywords = arguments.get("keywords")
                if not keywords:
                    raise ValueError("Missing required argument: keywords")

                datatype = arguments.get("datatype", "json")
                result = await search_endpoint(keywords, datatype)

            case AlphavantageTools.MARKET_STATUS.value:
                result = await fetch_market_status()

            case AlphavantageTools.REALTIME_OPTIONS.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                datatype = arguments.get("datatype", "json")
                contract = arguments.get("contract", "all")
                result = await fetch_realtime_options(symbol, datatype, contract)

            case AlphavantageTools.HISTORICAL_OPTIONS.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                datatype = arguments.get("datatype", "json")
                contract = arguments.get("contract", "all")
                result = await fetch_historical_options(symbol, datatype, contract)

            case AlphavantageTools.NEWS_SENTIMENT.value:
                tickers = arguments.get("tickers", [])
                datatype = arguments.get("datatype", "json")
                topics = arguments.get("topics", None)
                time_from = arguments.get("time_from", None)
                time_to = arguments.get("time_to", None)
                sort = arguments.get("sort", "LATEST")
                limit = arguments.get("limit", 50)

                result = await fetch_news_sentiment(
                    tickers, datatype, topics, time_from, time_to, sort, limit
                )

            case AlphavantageTools.TOP_GAINERS_LOSERS.value:
                result = await fetch_top_gainer_losers()

            case AlphavantageTools.INSIDER_TRANSACTIONS.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                result = await fetch_insider_transactions(symbol)

            case AlphavantageTools.ANALYTICS_FIXED_WINDOW.value:
                symbols = arguments.get("symbols")
                interval = arguments.get("interval")
                series_range = arguments.get("series_range")
                ohlc = arguments.get("ohlc", "close")
                calculations = arguments.get("calculations")

                if not symbols or not interval or not series_range or not calculations:
                    raise ValueError(
                        "Missing required arguments: symbols, interval, series_range, calculations"
                    )
                result = await fetch_analytics_fixed_window(
                    symbols, interval, series_range, ohlc, calculations
                )

            case AlphavantageTools.ANALYTICS_SLIDING_WINDOW.value:
                symbols = arguments.get("symbols")
                interval = arguments.get("interval")
                series_range = arguments.get("series_range")
                ohlc = arguments.get("ohlc", "close")
                window_size = arguments.get("window_size")
                calculations = arguments.get("calculations", [])

                if (
                    not symbols
                    or not interval
                    or not series_range
                    or not calculations
                    or not window_size
                ):
                    raise ValueError(
                        "Missing required arguments: symbols, interval, series_range, calculations, window_size"
                    )
                result = await fetch_analytics_sliding_window(
                    symbols, series_range, ohlc, interval, interval, calculations
                )

            case AlphavantageTools.COMPANY_OVERVIEW.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                result = await fetch_company_overview(symbol)

            case AlphavantageTools.ETF_PROFILE.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                result = await fetch_etf_profile(symbol)

            case AlphavantageTools.COMPANY_DIVIDENDS.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                result = await company_dividends(symbol)

            case AlphavantageTools.COMPANY_SPLITS.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                result = await fetch_company_splits(symbol)

            case AlphavantageTools.INCOME_STATEMENT.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                result = await fetch_income_statement(symbol)
            case AlphavantageTools.BALANCE_SHEET.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                result = await fetch_balance_sheet(symbol)

            case AlphavantageTools.CASH_FLOW.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")

                result = await fetch_cash_flow(symbol)

            case AlphavantageTools.COMPANY_EARNINGS.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")
                result = await fetch_earnings(symbol)

            case AlphavantageTools.LISTING_STATUS.value:
                date = arguments.get("date")
                state = arguments.get("state")
                result = await fetch_listing_status(date, state)

            case AlphavantageTools.EARNINGS_CALENDAR.value:
                symbol = arguments.get("symbol")
                horizon = arguments.get("horizon")

                result = await fetch_earnings_calendar(symbol, horizon)

            case AlphavantageTools.EARNINGS_CALL_TRANSCRIPT.value:
                symbol = arguments.get("symbol")
                quarter = arguments.get("quarter")

                result = await fetch_earnings_call_transcript(symbol, quarter)

            case AlphavantageTools.IPO_CALENDAR.value:
                result = await fetch_ipo_calendar()

            case AlphavantageTools.EXCHANGE_RATE.value:
                from_currency = arguments.get("from_currency")
                to_currency = arguments.get("to_currency")

                if not from_currency or not to_currency:
                    raise ValueError(
                        "Missing required arguments: from_currency, to_currency"
                    )

                result = await fetch_exchange_rate(from_currency, to_currency)

            case AlphavantageTools.FX_INTRADAY.value:
                from_symbol = arguments.get("from_symbol")
                to_symbol = arguments.get("to_symbol")
                interval = arguments.get("interval")
                outputsize = arguments.get("outputsize", "compact")
                datatype = arguments.get("datatype", "json")

                if not from_symbol or not to_symbol or not interval:
                    raise ValueError(
                        "Missing required arguments: from_symbol, to_symbol, interval"
                    )

                result = await fetch_fx_intraday(
                    from_symbol, to_symbol, interval, outputsize, datatype
                )

            case AlphavantageTools.FX_DAILY.value:
                from_symbol = arguments.get("from_symbol")
                to_symbol = arguments.get("to_symbol")
                datatype = arguments.get("datatype", "json")
                outputsize = arguments.get("outputsize", "compact")

                if not from_symbol or not to_symbol:
                    raise ValueError(
                        "Missing required arguments: from_symbol, to_symbol"
                    )

                result = await fetch_fx_daily(
                    from_symbol, to_symbol, datatype, outputsize
                )

            case AlphavantageTools.FX_WEEKLY.value:
                from_symbol = arguments.get("from_symbol")
                to_symbol = arguments.get("to_symbol")
                datatype = arguments.get("datatype", "json")

                if not from_symbol or not to_symbol:
                    raise ValueError(
                        "Missing required arguments: from_symbol, to_symbol"
                    )

                result = await fetch_fx_weekly(from_symbol, to_symbol, datatype)

            case AlphavantageTools.FX_MONTHLY.value:
                from_symbol = arguments.get("from_symbol")
                to_symbol = arguments.get("to_symbol")
                datatype = arguments.get("datatype", "json")

                if not from_symbol or not to_symbol:
                    raise ValueError(
                        "Missing required arguments: from_symbol, to_symbol"
                    )

                result = await fetch_fx_monthly(from_symbol, to_symbol, datatype)

            case AlphavantageTools.CRYPTO_INTRADAY.value:
                symbol = arguments.get("symbol")
                market = arguments.get("market")
                interval = arguments.get("interval")
                outputsize = arguments.get("outputsize", "compact")
                datatype = arguments.get("datatype", "json")

                if not symbol or not market or not interval:
                    raise ValueError(
                        "Missing required arguments: symbol, market, interval"
                    )

                result = await fetch_digital_currency_intraday(
                    symbol, market, interval, datatype, outputsize
                )

            case AlphavantageTools.DIGITAL_CURRENCY_DAILY.value:
                symbol = arguments.get("symbol")
                market = arguments.get("market")

                if not symbol or not market:
                    raise ValueError("Missing required arguments: symbol, market")

                result = await fetch_digital_currency_daily(symbol, market)

            case AlphavantageTools.DIGITAL_CURRENCY_WEEKLY.value:
                symbol = arguments.get("symbol")
                market = arguments.get("market")

                if not symbol or not market:
                    raise ValueError("Missing required arguments: symbol, market")

                result = await fetch_digital_currency_daily(symbol, market)

            case AlphavantageTools.DIGITAL_CURRENCY_MONTHLY.value:
                symbol = arguments.get("symbol")
                market = arguments.get("market")

                if not symbol or not market:
                    raise ValueError("Missing required arguments: symbol, market")

                result = await fetch_digital_currency_monthly(symbol, market)

            case AlphavantageTools.WTI_CRUDE_OIL.value:
                interval = arguments.get("interval", "montHly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_wti_crude(interval, datatype)

            case AlphavantageTools.BRENT_CRUDE_OIL.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_brent_crude(interval, datatype)

            case AlphavantageTools.NATURAL_GAS.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_natural_gas(interval, datatype)

            case AlphavantageTools.COPPER.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_copper(interval, datatype)

            case AlphavantageTools.ALUMINUM.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_aluminum(interval, datatype)

            case AlphavantageTools.WHEAT.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_wheat(interval, datatype)

            case AlphavantageTools.CORN.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_corn(interval, datatype)

            case AlphavantageTools.COTTON.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_cotton(interval, datatype)

            case AlphavantageTools.SUGAR.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_sugar(interval, datatype)

            case AlphavantageTools.COFFEE.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_coffee(interval, datatype)

            case AlphavantageTools.ALL_COMMODITIES.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_all_commodities(interval, datatype)

            case AlphavantageTools.REAL_GDP.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_real_gdp(interval, datatype)

            case AlphavantageTools.REAL_GDP_PER_CAPITA.value:
                datatype = arguments.get("datatype", "json")

                result = await fetch_real_gdp_per_capita(datatype)

            case AlphavantageTools.TREASURY_YIELD.value:
                interval = arguments.get("interval", "monthly")
                maturity = arguments.get("maturity", "10year")
                datatype = arguments.get("datatype", "json")

                result = await fetch_treasury_yield(interval, maturity, datatype)

            case AlphavantageTools.FEDERAL_FUNDS_RATE.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_federal_funds_rate(interval, datatype)

            case AlphavantageTools.CPI.value:
                interval = arguments.get("interval", "monthly")
                datatype = arguments.get("datatype", "json")

                result = await fetch_cpi(interval, datatype)

            case AlphavantageTools.INFLATION.value:
                datatype = arguments.get("datatype", "json")

                result = await fetch_inflation(datatype)

            case AlphavantageTools.RETAIL_SALES.value:
                datatype = arguments.get("datatype", "json")

                result = await fetch_retail_sales(datatype)

            case AlphavantageTools.DURABLES.value:
                datatype = arguments.get("datatype", "json")

                result = await fetch_durables(datatype)

            case AlphavantageTools.UNEMPLOYMENT.value:
                datatype = arguments.get("datatype", "json")

                result = await fetch_unemployment(datatype)

            case AlphavantageTools.NONFARM_PAYROLL.value:
                datatype = arguments.get("datatype", "json")

                result = await fetch_nonfarm_payrolls(datatype)

            case AlphavantageTools.SMA.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_sma(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.EMA.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_ema(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.WMA.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_wma(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.DEMA.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_dema(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.TEMA.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_tema(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.TRIMA.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_trima(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.KAMA.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_kama(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.MAMA.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_type = arguments.get("series_type")
                fastlimit = arguments.get("fastlimit")
                slowlimit = arguments.get("slowlimit")
                datatype = arguments.get("datatype", "json")

                if (
                    not symbol
                    or not interval
                    or not series_type
                    or not fastlimit
                    or not slowlimit
                ):
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type, fastlimit, slowlimit"
                    )

                result = await fetch_mama(
                    symbol, interval, month, series_type, fastlimit, slowlimit, datatype
                )

            case AlphavantageTools.VWAP.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_vwap(symbol, interval, month, datatype)

            case AlphavantageTools.T3.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_t3(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.MACD.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_type = arguments.get("series_type")
                fastperiod = arguments.get("fastperiod", 12)
                slowperiod = arguments.get("slowperiod", 26)
                signalperiod = arguments.get("signalperiod", 9)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_macd(
                    symbol,
                    interval,
                    month,
                    series_type,
                    fastperiod,
                    slowperiod,
                    signalperiod,
                    datatype,
                )
            case AlphavantageTools.MACDEXT.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_type = arguments.get("series_type")
                fastperiod = arguments.get("fastperiod", 12)
                slowperiod = arguments.get("slowperiod", 26)
                signalperiod = arguments.get("signalperiod", 9)
                fastmatype = arguments.get("fastmatype", 0)
                slowmatype = arguments.get("slowmatype", 0)
                signalmatype = arguments.get("signalmatype", 0)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_macdext(
                    symbol,
                    interval,
                    month,
                    series_type,
                    fastperiod,
                    slowperiod,
                    signalperiod,
                    fastmatype,
                    slowmatype,
                    signalmatype,
                    datatype,
                )

            case AlphavantageTools.STOCH.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                fastkperiod = arguments.get("fastkperiod", 5)
                slowkperiod = arguments.get("slowkperiod", 3)
                slowdperiod = arguments.get("slowdperiod", 3)
                slowkmatype = arguments.get("slowkmatype", 0)
                slowdmatype = arguments.get("slowdmatype", 0)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_stoch(
                    symbol,
                    interval,
                    month,
                    fastkperiod,
                    slowkperiod,
                    slowdperiod,
                    slowkmatype,
                    slowdmatype,
                    datatype,
                )

            case AlphavantageTools.STOCHF.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                fastkperiod = arguments.get("fastkperiod", 5)
                fastdperiod = arguments.get("fastdperiod", 3)
                fastdmatype = arguments.get("fastdmatype", 0)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_stochf(
                    symbol,
                    interval,
                    month,
                    fastkperiod,
                    fastdperiod,
                    fastdmatype,
                    datatype,
                )

            case AlphavantageTools.RSI.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_rsi(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.STOCHRSI.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                series_type = arguments.get("series_type")
                fastkperiod = arguments.get("fastkperiod", 5)
                fastdperiod = arguments.get("fastdperiod", 3)
                fastdmatype = arguments.get("fastdmatype", 0)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_stochrsi(
                    symbol,
                    interval,
                    month,
                    time_period,
                    series_type,
                    fastkperiod,
                    fastdperiod,
                    fastdmatype,
                    datatype,
                )

            case AlphavantageTools.WILLR.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_willr(
                    symbol, interval, month, time_period, datatype
                )

            case AlphavantageTools.ADX.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_adx(symbol, interval, month, time_period, datatype)

            case AlphavantageTools.ADXR.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_adxr(
                    symbol, interval, month, time_period, datatype
                )

            case AlphavantageTools.APO.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_type = arguments.get("series_type")
                fastperiod = arguments.get("fastperiod", 12)
                slowperiod = arguments.get("slowperiod", 26)
                matype = arguments.get("matype", 0)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_apo(
                    symbol,
                    interval,
                    month,
                    series_type,
                    fastperiod,
                    slowperiod,
                    matype,
                    datatype,
                )

            case AlphavantageTools.PPO.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_type = arguments.get("series_type")
                fastperiod = arguments.get("fastperiod", 12)
                slowperiod = arguments.get("slowperiod", 26)
                matype = arguments.get("matype", 0)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_ppo(
                    symbol,
                    interval,
                    month,
                    series_type,
                    fastperiod,
                    slowperiod,
                    matype,
                    datatype,
                )

            case AlphavantageTools.MOM.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 10)
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_mom(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.BOP.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_bop(symbol, interval, month, datatype)

            case AlphavantageTools.CCI.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 20)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_cci(symbol, interval, month, time_period, datatype)

            case AlphavantageTools.CMO.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_cmo(symbol, interval, month, time_period, datatype)

            case AlphavantageTools.ROC.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 10)
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_roc(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.ROCR.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 10)
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_rocr(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.AROON.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_aroon(
                    symbol, interval, month, time_period, datatype
                )

            case AlphavantageTools.AROONOSC.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_aroonosc(
                    symbol, interval, month, time_period, datatype
                )

            case AlphavantageTools.MFI.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_mfi(symbol, interval, month, time_period, datatype)

            case AlphavantageTools.TRIX.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 30)
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_trix(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.ULTOSC.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period1 = arguments.get("time_period1", 7)
                time_period2 = arguments.get("time_period2", 14)
                time_period3 = arguments.get("time_period3", 28)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_ultosc(
                    symbol,
                    interval,
                    month,
                    time_period1,
                    time_period2,
                    time_period3,
                    datatype,
                )

            case AlphavantageTools.DX.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_dx(symbol, interval, month, time_period, datatype)

            case AlphavantageTools.MINUS_DI.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_minus_di(
                    symbol, interval, month, time_period, datatype
                )

            case AlphavantageTools.PLUS_DI.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_plus_di(
                    symbol, interval, month, time_period, datatype
                )
            case AlphavantageTools.MINUS_DM.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_minus_dm(
                    symbol, interval, month, time_period, datatype
                )

            case AlphavantageTools.PLUS_DM.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_plus_dm(
                    symbol, interval, month, time_period, datatype
                )

            case AlphavantageTools.BBANDS.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 20)
                series_type = arguments.get("series_type")
                nbdevup = arguments.get("nbdevup", 2)
                nbdevdn = arguments.get("nbdevdn", 2)
                matype = arguments.get("matype", 0)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_bbands(
                    symbol,
                    interval,
                    month,
                    time_period,
                    series_type,
                    nbdevup,
                    nbdevdn,
                    matype,
                    datatype,
                )

            case AlphavantageTools.MIDPOINT.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period, series_type"
                    )

                result = await fetch_midpoint(
                    symbol, interval, month, time_period, series_type, datatype
                )

            case AlphavantageTools.MIDPRICE.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_midprice(
                    symbol, interval, month, time_period, datatype
                )

            case AlphavantageTools.SAR.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                acceleration = arguments.get("acceleration", 0.02)
                maximum = arguments.get("maximum", 0.2)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_sar(
                    symbol, interval, month, acceleration, maximum, datatype
                )

            case AlphavantageTools.TRANGE.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_trange(symbol, interval, month, datatype)

            case AlphavantageTools.ATR.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_atr(symbol, interval, month, time_period, datatype)

            case AlphavantageTools.NATR.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                time_period = arguments.get("time_period", 14)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not time_period:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, time_period"
                    )

                result = await fetch_natr(
                    symbol, interval, month, time_period, datatype
                )

            case AlphavantageTools.AD.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_ad(symbol, interval, month, datatype)

            case AlphavantageTools.ADOSC.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                fastperiod = arguments.get("fastperiod", 3)
                slowperiod = arguments.get("slowperiod", 10)
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_adosc(
                    symbol, interval, month, fastperiod, slowperiod, datatype
                )

            case AlphavantageTools.OBV.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_obv(symbol, interval, month, datatype)

            case AlphavantageTools.HT_TRENDLINE.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_ht_trendline(
                    symbol, interval, month, series_type, datatype
                )

            case AlphavantageTools.HT_SINE.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_type = arguments.get("series_type")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_type:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_type"
                    )

                result = await fetch_ht_sine(
                    symbol, interval, month, series_type, datatype
                )

            case AlphavantageTools.HT_TRENDMODE.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval:
                    raise ValueError("Missing required arguments: symbol, interval")

                result = await fetch_ht_trendmode(symbol, interval, month, datatype)

            case AlphavantageTools.HT_DCPERIOD.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_types = arguments.get("series_types")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_types:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_types"
                    )

                result = await fetch_ht_dcperiod(
                    symbol, interval, month, series_types, datatype
                )

            case AlphavantageTools.HT_DCPHASE.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_types = arguments.get("series_types")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_types:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_types"
                    )

                result = await fetch_ht_dcphase(
                    symbol, interval, month, series_types, datatype
                )

            case AlphavantageTools.HT_PHASOR.value:
                symbol = arguments.get("symbol")
                interval = arguments.get("interval")
                month = arguments.get("month")
                series_types = arguments.get("series_types")
                datatype = arguments.get("datatype", "json")

                if not symbol or not interval or not series_types:
                    raise ValueError(
                        "Missing required arguments: symbol, interval, series_types"
                    )

                result = await fetch_ht_phasor(
                    symbol, interval, month, series_types, datatype
                )
            case _:
                raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        raise ValueError(f"Error processing alphavantage query: {str(e)}") from e


def get_version():
    from importlib.metadata import version
    return version("alphavantage")


async def run_stdio_server():
    """Run the MCP stdio server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="alphavantage",
                server_version=get_version(),
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


async def run_streamable_http_server(port=8080):
    """Run the Streamable HTTP server on the specified port"""
    transport = StreamableHTTPServerTransport(mcp_session_id=None, is_json_response_enabled=True)

    async with transport.connect() as (read_stream, write_stream):
        server_task = asyncio.create_task(
            server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="alphavantage",
                    server_version=get_version(),
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
        )
        # Create ASGI app wrapper for the transport
        async def asgi_app(scope, receive, send):
            if scope["type"] == "http" and scope["path"].startswith("/mcp"):
                await transport.handle_request(scope, receive, send)
            else:
                await send({
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [[b"content-type", b"text/plain"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Not Found",
                })
        
        config = uvicorn.Config(asgi_app, host="localhost", port=port)
        uvicorn_server = uvicorn.Server(config)
        http_task = asyncio.create_task(uvicorn_server.serve())

        await asyncio.gather(server_task, http_task)

async def main(server_type='stdio', port=8080):
    """Main entry point with server type selection"""
    if server_type == 'http':
        print(f"Starting Streamable HTTP server on port {port}")
        await run_streamable_http_server(port=port)
    else:
        print("Starting stdio server")
        await run_stdio_server()
