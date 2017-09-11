import logging
from pandas_datareader import data
from Utils import isVolumeHighEnough, isVolumeRaising_2, is52W_High, write_stocks_to_buy_file, gapUp


##################################
# 52 weeks high
# high volume
# volume raising the last 3 days
# volume today must be higher then AVG last days
##################################
def replaceWrongStockMarket(stockName):
    replacePatternn = [".MU", ".DE", ".SW", ".F", ".EX", ".TI", ".MI"]

    for pattern in replacePatternn:
        if pattern in stockName:
            stockName = stockName.replace(pattern, "")
            stockName = "ETR:" + stockName
            break

    return stockName


def strat_scheduler(stocksToCheck, dataProvider, Ago52W, Ago5D, Ago10D, end):
    stocksToBuy = []

    for stockName in stocksToCheck:
        readException = False

        try:
            # read data
            newStockName = replaceWrongStockMarket(stockName)
            stockName = newStockName
            stock52W = data.DataReader(stockName, dataProvider, Ago52W, end)
            stock5D = data.DataReader(stockName, dataProvider, Ago5D, end)
            stock10D = data.DataReader(stockName, dataProvider, Ago10D, end)

        except Exception as e:
            # e = sys.exc_info()[0]
            print("strat_scheduler: Data Read exception: " + str(stockName) + " is faulty: " + str(e))
            readException = True

        if not readException:
            ##############################################################
            # insert STRATEGIES here
            try:
                res = strat_52WHi_HiVolume(stockName, stock52W, stock5D, stock10D)
                if res != "":
                    stocksToBuy.append(res)
                    print ("buy: " + res)

                    # TODO canslim / Henkel

                    # TODO auswertung von chartsignalen mittels finanzen.at
                    # http://www.finanzen.net/chartsignale/index/Alle/liste/jc-1234er-long
                    ############################################################################

                res = strat_GapUp_HiVolume(stockName, stock52W, stock5D, stock10D)
                if res != "":
                    stocksToBuy.append(res)
                    print ("buy: " + res)

            except Exception as e:
                # e = sys.exc_info()[0]
                print("strat_scheduler: Strategy Exception: " + str(stockName) + " is faulty: " + str(e))

                # if "Unable to read URL" in str(e):
                # return stocksToBuy # return because google stops transfer

    return stocksToBuy


def strat_52WHi_HiVolume(stockName, stock52W, stock5D, stock10D):

    volumeRaising = False
    volumeHighEnough = False
    stockHas52Hi = False

    df = stock52W
    logging.debug(stockName)
    logging.debug(stock5D)

    volumeHighEnough = isVolumeHighEnough(stock5D)
    if volumeHighEnough:
        # TODO volumeRaising = isVolumeRaising(stock5D, stockName)
        volumeRaising = isVolumeRaising_2(stock5D, stock10D, stockName)

        if volumeRaising:
            stockHas52Hi = is52W_High(df)

    if volumeHighEnough and stockHas52Hi and volumeRaising:
        dataLen = len(stock5D)
        endKurs = stock5D.iloc[dataLen - 1].Close
        write_stocks_to_buy_file(
            str(stockName) + ", " + str(endKurs) + ", strat_52WHi_HiVolume")  # TODO überall einbauen in jede strat
        return stockName

    # else case
    return ""

def strat_GapUp_HiVolume (stockName, stock52W, stock5D, stock10D):
    volumeRaising = False
    volumeHighEnough = False

    df = stock52W
    logging.debug(stockName)
    logging.debug(stock5D)

    volumeHighEnough = isVolumeHighEnough(stock5D)
    if volumeHighEnough:
        volumeRaising = isVolumeRaising_2(stock5D, stock10D, stockName)

        if volumeRaising:
            isGapUp = gapUp(df, 1.03)

    if volumeHighEnough and isGapUp and volumeRaising:
        dataLen = len(stock5D)
        endKurs = stock5D.iloc[dataLen - 1].Close
        write_stocks_to_buy_file(
            str(stockName) + ", " + str(endKurs) + ", strat_52WHi_HiVolume")  # TODO überall einbauen in jede strat
        return stockName

    # else case
    return ""