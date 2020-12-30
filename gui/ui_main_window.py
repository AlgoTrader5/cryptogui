import os
import sys
import argparse

from PyQt5 import QtWidgets, QtCore, QtGui

from ui_market_window import MarketWindow

parser = argparse.ArgumentParser()
parser.add_argument("--config",   default="config.yaml", help='cryptostore configuration containing subscribed instruments')
parser.add_argument("--zmq-port", dest="zmq_port", default=5556,   help='zmq connection to receive market updates')
args = parser.parse_args()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, config: str, port: int):
        super(MainWindow, self).__init__()
        self.config = config
        self.port = port

        # 1. set up gui windows
        self.central_widget = None
        self.setGeometry(50, 50, 600, 400)
        self.setWindowTitle('ConfigUI')
        self.setFont(QtGui.QFont("Helvetica [Cronyx]", 10))
        self.init_central_area()

    
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

        
def main():
    app = QtWidgets.QApplication([])
    try:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    except ImportError:
        e
    # config = args.config
    config = ["COINBASE-BTC-USD","COINBASE-ETH-USD","COINBASE-ETH-BTC"]
    win = MainWindow(config, args.zmq_port)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
