import os
import sys
import argparse
import aiohttp
import asyncio
import json

from PyQt5 import QtWidgets, QtCore, QtGui

# SOURCE_DIR = "D:/repos/cryptogui"
SOURCE_DIR = "C:/Users/Dos/Documents/Adam/repos/cryptogui"

sys.path.append(f"{SOURCE_DIR}/data")
from datafeed import DataFeed
from event import EventType, ResponseEvent
from live_event_engine import LiveEventEngine
from ui_market_window import MarketWindow
from deribit_options_window import DeribitOptionsWindow

sys.path.append(f"{SOURCE_DIR}/utils")
from get_subscriptions_from_config import get_subscriptions_from_config

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",   default=f"{SOURCE_DIR}/config.yaml", help='cryptostore configuration containing subscribed instruments')
    parser.add_argument("--addr", default="tcp://127.0.0.1:5678",   help='zmq connection to receive market updates')
    return parser.parse_args()


class MainWindow(QtWidgets.QMainWindow):
    '''
    config: cryptostore config

    port: zmq port for subscribed datafeed (cryptostore)
    '''
    def __init__(self, config: str, addr: str):
        super(MainWindow, self).__init__()
        self.config = config
        self.addr = addr
        self.event_engine = LiveEventEngine()
        self.data_feed = DataFeed(addr=addr, event_engine=self.event_engine)

        # self.global_loop = global_loop if global_loop else asyncio.get_event_loop()

        # 1. set up gui windows
        self.central_widget = None
        self.setGeometry(50, 50, 600, 400)
        self.setWindowTitle('Cryptogui')
        self.setFont(QtGui.QFont("Helvetica [Cronyx]", 10))
        self.init_central_area()

        self.event_engine.register_handler(EventType.TICK, self._tick_event_handler)
        self.event_engine.register_handler(EventType.QUERY, self._query_request_event_handler)
        self.event_engine.register_handler(EventType.RESPONSE, self._query_response_event_handler)
        self.event_engine.start()

        self.data_feed.start()

        
    def _tick_event_handler(self, t):
        self.market_window.tick_signal.emit(t)

    
    def _query_request_event_handler(self, e):
        print(f"query request event {e}")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.async_query(e))

    def _query_response_event_handler(self, e):
        ''' map data to correct widget based on event query_id '''
        if e.query_id == "DERIBIT_OPTIONS" and self.deribit_options_window:
            self.deribit_options_window.ticker_signal.emit(e)


    # ------------------ async requests -------------------#
    async def fetch(self, client, url):
        async with client.get(url) as response:
            http_response = await response.text()
            http_response = json.loads(http_response)
            return http_response

    async def async_query(self, e):
        async with aiohttp.ClientSession() as client:
            http_response = await self.fetch(client, e.url)
            response_event = ResponseEvent(e.query_id, http_response)
            self.event_engine.put(response_event)
    # --------------------------- END  ----------------------------#



    def init_central_area(self):
        self.central_widget = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()

        # ------------------ main widget -------------------#
        win = QtWidgets.QWidget()

        #-------------------------------- Top Left ------------------------------------------#
        topleft = MarketWindow(subscriptions=self.config)
        self.market_window = topleft
        
        # -------------------------------- Top right ------------------------------------------#
        topright = QtWidgets.QTabWidget()
        tab1 = QtWidgets.QWidget()
        tab2 = QtWidgets.QWidget()
        topright.addTab(tab1, 'Deribit Options')
        topright.addTab(tab2, 'Deribit Index')

        # TAB1
        instruments = []
        self.deribit_options_window = DeribitOptionsWindow(events_engine=self.event_engine)
        tab1_layout = QtWidgets.QVBoxLayout()
        tab1_layout.addWidget(self.deribit_options_window)
        tab1.setLayout(tab1_layout)

        # TAB2
        # self.deribit_index_window = DeribitIndexWindow()
        # tab2_layout = QtWidgets.QVBoxLayout()
        # tab2_layout.addWidget(self.deribit_index_window)
        # tab2.setLayout(tab2_layout)

        splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(topleft)
        splitter1.addWidget(topright)
        splitter1.setSizes([700,450])
        
        hbox.addWidget(splitter1)
        main_layout = QtWidgets.QHBoxLayout()
        win.setLayout(main_layout)

        hbox.addWidget(win)
        self.central_widget.setLayout(hbox)
        self.setCentralWidget(self.central_widget)
    

    def closeEvent(self, a0: QtGui.QCloseEvent):
        # close any running processes/threads here
        print("Here is a QtGui.QCloseEvent.")
        self.event_engine.stop()


        
def main():
    args = get_args()

    app = QtWidgets.QApplication([])
    try:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    except ImportError:
        pass
    
    # config = ["COINBASE-BTC-USD","COINBASE-ETH-USD","COINBASE-ETH-BTC"]
    config = get_subscriptions_from_config(args.config)

    win = MainWindow(config, args.addr)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
