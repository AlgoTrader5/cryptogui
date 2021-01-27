Currently a WIP.

# cryptogui
PyQt5 application to display near real-time bid ask data fed from cryptostore/cryptofeed. 

*Snippets of code have been inspired by EliteQuant_Python project

To run:

1) Install Bryant Moscon's cryptostore from github

2) Run cryptostore using the config.yaml in this (cryptogui) repository and ensure the following: ZMQ pass through is enabled and delta=False for L2 book.

3) Open new terminal and change into this cryptogui root folder.

4) Run start.bat

Features to be added:
- display funding rates on perpetuals
- display options chains
- display futures (all expirys)
- display trade blotter
- simulate RFQ (request for quote) to buy X amount of BTC-USD (considering fees and depth/slippage)
