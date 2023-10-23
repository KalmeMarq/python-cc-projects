# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ex2_colordraw.ui'
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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(605, 475)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 0, 211, 431))
        self.widget.setStyleSheet(u"background-color: rgb(89, 74, 255);")
        self.verticalLayoutWidget = QWidget(self.widget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(30, 40, 146, 318))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.colorL3 = QLabel(self.verticalLayoutWidget)
        self.colorL3.setObjectName(u"colorL3")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.colorL3.sizePolicy().hasHeightForWidth())
        self.colorL3.setSizePolicy(sizePolicy)
        self.colorL3.setMinimumSize(QSize(68, 68))
        self.colorL3.setMaximumSize(QSize(68, 68))
        self.colorL3.setStyleSheet(u"background: rgb(10, 255, 10)")

        self.gridLayout_2.addWidget(self.colorL3, 1, 0, 1, 1)

        self.colorL4 = QLabel(self.verticalLayoutWidget)
        self.colorL4.setObjectName(u"colorL4")
        self.colorL4.setStyleSheet(u"background: rgb(255, 255, 10)")

        self.gridLayout_2.addWidget(self.colorL4, 1, 1, 1, 1)

        self.colorL2 = QLabel(self.verticalLayoutWidget)
        self.colorL2.setObjectName(u"colorL2")
        sizePolicy.setHeightForWidth(self.colorL2.sizePolicy().hasHeightForWidth())
        self.colorL2.setSizePolicy(sizePolicy)
        self.colorL2.setMinimumSize(QSize(68, 68))
        self.colorL2.setMaximumSize(QSize(68, 68))
        self.colorL2.setStyleSheet(u"background: rgb(255, 10, 10)")

        self.gridLayout_2.addWidget(self.colorL2, 0, 1, 1, 1)

        self.colorL1 = QLabel(self.verticalLayoutWidget)
        self.colorL1.setObjectName(u"colorL1")
        sizePolicy.setHeightForWidth(self.colorL1.sizePolicy().hasHeightForWidth())
        self.colorL1.setSizePolicy(sizePolicy)
        self.colorL1.setMinimumSize(QSize(68, 68))
        self.colorL1.setMaximumSize(QSize(68, 68))
        self.colorL1.setStyleSheet(u"background: rgb(10, 10, 255)")

        self.gridLayout_2.addWidget(self.colorL1, 0, 0, 1, 1)

        self.colorL6 = QLabel(self.verticalLayoutWidget)
        self.colorL6.setObjectName(u"colorL6")
        self.colorL6.setStyleSheet(u"background: rgb(255, 255, 255)")

        self.gridLayout_2.addWidget(self.colorL6, 2, 1, 1, 1)

        self.colorL5 = QLabel(self.verticalLayoutWidget)
        self.colorL5.setObjectName(u"colorL5")
        sizePolicy.setHeightForWidth(self.colorL5.sizePolicy().hasHeightForWidth())
        self.colorL5.setSizePolicy(sizePolicy)
        self.colorL5.setMinimumSize(QSize(68, 68))
        self.colorL5.setMaximumSize(QSize(68, 66))
        self.colorL5.setStyleSheet(u"background: rgb(0, 0, 0)")

        self.gridLayout_2.addWidget(self.colorL5, 2, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)

        self.label_2 = QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"color: rgb(255, 255, 255);")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.currentColorL = QLabel(self.verticalLayoutWidget)
        self.currentColorL.setObjectName(u"currentColorL")
        sizePolicy.setHeightForWidth(self.currentColorL.sizePolicy().hasHeightForWidth())
        self.currentColorL.setSizePolicy(sizePolicy)
        self.currentColorL.setMinimumSize(QSize(68, 68))
        self.currentColorL.setMaximumSize(QSize(68, 68))
        self.currentColorL.setStyleSheet(u"background: rgb(255, 10, 10)")

        self.horizontalLayout.addWidget(self.currentColorL)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(50, 10, 111, 16))
        self.label.setStyleSheet(u"color: rgb(255, 255, 255);")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 605, 22))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.colorL3.setText("")
        self.colorL4.setText("")
        self.colorL2.setText("")
        self.colorL1.setText("")
        self.colorL6.setText("")
        self.colorL5.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Color Atual", None))
        self.currentColorL.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"Area de Desenho", None))
    # retranslateUi

