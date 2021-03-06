# Project Title
Price quotes download from Interactive Brokers

# Project description
This python script downloads intraday **hourly** price quotes of futures, forex, CFDs using 
Interactive Brokers(IBKR) API into csv files.

Samples of the csv files are located in folder `data/recent/ `

# Prerequisites
- Python v3.7
- [ib_insync](https://github.com/erdewit/ib_insync) python framework for Interactive Brokers(IBKR) API
- Data download of futures contracts require paid subscription to market data. 
Forex and index CFD contracts price quotes can be downloaded free of charge for 
IBKR customers. Please check with IBKR.
- TWS (Traders Workstation) desktop software needs to be configured properly. Please see
[documentation](https://interactivebrokers.github.io/tws-api/initial_setup.html). The port number in the script is to be matched with the port number set in TWS. 


This script is not affiliated with Interactive Brokers Group, Inc.'s.
