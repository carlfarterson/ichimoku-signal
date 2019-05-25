# Main script for ichimoku cloud
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
%matplotlib inline

def ichimoku():

    pd.plotting.register_matplotlib_converters()

    tenkan_period = 20
    kijun_period = 60
    senkou_b_period = 120
    displacement = 30

    df = pd.read_csv('data/btc_hourly_candle_2019.csv')

    extend_df(df, displacement)
    df['price'] = df['close'].shift(1)

    make_lines(df, tenkan=tenkan_period, kijun=kijun_period)
    make_spans(df, displacement=displacement, senkou_b_period=senkou_b_period)

    df = df[1500:].reset_index(drop=True)
    intersections = find_intersections(df)
    chart(df, intersections)




# Function to extend table by the displacement
def extend_df(df, displacement):
    df['date'] = [datetime.strptime(hr, '%Y-%m-%d %H:%M:%S') for hr in df['date']]
    last_date = df['date'].at[len(df)-1]
    dates = [last_date + timedelta(hours=i+1) for i in range(displacement)]
    df = df.append({'date': dates}, ignore_index=True, sort=False)


# Tenkan (conversion line) = (highest high + highest low)/2 for the past 9 periods
# Kijun (base line) = (highest high + lowest low)/2 for the past 26 periods
def make_lines(df, **kwargs):
    for i in kwargs:
        high = df['high'].rolling(window=kwargs[i]).max()
        low = df['low'].rolling(window=kwargs[i]).min()
        df[i] = (high + low)/2


# Chikou (lagging span) = Current closing price time-shifted backwards 26 periods
# Senkou span A (leading span A) = (tenkan + kijun)/2 time-shifted forwards 26 periods
# Senkou span B (leading span B) = (highest high + lowest low)/2 for past 52 periods, shifted forwards 26 periods
def make_spans(df, displacement, senkou_b_period):
    df['chikou'] = df['close'].shift(-displacement)
    df['senkou_a'] = (df['tenkan'] + df['kijun']) / 2

    make_lines(df, senkou_b=senkou_b_period)
    df[['senkou_a', 'senkou_b']] = df[['senkou_a', 'senkou_b']].shift(displacement)


def find_intersections(df):
    cloud = df['senkou_a'] > df['senkou_b']
    current_val = cloud[0]
    intersections = []
    for i in range(1, len(cloud)):
        if cloud[i] is not current_val:
            try:
                if cloud[i + 12] is not current_val:
                    current_val = cloud[i]
                    intersections.append(i)
            except:
                pass

    return intersections


# Code to make chart
def chart(df, intersections):
    price = df['price']
    tenkan = df['tenkan']
    kijun = df['kijun']
    senkou_a = df['senkou_a']
    senkou_b = df['senkou_b']
    x = df['date']

    fig, ax = plt.subplots(figsize=(20, 20))
    plt.plot(x, senkou_a, color='green', linewidth=0.5)
    plt.plot(x, senkou_b, color='red', linewidth=0.5)
    plt.plot(x, tenkan, color='blue')
    plt.plot(x, kijun, color='maroon')
    plt.plot(x, price, color='black', linewidth=1)
    [plt.axvline(x=x[i]) for i in intersections]

    ax.set(xlabel='Date', ylabel='BTC price ($)', title='2019 BTC/USD price (Bitmex)')
    plt.rc('axes', labelsize=20)
    plt.rc('font', size=16)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45)

    # Span A > Span B == green cloud
    # Span A < Span B == red cloud
    plt.fill_between(
        x, senkou_a, senkou_b,
        where=senkou_a >= senkou_b,
        facecolor='limegreen',
        interpolate=True
    )
    plt.fill_between(
        x, senkou_a, senkou_b,
        where=senkou_a <= senkou_b,
        facecolor='salmon',
        interpolate=True
    )
    plt.legend()
    plt.show()