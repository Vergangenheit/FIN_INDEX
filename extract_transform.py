import pandas as pd
import numpy as np


def reduce_xrates(xrates: pd.DataFrame, tseries: pd.DataFrame):
    xrates = xrates.copy()
    timeframe = tseries.Name
    xrates = xrates[xrates.Name.isin(timeframe)].reset_index().drop("index", axis=1)

    return xrates


def trans_x(df: pd.DataFrame):
    df = df.copy()
    df["GBP_X"] = 1 / df.iloc[:, 1]
    df["EUR_X"] = 1 / df.iloc[:, 2]
    df = df.drop(df.iloc[:, [1, 2]], axis=1)

    return df


# merge exchange rates to timeseries
def merge_xrates(df: pd.DataFrame, xrates: pd.DataFrame, stocks: list, stocks_to_xc: dict()):
    df = df.copy()
    for stock in stocks:
        x = stocks_to_xc[stock]
        if x == "USD":
            df[str(stock + "_X")] = 1.0
        else:
            df[str(stock + "_X")] = xrates[str(x + "_X")]

    return df


# reorder columns
def reorder(df: pd.DataFrame, stocks: list):
    df = df.copy()
    columns_final = []
    for stock in stocks:
        cols = [col for col in df.columns if stock in col]
        for col in cols:
            columns_final.append(col)
    df = pd.concat([df["Name"], df[columns_final]], axis=1)

    return df


# convert free float
def transf_ff(df: pd.DataFrame):
    df = df.copy()
    ff_cols = [col for col in df.columns if "FREE FLOAT NOSH" in col]
    for col in ff_cols:
        df[col] /= 100

    return df


# CALCULATE FREE FLOAT MARKET CAPITALIZATION(Mt)
def market_cap(df: pd.DataFrame, stocks: list):
    df = df.copy()
    for stock in stocks:
        cols = [col for col in df.columns if stock in col]
        df[str("M_" + stock)] = df[cols[0]] * df[cols[1]] * df[cols[2]] * df[cols[3]]

    df["M"] = df.iloc[:, -1] + df.iloc[:, -2] + df.iloc[:, -3] + df.iloc[:, -4] + df.iloc[:, -5] + df.iloc[:,
                                                                                                   -6] + df.iloc[:, -7]

    df = df.drop(df.iloc[:, -8:-1], axis=1)

    return df


# DUPLICATE AND SHIFT COLUMNS TO OBTAIN COMPARISON at t+1
def shift(df: pd.DataFrame, stocks: list):
    df = df.copy()
    for stock in stocks:
        stock_cols = [col for col in df.columns if stock in col]
        for c in stock_cols:
            df[str(c + "_t-1")] = df[c].shift(1)

    return df


# calculate deltaMC
def deltamc(df: pd.DataFrame, stocks: list):
    df = df.copy()
    for stock in stocks:
        col = []
        col.append(stock)
        col.append(str(stock + " - NUMBER OF SHARES"))
        col.append(str(stock + " - FREE FLOAT NOSH"))
        col.append(str(stock + "_X"))
        col.append(str(stock + "_t-1"))
        col.append(str(stock + " - NUMBER OF SHARES" + "_t-1"))
        col.append(str(stock + " - FREE FLOAT NOSH" + "_t-1"))
        col.append(str(stock + "_X" + "_t-1"))

        df[str(stock + "_deltaMC")] = df[col[0]] * df[col[1]] * df[col[2]] * df[col[3]] - df[col[4]] * df[col[5]] * df[
            col[6]] * df[col[7]]

    df["deltaMC"] = df.iloc[:, -1] + df.iloc[:, -2] + df.iloc[:, -3] + df.iloc[:, -4] + df.iloc[:, -5] + df.iloc[:,
                                                                                                         -6] + df.iloc[
                                                                                                               :, -7]

    df = df.drop(df.iloc[:, -8:-1], axis=1)
    df = df.drop(df.iloc[:, -29:-1], axis=1)

    return df


# def drop_duplicates(df:pd.DataFrame):
#     df = df.copy()
#     df = df.drop(df.iloc[:,-29:-1],axis=1)
#
#     return df

# calculation of final index

def calculate_divisor(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # shift FF Market capitalization(M)
    df['M_t-1'] = df['M'].shift(1)
    # initialize D
    df['D'] = np.nan
    df.loc[0, 'D'] = 1
    df['D_t-1'] = df['D'].shift(1)
    for i in df.index:
        if i + 1 <= df.index.max():
            df.loc[i + 1, 'D'] = df.loc[i + 1, 'D_t-1'] * (
                        (df.loc[i + 1, 'M_t-1'] + df.loc[i + 1, 'deltaMC']) / df.loc[i + 1, 'M_t-1'])
            df['D_t-1'] = df['D'].shift(1)

    return df


def final_index(df: pd.DataFrame)-> pd.DataFrame:
    df = df.copy()
    df["INDEX"] = df["M"] / df["D"]
    df = df.drop(['M_t-1','D_t-1'], axis=1)

    return df


def transform():
    # read ts file
    tseries = pd.read_excel("TimeSeriesData_Apr15-Apr20.xlsx")

    stocks = ["APPLE", "ALLIANZ", "GENERAL ELECTRIC", "LLOYDS BANKING GROUP", "BT GROUP", "DEUTSCHE POST",
              "JOHNSON & JOHNSON"]

    # read xrates file
    xrates = pd.read_excel("FX_EUR_GBP.xlsx")

    stocks_to_xc = {"APPLE": "USD", "ALLIANZ": "EUR", "GENERAL ELECTRIC": "USD", "LLOYDS BANKING GROUP": "GBP",
                    "BT GROUP": "GBP", "DEUTSCHE POST": "EUR", "JOHNSON & JOHNSON": "USD"}
    xrates = reduce_xrates(xrates, tseries)
    xrates = trans_x(xrates)
    tseries = merge_xrates(tseries, xrates, stocks, stocks_to_xc)
    tseries = reorder(tseries, stocks)
    tseries = transf_ff(tseries)
    tseries = market_cap(tseries, stocks)
    tseries = shift(tseries, stocks)
    tseries = deltamc(tseries, stocks)
    tseries = calculate_divisor(tseries)
    tseries = final_index(tseries)

    tseries.to_csv("tseries.csv")


if __name__ == "__main__":
    transform()
