import os
import sys
import argparse

from PyQt5 import QtWidgets

parser = argparse.ArgumentParser()
parser.add_argument("--config",   default="cryptogui/config.yaml", help='cryptostore configuration')
parser.add_argument("--zmq-port", dest="zmq_port", default=5556,   help='cryptostore zmq connection')
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
        self.init_menu()
        self.init_central_area()

    def load_config(self, config):
        pass

    def init_menu(self):
        menubar = self.menuBar()
        sysMenu = menubar.addMenu('File')
        
        # open folder
        sys_folderAction = QtWidgets.QAction('Folder', self)
        sys_folderAction.setStatusTip('Open_Folder')
        sys_folderAction.triggered.connect(self.open_proj_folder)
        sysMenu.addAction(sys_folderAction)
        sysMenu.addSeparator()
        
        # sys|exit
        sys_exitAction = QtWidgets.QAction('Exit', self)
        sys_exitAction.setShortcut('Ctrl+Q')
        sys_exitAction.setStatusTip('Exit_App')
        sys_exitAction.triggered.connect(self.close)
        sysMenu.addAction(sys_exitAction)

    def init_central_area(self):
        self.central_widget = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        main_layout = QtWidgets.QHBoxLayout()
        win = QtWidgets.QWidget()
        win.setLayout(main_layout)
        hbox.addWidget(win)
        self.central_widget.setLayout(hbox)
        self.setCentralWidget(self.central_widget)
        
    def open_proj_folder(self):
        pass
        # webbrowser.open(root)
        
    def closeEvent(self, a0: QtGui.QCloseEvent):
        print("QtGui.QCloseEvent")

def main():
    app = QtWidgets.QApplication([])
    import qdarkstyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    win = MainWindow(args.config, args.zmq_port)
    win.show()
    win.showMaximized()
    sys.exit(app.exec_())
