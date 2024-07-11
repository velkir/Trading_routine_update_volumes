#Binance Data
#0.Создать blacklist.txt с стейблкоинами и непригодными активами.
#1.Запросить через ccxt данные у Binance по всем тикерам, заканчивающимся на USDT и которых нету в blacklist
#2.Если есть в таблице - обновить. Если есть в таблице, но нету в запросе - зачеркнуть ячейку и выделить красным.
#Если есть в запросе и нету в таблице - добавить
#3.Отсортировать по колонке B

#Google sheets Data
#1.Запросить список тикеров (A2:A), положить их в список

#Сопоставление списков и внесение изменений
#1.Запуск цикла for для каждого тикера из Binance Data.
#Если тикер есть в обоих списках, то обновить ячейку B
#Если тикера нету в Google sheets Data, то записать тикер в первую пустую ячейку А и записать объем в соседнюю с ней ячейку.

#НЕ РЕАЛИЗОВАНО
#Если тикер есть в Google sheets Data и нету в Binance data, то закрасить ячейку с тикером красным и зачеркнуть текст в ячейке с тикером

import gspread
import ccxt
import time
import os
from datetime import datetime

def get_blacklist(filename="blacklist.txt"):
    print("{} Getting blacklist tickers".format(current_time()))
    project_root_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(project_root_dir , filename)

    file = open(filepath, "r")
    blacklist = file.read().split("\n")
    return blacklist

def get_tickers_from_binance(exchange):
    print("{} Starting to retrieve tickers from binance".format(current_time()))
    tickers_and_volume = {}
    blacklist = get_blacklist()

    try:
        raw_data = exchange.fetch_tickers()
        for key, ticker in raw_data.items():
            if str(key).endswith("/USDT") and str(key).replace("/", "") not in blacklist:
                tickers_and_volume[key.replace("/", "")] = [int(ticker["quoteVolume"])]
    except Exception as e:
        print(f"An error occurred: {e}")
    print("{} Finished retrieving tickers from binance".format(current_time()))
    return tickers_and_volume

def get_tickers_from_spreadsheet(spreadsheet="Business", worksheet="Technical analysis routine"):
    print("{} Starting to retrieve tickers from spreadsheet".format(current_time()))
    gc = gspread.service_account()
    sh = gc.open(spreadsheet)
    worksheet = sh.worksheet(worksheet)
    tickers = worksheet.get("A2:A")
    updated_tickers = [item for row in tickers for item in row]
    print("{} Finished retrieving tickers from spreadsheet".format(current_time()))
    return updated_tickers

def check_missing_tickers(binance_list, spreadsheet_list):
    print("{} Starting to compare Binance tickers with Spreadsheet tickers.".format(current_time()))
    delisted_tickers = []
    for binance_ticker in binance_list.keys():
        if binance_ticker not in spreadsheet_list:
            spreadsheet_list.append(binance_ticker)

    for spreadsheet_ticker in spreadsheet_list:
        if spreadsheet_ticker not in binance_list.keys():
            delisted_tickers.append(spreadsheet_ticker)
    if delisted_tickers:
        print("{} Found those potentially delisted tickers:".format(current_time()))
        for delisted_ticker in delisted_tickers:
            print(delisted_ticker)
    print("{} Finished comparing Binance tickers with Spreadsheet tickers.".format(current_time()))
    return spreadsheet_list, delisted_tickers

def current_time():
    return datetime.now().strftime("%H:%M:%S")


def update_spreadsheet(binance_volume, spreadsheet_tickers, spreadsheet="Business", worksheet="Test"):
    print("{} Starting to update the spreadsheet.".format(current_time()))
    gc = gspread.service_account()
    sh = gc.open(spreadsheet)
    worksheet = sh.worksheet(worksheet)

    for i, spreadsheet_ticker in enumerate(spreadsheet_tickers):
        print("{} Updating {} ticker.".format(current_time(), spreadsheet_ticker))
        if i>=60 and i%60==0:
            time.sleep(60.5)
        value = binance_volume.get(spreadsheet_ticker)[0]
        # worksheet.update_acell(label=f"A{i + 2}", value=spreadsheet_ticker)
        worksheet.update_acell(label=f"B{i + 2}", value=value)
    print("{} Spreadsheet has been successfully updated!.".format(current_time()))


exchange = ccxt.binance()

binance_tickers = get_tickers_from_binance(exchange)
spreadsheet_tickers = get_tickers_from_spreadsheet(worksheet="Test")
spreadsheet_tickers, delisted_tickers = check_missing_tickers(binance_tickers, spreadsheet_tickers)

update_spreadsheet(binance_tickers, spreadsheet_tickers)
# print("Delisted_tickers: {}".format(delisted_tickers))