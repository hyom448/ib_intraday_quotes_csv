from typing import Dict, List

from ib_insync import *
# util.startLoop()  # uncomment this line when in a notebook
logger = None  # see logger_configuration() for global variable initialisation


# configure logger to log to file and print out to console
def logger_configuration() -> None:
    import os
    import logging

    global logger  # make global so that logger can be accessed outside function

    # https://docs.python.org/3/howto/logging-cookbook.html
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    # log to file at ../log/(script_filename).log
    fh = logging.FileHandler(os.getcwd() + "/log/" + os.path.basename(__file__) + ".log")

    # add timestop automatically to log file
    fh.setLevel(level=logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    return None


# clean 'volume' column
def clean_volume_column(volume_str: str) -> str:
    volume = float(volume_str)
    output = volume
    if volume < 0:
        output = 0
    else:
        output = volume

    return str(output)


# transform downloaded intraday data from ib into format that can be imported by Amibroker as csv files
# df is the dataframe that contains the downloaded data
# fullname_value is value for column "FullName"
# ticker_value is value for column "Ticker"
# return transformed dataframe
def transform_intraday_ib(df, fullname_value: str, ticker_value: str):
    # import os

    # ensure df contains valid columns
    assert (('open' in df) and ('close' in df) and ('high' in df) and ('low' in df))
    # assert (['open', 'close', 'high', 'low'] in df)
    full_name = fullname_value
    ticker = ticker_value

    df["full_name"] = full_name
    df["ticker"] = ticker

    # split existing date column into 2 columns Date_YMD, TIME
    df['date'] = df['date'].astype(str)  # convert to string first to use .str()
    df[['Date_YMD', 'TIME']] = df['date'].str.split(' ', n=1, expand=True)
    # drop unwanted columns.
    df = df.drop(["date", "barCount", "average"], axis='columns')
    # shift column order
    df = df[['full_name', 'ticker', 'Date_YMD', 'TIME', 'open', 'high', 'low', 'close', 'volume']]
    # transform Date_YMD from 2017-04-18 to 20170418
    df['Date_YMD'] = df['Date_YMD'].str.replace("-", "")
    # clean 'volume' column. Many -ve values which are nonsense. Make to minimum 0
    df['volume'] = df['volume'].apply(clean_volume_column)
    return df


# get history of symbol list to download intraday history from Interactive Brokers
# need to download 360 days of data one at a time
def get_symbol_history_list(symbol: str, bar_size: str, what_to_show: str, duration: str, fullname: str,
                            exchange="SMART", currency="USD") -> List[Dict]:
    symbol_list: List[Dict] = [
        {"Symbol": symbol, "endDateTime": "", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
        {"Symbol": symbol, "endDateTime": "20170410 06:00:00", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
        {"Symbol": symbol, "endDateTime": "20151120 08:00:00", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
        {"Symbol": symbol, "endDateTime": "20140720 08:00:00", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
        {"Symbol": symbol, "endDateTime": "20130319 08:00:00", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
        {"Symbol": symbol, "endDateTime": "20111117 08:00:00", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
        {"Symbol": symbol, "endDateTime": "20100716 08:00:00", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
        {"Symbol": symbol, "endDateTime": "20090306 08:00:00", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
        {"Symbol": symbol, "endDateTime": "20071105 08:00:00", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
        # last set of data that can be downloaded
        {"Symbol": symbol, "endDateTime": "20060705 08:00:00", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
    ]
    return symbol_list


def get_symbol_list(symbol: str, bar_size: str, what_to_show: str, duration: str, fullname: str,
                    exchange="SMART", currency="USD") -> List[Dict]:
    symbol_list: List[Dict] = [
        {"Symbol": symbol, "endDateTime": "", "durationStr": duration,
         "barSizeSetting": bar_size, "whatToShow": what_to_show, "FullName": fullname,
         "Exchange": exchange, "Currency": currency, },
    ]
    return symbol_list


# download intraday data from Interactive Brokers
# contract_type can be "forex" or "cfd"
def download_intraday_data_to_csv(symbol_list: List[Dict], contract_type: str,
                                  csv_folderpath: str, print_start_date="no") -> None:
    import traceback
    import datetime
    # import logging
    # index = 0
    # for index in range(0, 1):
    # for index in range(9, len(symbol_list)):
    for index in range(0, len(symbol_list)):
        # print(df[['date', 'open', 'high', 'low', 'close']])
        if symbol_list[index]["endDateTime"] != "":
            csv_filename = symbol_list[index]["Symbol"] + '_' + symbol_list[index]["barSizeSetting"] \
                           + '_' + symbol_list[index]["durationStr"] \
                           + '_' + symbol_list[index]["endDateTime"] \
                           + ".csv"
        elif symbol_list[index]["endDateTime"] == "":
            today_date_yyyymmdd = datetime.datetime.today().strftime('%Y-%m-%d')
            if print_start_date == "yes":
                start_date = "download" + today_date_yyyymmdd
            else:
                start_date = ""

            csv_filename = symbol_list[index]["Symbol"] + '_' + symbol_list[index]["barSizeSetting"] \
                           + '_' + symbol_list[index]["durationStr"] \
                           + '_' + start_date \
                           + ".csv"

        csv_filename = csv_filename.replace(" ", "_")
        csv_filename = csv_filename.replace(":", "_")
        csv_filepath = csv_folderpath + csv_filename

        logger.info("Downloading " + str(index) + " " + csv_filename)
        if contract_type == "forex":
            contract = Forex(symbol_list[index]["Symbol"])
        elif contract_type == "cfd":
            contract = CFD(symbol=symbol_list[index]["Symbol"],
                           exchange=symbol_list[index]["Exchange"],
                           currency=symbol_list[index]["Currency"])
        elif contract_type == "index":
            contract = Index(symbol=symbol_list[index]["Symbol"],
                             exchange=symbol_list[index]["Exchange"],
                             currency=symbol_list[index]["Currency"])
        elif contract_type == "cont_futures":
            contract = Contract(symbol=symbol_list[index]["Symbol"],
                                secType='CONTFUT',
                                exchange=symbol_list[index]["Exchange"],
                                currency=symbol_list[index]["Currency"],
                                includeExpired=True)
        else:
            raise Exception(F"invalid contract parameter {{contract}}")
        # documentation on reqHistoricalData()
        # https://interactivebrokers.github.io/tws-api/historical_bars.html
        # report traded price.
        try:
            bars = ib.reqHistoricalData(contract,
                                        endDateTime=symbol_list[index]["endDateTime"],
                                        durationStr=symbol_list[index]["durationStr"],
                                        barSizeSetting=symbol_list[index]["barSizeSetting"],
                                        whatToShow=symbol_list[index]["whatToShow"],
                                        # useRTH=True)
                                        useRTH=False)  # if use true, futures data download will be incomplete. Only during U.S hours
        except Exception as e:
            logger.info(traceback.format_exc())  # Logs the error appropriately.
            continue  # skip current iteration and move to next for-loop iteration

        df = util.df(bars)
        df_new = transform_intraday_ib(df=df,
                                       fullname_value=symbol_list[index]["FullName"],
                                       ticker_value=symbol_list[index]["Symbol"])
        df_new.to_csv(csv_filepath, index=False)
    return None


# download recent forex data in hourly bars
# contract_type : "forex", "cfd", "index"
def download_recent_intraday_data(folderpath, number_of_days: int, download_list, contract_type) -> None:
    assert type(number_of_days) == int and (0 <= number_of_days <= 360)

    bar_size = "1 hour"

    # can't show 'TRADES' for FOREX AND CFD. See https://interactivebrokers.github.io/tws-api/historical_bars.html
    if contract_type == "forex" or contract_type == 'cfd':
        what_to_show = "MIDPOINT"
    elif contract_type == "index":
        what_to_show = "TRADES"
    elif contract_type == "cont_futures":
        what_to_show = "TRADES"
    else:
        assert False

    duration = str(number_of_days) + " D"

    if contract_type == "forex":
        for index in range(0, len(download_list)):
            symbol_list = get_symbol_list(symbol=download_list[index], bar_size=bar_size,
                                          what_to_show=what_to_show,
                                          duration=duration,
                                          fullname=download_list[index]
                                          )

            download_intraday_data_to_csv(symbol_list=symbol_list, contract_type=contract_type,
                                          csv_folderpath=folderpath)
    elif contract_type == "cfd" or contract_type == "index" or contract_type == "cont_futures":
        for index in range(0, len(download_list)):
            symbol_list = get_symbol_list(symbol=download_list[index]["Symbol"], bar_size=bar_size,
                                          what_to_show=what_to_show,
                                          duration=duration,
                                          fullname=download_list[index]["FullName"],
                                          exchange=download_list[index]["Exchange"],
                                          currency=download_list[index]["Currency"]
                                          )

            download_intraday_data_to_csv(symbol_list=symbol_list, contract_type=contract_type,
                                          csv_folderpath=folderpath)
    else:
        assert False

    return None


def download_historical_intraday_data(folderpath: str, download_list: List[str], contract_type: str) -> None:
    bar_size = "1 hour"
    # can't show 'TRADES' for CFD. See https://interactivebrokers.github.io/tws-api/historical_bars.html
    # can't show 'TRADES' for FOREX AND CFD. See https://interactivebrokers.github.io/tws-api/historical_bars.html
    if contract_type == "forex":
        what_to_show = "MIDPOINT"
    elif contract_type == 'cfd':
        what_to_show = "MIDPOINT"
    elif contract_type == "index":
        what_to_show = "TRADES"
    # https://groups.io/g/insync/topic/adding_contfut_to_ib_insync/5850800?p=,,,20,0,0,0::recentpostdate%2Fsticky,,,20,2,0,5850800
    elif contract_type == "cont_futures":  # continuous futures
        what_to_show = "TRADES"
    else:
        assert False
    duration = "360 D"

    if contract_type == "forex":
        for index in range(0, len(download_list)):
            symbol_list = get_symbol_history_list(symbol=download_list[index], bar_size=bar_size,
                                                  what_to_show=what_to_show,
                                                  duration=duration,
                                                  fullname=download_list[index]
                                                  )
            download_intraday_data_to_csv(symbol_list=symbol_list, contract_type=contract_type,
                                          csv_folderpath=folderpath)
    elif contract_type == "cfd" or contract_type == "index" or contract_type == "cont_futures":
        for index in range(0, len(download_list)):
            symbol_list = get_symbol_history_list(symbol=download_list[index]["Symbol"], bar_size=bar_size,
                                                  what_to_show=what_to_show,
                                                  duration=duration,
                                                  fullname=download_list[index]["FullName"],
                                                  exchange=download_list[index]["Exchange"],
                                                  currency=download_list[index]["Currency"]
                                                  )
            download_intraday_data_to_csv(symbol_list=symbol_list, contract_type=contract_type,
                                          csv_folderpath=folderpath)

    return None


# import forex ascii file.
# database_path = folder path of amibroker database. Sample "C:/AmiB/Forex-EOD"
# filename = filepath including filename of text file containing forex data conforming to specified customized format
def import_forex_ascii(database_path: str, filename: str) -> None:
    import win32com.client
    ab = win32com.client.Dispatch("Broker.Application")
    ab.LoadDatabase(database_path)
    file_format = "ibintra.format"  # see C:\Program Files\AmiBroker\Formats\import.types
    ab.Import(0, filename, file_format)
    ab.RefreshAll()
    return None


# database_path = path of amibroker forex database Sample "C:/AmiB/Forex-EOD"
# folder_path = folder path of files containing forex eod data
def import_file_list_in_folder(database_path: str, folder_path: str) -> None:
    import os
    n = 1
    for file in os.listdir(folder_path)[:n]:
        # if file.endswith(".csv") and file.startswith("FOREX"):
        if file.endswith(".csv"):
            file_pathname = os.path.join(folder_path, file)
            import_forex_ascii(database_path=database_path, filename=file_pathname)
            print("Amibroker : importing file " + file_pathname)
    return None


forex_symbol_list: List[str] = \
    ['EURUSD', 'USDSGD', 'USDJPY', 'USDHKD', 'USDCNH', 'USDCAD', 'USDCHF', 'EURSGD', 'GBPUSD',
     'EURGBP', 'EURAUD', 'GBPUSD', 'EURGBP', 'EURAUD', 'GBPUSD', 'GBPAUD', 'AUDUSD', 'AUDSGD',
     'AUDHKD', 'AUDCNH', 'AUDJPY', 'NZDUSD', 'SGDJPY', 'SGDCNH', 'CHFJPY', 'EURCHF', 'USDKRW', 'CADJPY',
     'EURCAD', 'AUDCAD', 'GBPNZD', 'GBPSGD', 'USDCZK', 'USDDKK', 'USDHUF', 'USDILS', 'USDKRW',
     'USDMXN', 'USDNOK', 'USDPLN', 'USDRUB', 'USDSEK', 'USDTRY', 'USDZAR'
     ]

cfd_list: List[Dict] = [
    {"Symbol": 'IBUS500', "FullName": "S&P500_CFD", "Exchange": "SMART", "Currency": "USD"},
    {"Symbol": 'IBUST100', "FullName": "Nasdaq100_CFD", "Exchange": "SMART", "Currency": "USD"},
    {"Symbol": 'IBUS30', "FullName": "DowJonesIndustrialAverage_CFD", "Exchange": "SMART", "Currency": "USD"},
    {"Symbol": 'IBDE30', "FullName": "Dax30_CFD", "Exchange": "SMART", "Currency": "EUR"},
    {"Symbol": 'IBFR40', "FullName": "CAC30_CFD", "Exchange": "SMART", "Currency": "EUR"},
    {"Symbol": 'IBGB100', "FullName": "FTSE100_CFD", "Exchange": "SMART", "Currency": "GBP"},
    {"Symbol": 'IBES35', "FullName": "IBEX35_CFD", "Exchange": "SMART", "Currency": "EUR"},
    {"Symbol": 'IBCH20', "FullName": "SMI20_CFD", "Exchange": "SMART", "Currency": "CHF"},
    {"Symbol": 'IBNL25', "FullName": "AEX25_CFD", "Exchange": "SMART", "Currency": "EUR"},
    {"Symbol": 'IBEU50', "FullName": "Euronext50_CFD", "Exchange": "SMART", "Currency": "EUR"},
    {"Symbol": 'IBAU200', "FullName": "ASX200_CFD", "Exchange": "SMART", "Currency": "AUD"},
    {"Symbol": 'IBHK50', "FullName": "HangSeng50_CFD", "Exchange": "SMART", "Currency": "HKD"},
    {"Symbol": 'IBJP225', "FullName": "Nikkei225_CFD", "Exchange": "SMART", "Currency": "JPY"},
]

indices_list: List[Dict] = [
    # {"Symbol": 'STI', "FullName": "StraitsTimesIndex_Ind", "Exchange": "SGX", "Currency": "SGD"},  # no market permission
    {"Symbol": 'SPX', "FullName": "S&P500_Ind", "Exchange": "CBOE", "Currency": "USD"},
    {"Symbol": 'INDU', "FullName": "DowJonesIndustrialAverage_Ind", "Exchange": "CME", "Currency": "USD"},
    # {"Symbol": 'NDX', "FullName": "Nasdaq100_Ind", "Exchange": "NASDAQ", "Currency": "USD"},
    # {"Symbol": 'NK', "FullName": "Nikkei225_Ind", "Exchange": "CME", "Currency": "USD"},  # don't like mismatched currency
]

futures_list: List[Dict] = [
    # US futures exchanges
    {"Symbol": 'HG', "FullName": "Copper_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    {"Symbol": 'ZO', "FullName": "Oat_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'ZF', "FullName": "5_year_treasury_note_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'ZN', "FullName": "10_year_treasury_note_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'ZB', "FullName": "30_year_treasury_bond_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'YM', "FullName": "Dow_Jones_Industrial_Average_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'EMD', "FullName": "S&P_MidCap_400_Mini_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'ES', "FullName": "S&P_500_Mini_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'NQ', "FullName": "Nasdaq_100_mini_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'NKD', "FullName": "Nikkei225_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'PL', "FullName": "Platinum_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    {"Symbol": 'BZ', "FullName": "Brent_Crude_Oil_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    {"Symbol": 'CL', "FullName": "Light_sweet_crude_oil_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    {"Symbol": 'GC', "FullName": "Gold_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    {"Symbol": 'ZT', "FullName": "2_year_treasury_note_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'ZQ', "FullName": "30_day_fed_funds_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    # {"Symbol": 'SI', "FullName": "Silver_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    {"Symbol": 'ZC', "FullName": "Corn_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'ZW', "FullName": "Wheat_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'ZS', "FullName": "Soybean_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'ZM', "FullName": "Soybean_meal_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'ZL', "FullName": "Soybean_oil_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'ZR', "FullName": "Rough_rice_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'NG', "FullName": "Natural_gas_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    {"Symbol": 'AC', "FullName": "Ethanol_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    {"Symbol": 'BRR', "FullName": "Bitcoin_FUT", "Exchange": "CMECRYPTO", "Currency": "USD"},
    {"Symbol": 'AUD', "FullName": "AUDUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'JPY', "FullName": "JPYUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'EUR', "FullName": "EURUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'GBP', "FullName": "GBPUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'CAD', "FullName": "CADUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'NZD', "FullName": "NZDUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'MXP', "FullName": "MXPUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'RUR', "FullName": "RURUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'BRE', "FullName": "BREUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'ZAR', "FullName": "ZARUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'SEK', "FullName": "SEKUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'NOK', "FullName": "NOKUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'NZD', "FullName": "NZDUSD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'SIR', "FullName": "Indian_rupee_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'CHF', "FullName": "CHF_USD_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'IXB', "FullName": "Materials_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'IXE', "FullName": "Energy_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'IXI', "FullName": "Industrial_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'IXM', "FullName": "Financial_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'IXR', "FullName": "Consumer_Staples_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'IXT', "FullName": "Technology_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'IXU', "FullName": "Utilities_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    # {"Symbol": 'IXV', "FullName": "HealthCare_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'IXY', "FullName": "Consumer_Discretionary_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'IXRE', "FullName": "Real_Estate_Select_Sector_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'GF', "FullName": "Feeder_Cattle_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    {"Symbol": 'HE', "FullName": "Lean_Hogs_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    # Futures symbols below sometimes do not contain downloadable data. But usually can download over weekend
    {"Symbol": 'HO', "FullName": "Heating_Oil_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    {"Symbol": 'RB', "FullName": "Gasoline_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    # {"Symbol": 'HRC', "FullName": "Coil_Steel_Hot_Rolled_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    {"Symbol": 'PA', "FullName": "Palladium_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    # {"Symbol": 'TT', "FullName": "Cotton_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    # {"Symbol": 'SMC', "FullName": "S&P_600_SmallCap_FUT", "Exchange": "GLOBEX", "Currency": "USD"},
    # {"Symbol": 'UX', "FullName": "Uranium_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    # {"Symbol": 'TIO', "FullName": "Iron_ore_FUT", "Exchange": "NYMEX", "Currency": "USD"},

    # Futures Symbols below are small and illiquid
    # {"Symbol": 'QI', "FullName": "Silver_FUT", "Exchange": "NYMEX", "Currency": "USD"},
    # {"Symbol": 'YC', "FullName": "Corn_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    # {"Symbol": 'YK', "FullName": "Soybeans_FUT", "Exchange": "ECBOT", "Currency": "USD"},
    # {"Symbol": 'QG', "FullName": "Natural_Gas_FUT", "Exchange": "NYMEX", "Currency": "USD"},

    # SGX exchange futures
    # {"Symbol": 'IU', "FullName": "USDINR_FUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'KU', "FullName": "KRWUSD_FUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'M1CNX', "FullName": "ChinaMSCI_TotalReturnFUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'MXID', "FullName": "IndonesiaMSCI_FUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'NIFTY', "FullName": "CNX_Nifty_FUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'SSG', "FullName": "Singapore_MSCI_FUT", "Exchange": "SGX", "Currency": "SGD"},
    # {"Symbol": 'STW', "FullName": "Taiwan_MSCI_FUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'XINA50', "FullName": "XinhuaA50_FUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'UC', "FullName": "USDCNH_FUT", "Exchange": "SGX", "Currency": "CNH"},
    # {"Symbol": 'US', "FullName": "USDSGD_FUT", "Exchange": "SGX", "Currency": "SGD"},
    # {"Symbol": 'MXTH', "FullName": "ThailandMSCI_FUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'MXMY', "FullName": "MalaysiaMSCI_FUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'CY', "FullName": "CNYUSD_FUT", "Exchange": "SGX", "Currency": "USD"},
    # {"Symbol": 'M3CNX', "FullName": "ChinaMSCI_FUT", "Exchange": "SGX", "Currency": "USD"},

    # Eurex exchange futures
    # {"Symbol": 'DAX', "FullName": "DAX30_FUT", "Exchange": "DTB", "Currency": "EUR"},
    # {"Symbol": 'ESTX50', "FullName": "EuroStoxx50_FUT", "Exchange": "DTB", "Currency": "EUR"},
    # {"Symbol": 'ESA', "FullName": "EuroStoxxAutoAndParts_FUT", "Exchange": "DTB", "Currency": "EUR"},
    # {"Symbol": 'ESE', "FullName": "EuroStoxxOilAndGas_FUT", "Exchange": "DTB", "Currency": "EUR"},
    # {"Symbol": 'ESI', "FullName": "EuroStoxxInsurance_FUT", "Exchange": "DTB", "Currency": "EUR"},
    # {"Symbol": 'ESM', "FullName": "EuroStoxxMedia_FUT", "Exchange": "DTB", "Currency": "EUR"},
    # {"Symbol": 'ESU', "FullName": "EuroStoxxUtilities_FUT", "Exchange": "DTB", "Currency": "EUR"},
    # {"Symbol": 'SX3P', "FullName": "Stoxx600FoodAndBeverage_FUT", "Exchange": "DTB", "Currency": "EUR"},
    # {"Symbol": 'ESF', "FullName": "EuroStoxxFinancialServices_FUT", "Exchange": "DTB", "Currency": "EUR"},  #  low signal occurrence. chart full of gaps

    # HKFE exchange futures
    # {"Symbol": 'MHI', "FullName": "HangSengInd_FUT", "Exchange": "HKFE", "Currency": "HKD"},
    # {"Symbol": 'HHI.HK', "FullName": "HSCEI_FUT", "Exchange": "HKFE", "Currency": "HKD"},
    # {"Symbol": 'VHSI', "FullName": "HangSengVolatilityInd_FUT", "Exchange": "HKFE", "Currency": "HKD"},
    # {"Symbol": 'HB3', "FullName": "Hibor3mth_FUT", "Exchange": "HKFE", "Currency": "HKD"},
    # {"Symbol": 'IBOV', "FullName": "BovespaInd_FUT", "Exchange": "HKFE", "Currency": "HKD"},
    # {"Symbol": 'INDEXCF', "FullName": "MicexInd_FUT", "Exchange": "HKFE", "Currency": "HKD"},

    # not downloaded because of inconvenient currency
    # {"Symbol": 'NIY', "FullName": "Nikkei225_FUT", "Exchange": "GLOBEX", "Currency": "JPY"},
]

logger_configuration()

ib = IB()
ib_live_trading_api_port_number = 7496  # live trading account
ib_paper_trading_api_port_number = 7498  # paper trading account
# ib_api_port_number = ib_paper_trading_api_port_number
ib_api_port_number = ib_live_trading_api_port_number
if ib_api_port_number == ib_live_trading_api_port_number:
    ib.connect('127.0.0.1', ib_api_port_number, clientId=1, readonly=True)
elif ib_api_port_number == ib_paper_trading_api_port_number:
    ib.connect('127.0.0.1', ib_api_port_number, clientId=1, readonly=False)
else:
    ib.connect('127.0.0.1', ib_api_port_number, clientId=1, readonly=True)

# Uncomment to download recent intraday data
amibroker_db_path = "C:/AmiB/Forex-Intraday-import-db"
data_folderpath = "./data/recent/"
historical_data_folderpath = "./data/"
# for some reason, if use <25 days download, some SGX futures symbol will fail to download. Need to lengthen to 30 days.
# For some futures like MXTH, MXMY, need to lengthen to 70
# days_to_download = 30
# days_to_download = 70
days_to_download = 5

download_recent_intraday_data(folderpath=data_folderpath, number_of_days=days_to_download,
                              download_list=cfd_list, contract_type="cfd")
download_recent_intraday_data(folderpath=data_folderpath, number_of_days=days_to_download,
                              download_list=forex_symbol_list, contract_type="forex")
download_recent_intraday_data(folderpath=data_folderpath, number_of_days=days_to_download,
                              download_list=futures_list, contract_type="cont_futures")

# download_recent_intraday_data(folderpath=data_folderpath, number_of_days=days_to_download,
#                               download_list=indices_list, contract_type="index")

# Uncomment to download historical intraday data. Go back to multi-year data
# data_folderpath = "./data/historical/"
# download_historical_intraday_data(contract_type="forex", folderpath=historical_data_folderpath,
#                                   download_list=forex_symbol_list)
# download_historical_intraday_data(contract_type="cfd", folderpath=historical_data_folderpath, download_list=cfd_list)
# download_historical_intraday_data(contract_type="index", folderpath=historical_data_folderpath,
#                                   download_list=indices_list)
# download_historical_intraday_data(contract_type="cont_futures", folderpath=historical_data_folderpath,
#                                   download_list=futures_list)
