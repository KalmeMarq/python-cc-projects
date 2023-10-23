from __future__ import annotations
import sys
from PySide6.QtCore import *
import PySide6.QtCore
import PySide6.QtGui
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import ui_ex2_colordraw

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent, appWindow: ApplicationWindow) -> None:
        super().__init__(parent)
        self.appWindow = appWindow
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        mx = event.position().x()
        my = event.position().y()
        s_size = 54
        slotx = mx / s_size
        sloty = my / s_size
        self.appWindow.set_slot(int(slotx), int(sloty))

class ApplicationWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = ui_ex2_colordraw.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.graphicsView = CustomGraphicsView(self.ui.centralwidget, self)
        self.ui.graphicsView.setObjectName(u"graphicsView")
        self.ui.graphicsView.setGeometry(QRect(210, 0, 378, 432))
        self.setWindowTitle("Area de Desenho")
        self.ui.colorL1.mousePressEvent = lambda _ : self.__update_current_color_label(0)
        self.ui.colorL2.mousePressEvent = lambda _ : self.__update_current_color_label(1)
        self.ui.colorL3.mousePressEvent = lambda _ : self.__update_current_color_label(2)
        self.ui.colorL4.mousePressEvent = lambda _ : self.__update_current_color_label(3)
        self.ui.colorL5.mousePressEvent = lambda _ : self.__update_current_color_label(4)
        self.ui.colorL6.mousePressEvent = lambda _ : self.__update_current_color_label(5)
        
        self.ui.graphicsView.setAlignment(Qt.AlignTop | Qt.AlignLeft);
        self.ui.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ui.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.colors = [
            [Qt.GlobalColor.blue, 0x0A0AFF],
            [Qt.GlobalColor.red, 0xFF0A0A],
            [Qt.GlobalColor.green, 0x0AFF0A],
            [Qt.GlobalColor.yellow, 0xFFFF0A],
            [Qt.GlobalColor.black, 0x000000],
            [Qt.GlobalColor.white, 0xFFFFFF]
        ]
        self.currentColor = 1
        self.gridSlots = [0] * (7 * 8)
        self.__redraw_scene()

    def set_slot(self, x, y):
        self.gridSlots[y * 7 + x] = self.currentColor + 1
        self.__redraw_scene()

    def __redraw_scene(self):
        scene = QGraphicsScene()
        for x in range(0, 7):
            for y in range(0, 8):
                slot = self.gridSlots[y * 7 + x]
                if slot > 0:
                    scene.addRect(QRect(x * 54, y * 54, 54, 54), brush=QBrush(self.colors[slot - 1][0]))
                else:
                    scene.addRect(QRect(x * 54, y * 54, 54, 54))
        self.ui.graphicsView.setScene(scene)

    def __update_current_color_label(self, color_index):
        self.currentColor = color_index
        color = self.colors[self.currentColor][1]
        self.ui.currentColorL.setStyleSheet(f"background: rgb({color >> 16 & 0xFF},{color >> 8 & 0xFF},{color& 0xFF})")

def main():
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    
    win = ApplicationWindow()
    win.show()
    
    app.exec()

if __name__ == "__main__":
    main()