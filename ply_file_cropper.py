import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QGridLayout, \
    QFileDialog, QPushButton, QLineEdit, QInputDialog
from PyQt5.QtGui import QWindow
from PyQt5.QtCore import pyqtSlot, Qt
import numpy as np
import pptk
import win32gui
import open3d as o3d
import pickle


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'pptk'
        self.left = 50
        self.top = 50
        self.width = 800
        self.height = 600
        self.dict = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTable()
        self.createLoadPlyFileView()
        self.createLoadNpyFileView()
        self.createSaveButton()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QGridLayout()
        self.layout.addWidget(self.tableWidget, 0, 0)
        self.layout.addWidget(self.pb_save_pkl, 1, 0)
        self.layout.addWidget(self.pb_ply, 2, 0)
        self.layout.addWidget(self.le_ply, 2, 1)
        self.layout.addWidget(self.pb_pkl, 3, 0)
        self.layout.addWidget(self.le_pkl, 3, 1)
        self.setLayout(self.layout)

        # Show widget
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C:
            self.a = self.v.get('selected')
            self.v.close()
            self.v = pptk.viewer(self.xyz[self.a], self.rgb[self.a])
            hwnd = win32gui.FindWindowEx(0, 0, None, "viewer")
            self.window = QWindow.fromWinId(hwnd)
            self.windowcontainer = self.createWindowContainer(self.window, self.viewerWidget)
            self.windowcontainer.setFixedHeight(600)
            self.windowcontainer.setFixedWidth(600)
            self.layout.addWidget(self.windowcontainer, 0, 1)
            self.setLayout(self.layout)

            # Show widget
            self.show()

        elif event.key() == Qt.Key_S:
            text, ok = QInputDialog.getText(self, 'Save item', 'Enter the item name:')

            if ok:
                self.dict[text] = self.a
                self.tableWidget.insertRow(self.tableWidget.rowCount())
                self.tableWidget.setItem(self.tableWidget.rowCount()-1, 0, QTableWidgetItem(text))
                self.layout.addWidget(self.tableWidget, 0, 0)
                self.setLayout(self.layout)
                # Show widget
                self.show()

    def createLoadPlyFileView(self):
        self.le_ply = QLineEdit()
        self.le_ply.setObjectName("ply_path")

        self.pb_ply = QPushButton()
        self.pb_ply.setObjectName("load_ply")
        self.pb_ply.setText("Load .ply file")
        self.pb_ply.clicked.connect(self.on_ply_button_click)

    def createLoadNpyFileView(self):
        self.le_pkl = QLineEdit()
        self.le_pkl.setObjectName("pkl_path")

        self.pb_pkl = QPushButton()
        self.pb_pkl.setObjectName("load_pkl")
        self.pb_pkl.setText("Load .pkl file")
        self.pb_pkl.clicked.connect(self.on_pkl_button_click)

    def createSaveButton(self):
        self.pb_save_pkl = QPushButton()
        self.pb_save_pkl.setObjectName("save_pkl")
        self.pb_save_pkl.setText("Save .pkl file")
        self.pb_save_pkl.clicked.connect(self.on_pkl_save_button_click)

    def create3dView(self, path):
        self.viewerWidget = QWidget()
        pcd = o3d.io.read_point_cloud(path)
        self.xyz = np.asarray(pcd.points)
        self.rgb = np.asarray(pcd.colors)
        self.v = pptk.viewer(self.xyz, self.rgb)

        hwnd = win32gui.FindWindowEx(0, 0, None, "viewer")
        self.window = QWindow.fromWinId(hwnd)

        self.windowcontainer = self.createWindowContainer(self.window, self.viewerWidget)
        self.windowcontainer.setFixedHeight(600)
        self.windowcontainer.setFixedWidth(600)

    def createTable(self):
        # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(['Items'])
        self.tableWidget.setFixedHeight(600)
        self.tableWidget.setFixedWidth(200)

        # table selection change
        self.tableWidget.clicked.connect(self.on_click)

    @pyqtSlot()
    def on_click(self):
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            self.a = self.dict[currentQTableWidgetItem.text()]
            self.v.close()
            self.v = pptk.viewer(self.xyz[self.a], self.rgb[self.a])
            hwnd = win32gui.FindWindowEx(0, 0, None, "viewer")
            self.window = QWindow.fromWinId(hwnd)
            self.windowcontainer = self.createWindowContainer(self.window, self.viewerWidget)
            self.windowcontainer.setFixedHeight(600)
            self.windowcontainer.setFixedWidth(600)
            self.layout.addWidget(self.windowcontainer, 0, 1)
            self.setLayout(self.layout)

            # Show widget
            self.show()

    def on_ply_button_click(self):

        dialog = QFileDialog()

        options = QFileDialog.Options()
        self.file_dir = dialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                               "Point Cloud (*.ply)", options=options)
        self.le_ply.setText(self.file_dir[0])

        self.create3dView(path=self.file_dir[0])
        self.layout.addWidget(self.windowcontainer, 0, 1)
        self.setLayout(self.layout)
        # Show widget
        self.show()

    def on_pkl_button_click(self):

        dialog = QFileDialog()
        options = QFileDialog.Options()
        self.file_dir = dialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                               "Pickle (*.pkl)", options=options)
        self.le_pkl.setText(self.file_dir[0])

        with open(self.file_dir[0], 'rb') as f:
            self.dict = pickle.load(f)

        for key, value in self.dict.items():
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QTableWidgetItem(key))

        self.layout.addWidget(self.tableWidget, 0, 0)

        self.setLayout(self.layout)

        # Show widget
        self.show()

    def on_pkl_save_button_click(self):
        text, ok = QInputDialog.getText(self, 'Save item', 'Enter the item name:')

        if ok:
            with open(text + '.pkl', 'wb') as f:
                pickle.dump(self.dict, f, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
