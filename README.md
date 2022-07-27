# Download StockTwits Data

### Usage:
<br/>
1. Get the top 1000 latest streams of a symbol:-
   
   `> python3 stocktwits_streams.py latest BTC 1000`

<br/>
2. Get the streams for a symbol between two dates:-
   
   `> python3 stocktwits_streams.py history ETH 2022-07-10 2022-07-12`
   
   *NOTE: The later the start_date, the more the time taken since
   this program reads the tweets backwards.*

<br/>
3. Get the streams for a symbol between two dates going back from a specific id:-

   `> python3 stocktwits_streams.py history AAAU 2018-01-01 2018-12-31 175000000`

   *NOTE: By controlling the id, we can reduce the time taken for the script to 
   execute for older time periods.*
   
