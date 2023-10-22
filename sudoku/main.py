import sys
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import *

class ApplicationWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Sudoku")
    self.webview = QWebEngineView()
    self.webview.setUrl("https://kalmemarq.github.io/sudoku")
    self.setCentralWidget(self.webview)

def main():
  app = QApplication(sys.argv)
  app.setStyle('fusion')

  win = ApplicationWindow()
  win.show()
  
  app.exec()

if __name__ == "__main__":
  main()