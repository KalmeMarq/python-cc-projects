import sys
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from ui_application_window import Ui_MainWindow

class ApplicationWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.setWindowIcon(QIcon("res/icon.png"))
    self.setWindowTitle("Calculadora")
    self.setWindowFlags(Qt.WindowType.MSWindowsFixedSizeDialogHint)
    self.ui.zero_button.clicked.connect(lambda _ : self.__type_number(0))
    self.ui.one_button.clicked.connect(lambda _ : self.__type_number(1))
    self.ui.two_button.clicked.connect(lambda _ : self.__type_number(2))
    self.ui.three_button.clicked.connect(lambda _ : self.__type_number(3))
    self.ui.four_button.clicked.connect(lambda _ : self.__type_number(4))
    self.ui.five_button.clicked.connect(lambda _ : self.__type_number(5))
    self.ui.six_button.clicked.connect(lambda _ : self.__type_number(6))
    self.ui.seven_button.clicked.connect(lambda _ : self.__type_number(7))
    self.ui.eight_button.clicked.connect(lambda _ : self.__type_number(8))
    self.ui.nine_button.clicked.connect(lambda _ : self.__type_number(9))
    self.ui.plus_button.clicked.connect(lambda _ : self.__type_op("+"))
    self.ui.sub_button.clicked.connect(lambda _ : self.__type_op("-"))
    self.ui.mul_button.clicked.connect(lambda _ : self.__type_op("*"))
    self.ui.div_button.clicked.connect(lambda _ : self.__type_op("/"))
    self.ui.equal_button.clicked.connect(lambda _ : self.__type_equals())
    self.ui.clear_button.clicked.connect(lambda _ : self.__clear_screen())
    self.ui.dot_button.clicked.connect(lambda _ : self.__type_dot())
    self.ui.switch_neg_button.clicked.connect(lambda _ : self.__type_switch_neg())
    self.ui.clear_input_button.clicked.connect(lambda _ : self.__clear_input())
    self.ui.delete_button.clicked.connect(lambda _ : self.__delete_digit())
    self.ui.delete_button.setText("")
    self.ui.delete_button.setIcon(QIcon("res/delete.png"))
    self.ui.clear_history_button.clicked.connect(lambda _ : self.ui.listWidget.clear())
    self.ui.switch_neg_button.setProperty('class', 'centerbuttons')
    self.ui.dot_button.setProperty('class', 'centerbuttons')
    self.ui.zero_button.setProperty('class', 'centerbuttons')
    self.ui.one_button.setProperty('class', 'centerbuttons')
    self.ui.two_button.setProperty('class', 'centerbuttons')
    self.ui.three_button.setProperty('class', 'centerbuttons')
    self.ui.four_button.setProperty('class', 'centerbuttons')
    self.ui.five_button.setProperty('class', 'centerbuttons')
    self.ui.six_button.setProperty('class', 'centerbuttons')
    self.ui.seven_button.setProperty('class', 'centerbuttons')
    self.ui.eight_button.setProperty('class', 'centerbuttons')
    self.ui.nine_button.setProperty('class', 'centerbuttons')
    self.ui.clear_history_button.setText("")
    self.ui.clear_history_button.setIcon(QIcon("res/bin.png"))
    self.__apply_custom_styles()
    self.__clear_screen()
    
  def __apply_custom_styles(self):
    listfont = self.ui.listWidget.font()
    listfont.setPointSize(12)
    self.setStyleSheet("""
  QMainWindow {
    background: #202020;
  }

  QLabel {
    color: white;
    font-weight: 600;
  }
                       
  QListWidget {
    background: #202020;
    border-color: #202020;
    color: white;
    outline: 0;
  }

  QPushButton {
    border-radius: 4px;
    margin: 2px;
    color: white;
    font-size: 15px;
    font-weight: 600;
    background: #323232;
    border: 1px solid #323232;
  }

  QPushButton:hover {
    background: #3C3C3C;
  }
                       
  QPushButton:pressed {
    background: #323232;
  }
                       
  .centerbuttons {
    background: #3B3B3B;
    border: 1px solid #3B3B3B;
  }
                      
  .centerbuttons:hover {
    background: #323232;
  }
                       
  .centerbuttons:pressed {
    background: #282828;
  }
""")
    self.ui.equal_button.setStyleSheet("""
  QPushButton {
    background: #4CC2FF;
    color: black;
  }

  QPushButton:hover {
    background: #47B1E8;
  }
                       
  QPushButton:pressed {
    background: #42A1D2;
  }
""")
    self.ui.clear_history_button.setStyleSheet("""
font-size: 14px;
""")
    self.ui.clear_history_button.setStyleSheet("""
QPushButton {
  background: transparent;
  border-color: transparent;
  }

  QPushButton:hover {
    background: #2D2D2D;
  }
                       
  QPushButton:pressed {
    background: #292929;
  }
""")
    
  def __clear_input(self):
    if len(self.in_value) > 0:
      self.in_value = "0"
      self.ui.input.setText(self.in_value)

  def __delete_digit(self):
    if len(self.in_value) > 0:
      self.in_value = self.in_value[:-1]

    if len(self.in_value) == 0:
      self.in_value = "0"

    self.ui.input.setText(self.in_value)

  def __type_number(self, num):
    if len(self.ui.output.text()) > 0 and (self.ui.output.text()[-1] == '=' or not self.in_value.isnumeric()):
      self.ui.output.setText("")
      self.out_value = ""
      self.in_value = ""
      self.in_op = ""
      self.ui.input.setText("")

    if num == 0 and len(self.ui.output.text()) > 0 and self.in_value[-1] != '0':
      self.in_value += str(num)
    else:
      if self.in_value == '0':
        self.in_value = ""
      self.in_value += str(num)
    self.ui.input.setText(self.in_value)

  def __type_op(self, op: str):
    self.out_value = self.in_value
    self.in_op = op
    self.ui.output.setText(f"{self.out_value} {op}")
    self.ui.input.setText("0")
    self.in_value = "0"

  def __type_switch_neg(self):
    if self.in_value.find("-") == -1:
      self.in_value = "-" + self.in_value
    else:
      self.in_value = self.in_value[1:]
    self.ui.input.setText(self.in_value)

  def __type_dot(self):
    if self.in_value.find(".") == -1:
      self.in_value += "."
      self.ui.input.setText(self.in_value)

  def __clear_screen(self):
    self.ui.output.setText("")
    self.in_value = "0"
    self.out_value = ""
    self.in_op = ""
    self.ui.input.setText(self.in_value)

  def __type_equals(self):
    try:
      float(self.in_value)
    except Exception:
      self.__clear_screen()
      return

    if len(self.out_value) == 0:
      self.ui.output.setText(f"{self.in_value} =")
      self.ui.listWidget.insertItem(0, f"{self.in_value} = {self.in_value}")
    else:
      left_value = float(self.out_value)
      right_value = float(self.in_value)

      if self.in_op == "+":
        result = left_value + right_value

      if self.in_op == "-":
        result = left_value - right_value

      if self.in_op == "*":
        result = left_value * right_value

      if self.in_op == "/":
        if right_value == 0:
          self.in_value = "Não podes dividir por zero"
          self.ui.input.setText(self.in_value)
          return

        result = left_value / right_value

      self.ui.output.setText(f"{self.out_value} {self.in_op} {self.in_value} =")
      self.in_value = str(result)
      self.ui.input.setText(self.in_value)
      self.ui.listWidget.insertItem(0, f"{self.ui.output.text()} {self.in_value}")

def main():
  app = QApplication(sys.argv)
  app.setStyle('fusion')

  win = ApplicationWindow()
  win.show()
  
  app.exec()

if __name__ == "__main__":
  main()