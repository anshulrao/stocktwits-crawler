#!/usr/bin/env python3

"""
Download streams/tweets of stocks/symbols from StockTwits.

Usage:
1. Get the top 1000 latest streams of a symbol:-
    > python3 stocktwits_crawler.py latest AA 1000

2. Get the streams for a symbol b/w two dates:-
    > python3 stocktwits_crawler.py history AA 2022-07-10 2022-07-12

    NOTE: The later the start_date, the more the time taken since this
    program reads the tweets backwards.

3. Get the streams for a symbol b/w two dates going back from a specific id:-
    > python3 stocktwits_crawler.py history AA 2018-01-01 2018-12-31 175000000

    NOTE: By controlling the id, we can reduce the time taken for the script
    to execute for older time periods.


Author: Anshul Rao (@anshulrao)

"""

from datetime import datetime
import json
import logging
import pandas as pd
import requests
import sys
import time
import warnings

URL = f"https://api.stocktwits.com/api/2/streams/symbol/%s.json"


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
            'message_id': [],
            'date': []
        }

    for message in data['messages']:
        tweets['text'].append(message['body'])
        tweets['created_at'].append(message['created_at'])
        try:
            tweets['bear_bull_tag'].append(
                message['entities']['sentiment']['basic']
                )
        except TypeError:
            tweets['bear_bull_tag'].append("NIL")
        tweets['user_name'].append(message['user']['username'])
        tweets['user_id'].append(message['user']['id'])
        tweets['message_id'].append(message['id'])
        tweets['date'].append(int(datetime.strptime(
            message['created_at'],'%Y-%m-%dT%H:%M:%SZ'
            ).strftime('%Y%m%d')))

    return tweets


def get_streams(symbol, start_dt, end_dt, max_id=None):
    """
    :param symbol: stock symbol like ETH, BTC, etc.
    :param start_dt: start date of streams.
    :param end_dt: end date of streams.
    :return: dataframe with streams for the given 'symbol' in
             the given time range, i.e., between 'start_date' and
             'end_date'.

    """
    url = URL % symbol
    if max_id is not None:
        response = requests.get(url + f"?max={max_id}")
    else:
        response = requests.get(url)

    data = json.loads(response.text)
    tweets = read_messages(data, None)

    while tweets is None or min(tweets['date']) >= int(start_dt):
        max_id = data['cursor']['since']
        if max_id is None:
            break
        new_url = url + f"?max={max_id}"
        try:
            response = requests.get(new_url)
            try:
                data = json.loads(response.text)
                tweets = read_messages(data, tweets)
            except json.decoder.JSONDecodeError:
                logging.warning(f"{new_url} JSON response could not be decoded.")
                warnings.warn(f"{new_url} JSON response could not be decoded.")
                time.sleep(5)
        except requests.exceptions.ProxyError:
            print(f"{new_url} throwing proxy error. Sleeping for sometime.")
            time.sleep(600)
        except requests.exceptions.SSLError:
            print(f"{new_url} throwing SSL error. Sleeping for sometime.")
            time.sleep(600)
        if tweets is not None and min(tweets['date']) > int(end_dt):
            tweets = None

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
        # we'll go back from the latest url every time using 'max' to get
        # latest tweets.
        new_url = url + f"?max={data['cursor']['since']}"
        response = requests.get(new_url)
        try:
            data = json.loads(response.text)
            tweets = read_messages(data, tweets)
        except json.decoder.JSONDecodeError:
            logging.warning(f"{new_url} JSON response could not be decoded.")
            warnings.warn(f"{new_url} JSON response could not be decoded.")

    df = pd.DataFrame(tweets)
    df.drop_duplicates(inplace=True)
    df.drop(columns=["date"], inplace=True)

    return df


def main():
    """
    The main function.

    """
    start_time = time.time()
    option = sys.argv[1]
    if option == "history":
        if len(sys.argv) == 6:
            symbol, start_date, end_date, max_id = \
                sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
        else:
            symbol, start_date, end_date = \
                sys.argv[2], sys.argv[3], sys.argv[4]
            max_id = None
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')
        logging.basicConfig(filename=f'{symbol}_{start_dt}_{end_dt}.log',
                            filemode="a",
                            level=logging.DEBUG)
        df = get_streams(symbol, start_dt, end_dt, max_id)
        df.to_csv(f"{symbol}_{start_dt}_{end_dt}.csv.gz",
                  compression='gzip',
                  index=False)
        logging.info(f"Execution took {time.time() - start_time} seconds.")
    elif option == 'latest':
        symbol, count = sys.argv[2], int(sys.argv[3])
        df = get_latest_streams(symbol, count)
        df.to_csv(f"data/latest/{symbol}_{count}.csv", index=False)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
