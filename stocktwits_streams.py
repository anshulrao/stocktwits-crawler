"""
Usage:
1. Get the top 1000 latest streams of a symbol:-
   > python3 stocktwits_streams.py latest BTC 1000

2. Get the streams for a symbol between two dates:-
   > python3 stocktwits_streams.py history ETH 2022-07-10 2022-07-12
   NOTE: The later the start_date, the more the time taken since
   this program reads the tweets backwards.

"""

import requests
import json
import pandas as pd
from datetime import datetime
import sys


URL = f"https://api.stocktwits.com/api/2/streams/symbol/%s.X.json"


def read_messages(data, tweets):
    """
    Reads message(s) from the given data and returns a dictionary with
    required keys/columns.

    """
    if tweets is None:
        tweets = {
            'created_at': [],
            'user_name': [],
            'user_id': [],
            'bear_bull_tag': [],
            'text': [],
            'date': []
        }

    for message in data['messages']:
        tweets['text'].append(message['body'])
        tweets['created_at'].append(message['created_at'])
        try:
            tweets['bear_bull_tag'].append(message['entities']['sentiment']['basic'])
        except TypeError:
            tweets['bear_bull_tag'].append("NIL")
        tweets['user_name'].append(message['user']['username'])
        tweets['user_id'].append(message['user']['id'])
        tweets['date'].append(int(datetime.strptime(message['created_at'],
                                                    '%Y-%m-%dT%H:%M:%SZ').strftime('%Y%m%d')))

    return tweets


def get_streams(symbol, start_dt, end_dt):
    """
    :param symbol: stock symbol like ETH, BTC, etc.
    :param start_dt: start date of streams.
    :param end_dt: end date of streams.
    :return: dataframe with streams for the given 'symbol' in
             the given time range, i.e., between 'start_date' and
             'end_date'.

    """
    url = URL % symbol

    response = requests.get(url)
    data = json.loads(response.text)
    tweets = read_messages(data, None)

    while min(tweets['date']) >= int(start_dt):
        response = requests.get(url + f"?max={data['cursor']['since']}")
        data = json.loads(response.text)
        tweets = read_messages(data, tweets)

    df = pd.DataFrame(tweets)
    df = df[(df['date'] >= int(start_dt)) & (df['date'] <= int(end_dt))]
    df.drop_duplicates(inplace=True)
    df.drop(columns=["date"], inplace=True)

    return df


def get_latest_streams(symbol, count):
    """
    :param symbol: stock symbol like ETH, BTC, etc.
    :param count: number of streams required.
    :return: dataframe with streams for the given 'symbol'. these are
             approx. last 'count' number of streams for the given symbol.

    """
    url = URL % symbol

    response = requests.get(url)
    data = json.loads(response.text)
    tweets = read_messages(data, None)

    for i in range(count // 3):
        # making 'max' the 'since' of latest
        # we'll go back from the latest url every time using 'max' to get 1000 latest tweets.
        response = requests.get(url + f"?max={data['cursor']['since']}")
        data = json.loads(response.text)
        tweets = read_messages(data, tweets)

    df = pd.DataFrame(tweets)
    df.drop_duplicates(inplace=True)
    df.drop(columns=["date"], inplace=True)

    return df


def main():
    """
    The main function.

    """
    option = sys.argv[1]
    if option == "history":
        symbol, start_date, end_date = sys.argv[2], sys.argv[3], sys.argv[4]
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')
        df = get_streams(symbol, start_dt, end_dt)
        df.to_csv(f"data/history/{symbol}_{start_dt}_{end_dt}.csv", index=False)
    elif option == 'latest':
        symbol, count = sys.argv[2], int(sys.argv[3])
        df = get_latest_streams(symbol, count)
        df.to_csv(f"data/latest/{symbol}_{count}.csv", index=False)


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
