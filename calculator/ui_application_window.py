# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'application_window.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QSizePolicy, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(522, 380)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.output = QLabel(self.centralwidget)
        self.output.setObjectName(u"output")
        self.output.setGeometry(QRect(8, 10, 201, 20))
        self.output.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.input = QLabel(self.centralwidget)
        self.input.setObjectName(u"input")
        self.input.setGeometry(QRect(8, 40, 201, 20))
        font = QFont()
        font.setPointSize(11)
        self.input.setFont(font)
        self.input.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.seven_button = QPushButton(self.centralwidget)
        self.seven_button.setObjectName(u"seven_button")
        self.seven_button.setGeometry(QRect(10, 170, 51, 51))
        self.eight_button = QPushButton(self.centralwidget)
        self.eight_button.setObjectName(u"eight_button")
        self.eight_button.setGeometry(QRect(60, 170, 51, 51))
        self.nine_button = QPushButton(self.centralwidget)
        self.nine_button.setObjectName(u"nine_button")
        self.nine_button.setGeometry(QRect(110, 170, 51, 51))
        self.four_button = QPushButton(self.centralwidget)
        self.four_button.setObjectName(u"four_button")
        self.four_button.setGeometry(QRect(10, 220, 51, 51))
        self.five_button = QPushButton(self.centralwidget)
        self.five_button.setObjectName(u"five_button")
        self.five_button.setGeometry(QRect(60, 220, 51, 51))
        self.six_button = QPushButton(self.centralwidget)
        self.six_button.setObjectName(u"six_button")
        self.six_button.setGeometry(QRect(110, 220, 51, 51))
        self.one_button = QPushButton(self.centralwidget)
        self.one_button.setObjectName(u"one_button")
        self.one_button.setGeometry(QRect(10, 270, 51, 51))
        self.two_button = QPushButton(self.centralwidget)
        self.two_button.setObjectName(u"two_button")
        self.two_button.setGeometry(QRect(60, 270, 51, 51))
        self.three_button = QPushButton(self.centralwidget)
        self.three_button.setObjectName(u"three_button")
        self.three_button.setGeometry(QRect(110, 270, 51, 51))
        self.zero_button = QPushButton(self.centralwidget)
        self.zero_button.setObjectName(u"zero_button")
        self.zero_button.setGeometry(QRect(60, 320, 51, 51))
        self.switch_neg_button = QPushButton(self.centralwidget)
        self.switch_neg_button.setObjectName(u"switch_neg_button")
        self.switch_neg_button.setGeometry(QRect(10, 320, 51, 51))
        self.dot_button = QPushButton(self.centralwidget)
        self.dot_button.setObjectName(u"dot_button")
        self.dot_button.setGeometry(QRect(110, 320, 51, 51))
        self.equal_button = QPushButton(self.centralwidget)
        self.equal_button.setObjectName(u"equal_button")
        self.equal_button.setGeometry(QRect(160, 320, 51, 51))
        self.plus_button = QPushButton(self.centralwidget)
        self.plus_button.setObjectName(u"plus_button")
        self.plus_button.setGeometry(QRect(160, 270, 51, 51))
        self.sub_button = QPushButton(self.centralwidget)
        self.sub_button.setObjectName(u"sub_button")
        self.sub_button.setGeometry(QRect(160, 220, 51, 51))
        self.mul_button = QPushButton(self.centralwidget)
        self.mul_button.setObjectName(u"mul_button")
        self.mul_button.setGeometry(QRect(160, 170, 51, 51))
        self.div_button = QPushButton(self.centralwidget)
        self.div_button.setObjectName(u"div_button")
        self.div_button.setGeometry(QRect(160, 120, 51, 51))
        self.clear_button = QPushButton(self.centralwidget)
        self.clear_button.setObjectName(u"clear_button")
        self.clear_button.setGeometry(QRect(110, 120, 51, 51))
        self.listWidget = QListWidget(self.centralwidget)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setGeometry(QRect(230, 40, 281, 331))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(230, 11, 141, 21))
        font1 = QFont()
        font1.setPointSize(10)
        self.label.setFont(font1)
        self.clear_history_button = QPushButton(self.centralwidget)
        self.clear_history_button.setObjectName(u"clear_history_button")
        self.clear_history_button.setGeometry(QRect(430, 10, 75, 24))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.output.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.input.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.seven_button.setText(QCoreApplication.translate("MainWindow", u"7", None))
        self.eight_button.setText(QCoreApplication.translate("MainWindow", u"8", None))
        self.nine_button.setText(QCoreApplication.translate("MainWindow", u"9", None))
        self.four_button.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.five_button.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.six_button.setText(QCoreApplication.translate("MainWindow", u"6", None))
        self.one_button.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.two_button.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.three_button.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.zero_button.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.switch_neg_button.setText(QCoreApplication.translate("MainWindow", u"+/-", None))
        self.dot_button.setText(QCoreApplication.translate("MainWindow", u".", None))
        self.equal_button.setText(QCoreApplication.translate("MainWindow", u"=", None))
        self.plus_button.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.sub_button.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.mul_button.setText(QCoreApplication.translate("MainWindow", u"*", None))
        self.div_button.setText(QCoreApplication.translate("MainWindow", u"/", None))
        self.clear_button.setText(QCoreApplication.translate("MainWindow", u"C", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Hist\u00f3rico", None))
        self.clear_history_button.setText(QCoreApplication.translate("MainWindow", u"Limpar", None))
    # retranslateUi

