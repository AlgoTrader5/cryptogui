import os
import sys
import argparse

from PyQt5 import QtWidgets, QtCore, QtGui

SOURCE_DIR = "D:/repos/cryptogui"

sys.path.append(f"{SOURCE_DIR}/data")
from datafeed import DataFeed
from event import EventType
from live_event_engine import LiveEventEngine
from ui_market_window import MarketWindow

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

        # 1. set up gui windows
        self.central_widget = None
        self.setGeometry(50, 50, 600, 400)
        self.setWindowTitle('Cryptogui')
        self.setFont(QtGui.QFont("Helvetica [Cronyx]", 12))
        self.init_central_area()

        self.event_engine.register_handler(EventType.TICK, self._tick_event_handler)
        self.event_engine.start()

        self.data_feed.start()

    
    def _tick_event_handler(self, t):
        self.market_window.tick_signal.emit(t)


    def init_central_area(self):
        self.central_widget = QtWidgets.QWidget()
        #-------------------------------- Top Left ------------------------------------------#
        topleft = MarketWindow(subscriptions=self.config)
        self.market_window = topleft
        # -------------------------------- Top right ------------------------------------------#
        topright = QtWidgets.QWidget()
        
        splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(topleft)
        splitter1.addWidget(topright)
        splitter1.setSizes([700,450])
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(splitter1)
        main_layout = QtWidgets.QHBoxLayout()
        win = QtWidgets.QWidget()
        win.setLayout(main_layout)
        hbox.addWidget(win)
        self.central_widget.setLayout(hbox)
        self.setCentralWidget(self.central_widget)
    

    def closeEvent(self, a0: QtGui.QCloseEvent):
        # close any running processes/threads here
        print("QtGui.QCloseEvent")
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
