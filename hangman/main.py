import sys
from PySide6.QtCore import *
from PySide6.QtWidgets import *
import ui_ex3_forca
import ui_ex3_forca_start_dialog

class StartDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.ui = ui_ex3_forca_start_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Escolher a palavra secreta")
        self.ui.pushButton.clicked.connect(self.accept)

class ApplicationWindow(QMainWindow):
    def __init__(self, secret_word: str) -> None:
        super().__init__()
        self.ui = ui_ex3_forca.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Jogo da Forca")
        self.ui.a_btn.clicked.connect(lambda _ : self.__type_letter('A'))
        self.ui.b_btn.clicked.connect(lambda _ : self.__type_letter('B'))
        self.ui.c_btn.clicked.connect(lambda _ : self.__type_letter('C'))
        self.ui.d_btn.clicked.connect(lambda _ : self.__type_letter('D'))
        self.ui.e_btn.clicked.connect(lambda _ : self.__type_letter('E'))
        self.ui.f_btn.clicked.connect(lambda _ : self.__type_letter('F'))
        self.ui.g_btn.clicked.connect(lambda _ : self.__type_letter('G'))
        self.ui.h_btn.clicked.connect(lambda _ : self.__type_letter('H'))
        self.ui.i_btn.clicked.connect(lambda _ : self.__type_letter('I'))
        self.ui.j_btn.clicked.connect(lambda _ : self.__type_letter('J'))
        self.ui.k_btn.clicked.connect(lambda _ : self.__type_letter('K'))
        self.ui.l_btn.clicked.connect(lambda _ : self.__type_letter('L'))
        self.ui.m_btn.clicked.connect(lambda _ : self.__type_letter('M'))
        self.ui.n_btn.clicked.connect(lambda _ : self.__type_letter('N'))
        self.ui.o_btn.clicked.connect(lambda _ : self.__type_letter('O'))
        self.ui.p_btn.clicked.connect(lambda _ : self.__type_letter('P'))
        self.ui.q_btn.clicked.connect(lambda _ : self.__type_letter('Q'))
        self.ui.r_btn.clicked.connect(lambda _ : self.__type_letter('R'))
        self.ui.s_btn.clicked.connect(lambda _ : self.__type_letter('S'))
        self.ui.t_btn.clicked.connect(lambda _ : self.__type_letter('T'))
        self.ui.u_btn.clicked.connect(lambda _ : self.__type_letter('U'))
        self.ui.v_btn.clicked.connect(lambda _ : self.__type_letter('V'))
        self.ui.w_btn.clicked.connect(lambda _ : self.__type_letter('W'))
        self.ui.x_btn.clicked.connect(lambda _ : self.__type_letter('X'))
        self.ui.y_btn.clicked.connect(lambda _ : self.__type_letter('Y'))
        self.ui.z_btn.clicked.connect(lambda _ : self.__type_letter('Z'))
        self.secret_word = secret_word
        self.chances = 10
        self.ui.chancesL.setText(str(self.chances))
        self.ui.letrasDigitadasL.setText("")
        self.fill_word = " " * len(self.secret_word)
        self.ui.palavraSecL.setText(self.fill_word)

    def __start_game(self):
        self.chances = 10
        self.ui.chancesL.setText(str(self.chances))
        self.ui.letrasDigitadasL.setText("")
        self.fill_word = " " * len(self.secret_word)
        self.ui.palavraSecL.setText(self.fill_word)

        dialog = StartDialog(self)
        if dialog.exec() == 0:
            QApplication.quit()
            return
        else:
            self.secret_word = dialog.ui.lineEdit.text()

    def __type_letter(self, letter: str):
        if self.ui.letrasDigitadasL.text().find(letter) == -1:
            self.ui.letrasDigitadasL.setText(self.ui.letrasDigitadasL.text() + letter)

            if self.secret_word.find(letter) == -1:
                self.chances -= 1
            else:
                for i in range(len(self.secret_word)):
                    if self.secret_word[i] == letter:
                        self.fill_word = self.fill_word[:i] + letter + self.fill_word[(i + 1):]
                        self.ui.palavraSecL.setText(self.fill_word)
        
        self.ui.chancesL.setText(str(self.chances))

        if self.fill_word == self.secret_word:
            dialog = QMessageBox(QMessageBox.Icon.Information, "Parabéns", f"Parabéns! Acertaste a palavra secreta\n{self.secret_word}", parent=self)
            if dialog.exec():
                self.__start_game()

        if self.chances == 0:
            dialog = QMessageBox(QMessageBox.Icon.Information, "Perdeste!", f"Perdeste! A palavra secreta era\n{self.secret_word}", parent=self)
            if dialog.exec():
                self.__start_game()

def main():
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    
    dialog = StartDialog(None)
    if dialog.exec() == 0:
        QApplication.quit()
        return
    else:
        win = ApplicationWindow(dialog.ui.lineEdit.text())
        win.show()
    
    app.exec()

if __name__ == "__main__":
    main()