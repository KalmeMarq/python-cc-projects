import sys
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

class ApplicationWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Memory Game")

def main():
  app = QApplication(sys.argv)
  app.setStyle('fusion')

  win = ApplicationWindow()
  win.show()
  
  app.exec()

if __name__ == "__main__":
  main()