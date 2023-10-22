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
    self.__clear_screen()
    listfont = self.ui.listWidget.font()
    listfont.setPointSize(12)
    self.ui.clear_history_button.clicked.connect(lambda _ : self.ui.listWidget.clear())

  def __type_number(self, num):
    if len(self.ui.output.text()) > 0 and self.ui.output.text()[-1] == '=':
      self.ui.output.setText("")
      self.out_value = ""
      self.in_value = ""
      self.in_op = ""
      self.ui.input.setText("")

    if num == 0 and self.in_value[-1] != '0':
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