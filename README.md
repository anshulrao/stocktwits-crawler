# Download Cryptocurrency Data

## StockTwits

### Usage:
1. Get the top 1000 latest streams of a symbol:-
   
   `> python3 stocktwits_streams.py latest BTC 1000`

2. Get the streams for a symbol between two dates:-
   
   `> python3 stocktwits_streams.py history ETH 2022-07-10 2022-07-12`
   
   NOTE: The later the start_date, the more the time taken since
   this program reads the tweets backwards.
