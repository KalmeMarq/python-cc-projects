# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ex3_forca.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(590, 297)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 10, 131, 16))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 60, 131, 16))
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 110, 131, 16))
        self.letrasDigitadasL = QLabel(self.centralwidget)
        self.letrasDigitadasL.setObjectName(u"letrasDigitadasL")
        self.letrasDigitadasL.setGeometry(QRect(20, 30, 291, 16))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.letrasDigitadasL.setFont(font)
        self.chancesL = QLabel(self.centralwidget)
        self.chancesL.setObjectName(u"chancesL")
        self.chancesL.setGeometry(QRect(20, 80, 291, 16))
        self.chancesL.setFont(font)
        self.palavraSecL = QLabel(self.centralwidget)
        self.palavraSecL.setObjectName(u"palavraSecL")
        self.palavraSecL.setGeometry(QRect(20, 130, 291, 16))
        self.palavraSecL.setFont(font)
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 170, 563, 116))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.a_btn = QPushButton(self.layoutWidget)
        self.a_btn.setObjectName(u"a_btn")

        self.gridLayout.addWidget(self.a_btn, 0, 0, 1, 1)

        self.b_btn = QPushButton(self.layoutWidget)
        self.b_btn.setObjectName(u"b_btn")

        self.gridLayout.addWidget(self.b_btn, 0, 1, 1, 1)

        self.c_btn = QPushButton(self.layoutWidget)
        self.c_btn.setObjectName(u"c_btn")

        self.gridLayout.addWidget(self.c_btn, 0, 2, 1, 1)

        self.d_btn = QPushButton(self.layoutWidget)
        self.d_btn.setObjectName(u"d_btn")

        self.gridLayout.addWidget(self.d_btn, 0, 3, 1, 1)

        self.e_btn = QPushButton(self.layoutWidget)
        self.e_btn.setObjectName(u"e_btn")

        self.gridLayout.addWidget(self.e_btn, 0, 4, 1, 1)

        self.f_btn = QPushButton(self.layoutWidget)
        self.f_btn.setObjectName(u"f_btn")

        self.gridLayout.addWidget(self.f_btn, 0, 5, 1, 1)

        self.g_btn = QPushButton(self.layoutWidget)
        self.g_btn.setObjectName(u"g_btn")

        self.gridLayout.addWidget(self.g_btn, 0, 6, 1, 1)

        self.h_btn = QPushButton(self.layoutWidget)
        self.h_btn.setObjectName(u"h_btn")

        self.gridLayout.addWidget(self.h_btn, 1, 0, 1, 1)

        self.i_btn = QPushButton(self.layoutWidget)
        self.i_btn.setObjectName(u"i_btn")

        self.gridLayout.addWidget(self.i_btn, 1, 1, 1, 1)

        self.j_btn = QPushButton(self.layoutWidget)
        self.j_btn.setObjectName(u"j_btn")

        self.gridLayout.addWidget(self.j_btn, 1, 2, 1, 1)

        self.k_btn = QPushButton(self.layoutWidget)
        self.k_btn.setObjectName(u"k_btn")

        self.gridLayout.addWidget(self.k_btn, 1, 3, 1, 1)

        self.l_btn = QPushButton(self.layoutWidget)
        self.l_btn.setObjectName(u"l_btn")

        self.gridLayout.addWidget(self.l_btn, 1, 4, 1, 1)

        self.m_btn = QPushButton(self.layoutWidget)
        self.m_btn.setObjectName(u"m_btn")

        self.gridLayout.addWidget(self.m_btn, 1, 5, 1, 1)

        self.n_btn = QPushButton(self.layoutWidget)
        self.n_btn.setObjectName(u"n_btn")

        self.gridLayout.addWidget(self.n_btn, 1, 6, 1, 1)

        self.o_btn = QPushButton(self.layoutWidget)
        self.o_btn.setObjectName(u"o_btn")

        self.gridLayout.addWidget(self.o_btn, 2, 0, 1, 1)

        self.p_btn = QPushButton(self.layoutWidget)
        self.p_btn.setObjectName(u"p_btn")

        self.gridLayout.addWidget(self.p_btn, 2, 1, 1, 1)

        self.q_btn = QPushButton(self.layoutWidget)
        self.q_btn.setObjectName(u"q_btn")

        self.gridLayout.addWidget(self.q_btn, 2, 2, 1, 1)

        self.r_btn = QPushButton(self.layoutWidget)
        self.r_btn.setObjectName(u"r_btn")

        self.gridLayout.addWidget(self.r_btn, 2, 3, 1, 1)

        self.s_btn = QPushButton(self.layoutWidget)
        self.s_btn.setObjectName(u"s_btn")

        self.gridLayout.addWidget(self.s_btn, 2, 4, 1, 1)

        self.t_btn = QPushButton(self.layoutWidget)
        self.t_btn.setObjectName(u"t_btn")

        self.gridLayout.addWidget(self.t_btn, 2, 5, 1, 1)

        self.u_btn = QPushButton(self.layoutWidget)
        self.u_btn.setObjectName(u"u_btn")

        self.gridLayout.addWidget(self.u_btn, 2, 6, 1, 1)

        self.v_btn = QPushButton(self.layoutWidget)
        self.v_btn.setObjectName(u"v_btn")

        self.gridLayout.addWidget(self.v_btn, 3, 0, 1, 1)

        self.w_btn = QPushButton(self.layoutWidget)
        self.w_btn.setObjectName(u"w_btn")

        self.gridLayout.addWidget(self.w_btn, 3, 1, 1, 1)

        self.x_btn = QPushButton(self.layoutWidget)
        self.x_btn.setObjectName(u"x_btn")

        self.gridLayout.addWidget(self.x_btn, 3, 2, 1, 1)

        self.y_btn = QPushButton(self.layoutWidget)
        self.y_btn.setObjectName(u"y_btn")

        self.gridLayout.addWidget(self.y_btn, 3, 3, 1, 1)

        self.z_btn = QPushButton(self.layoutWidget)
        self.z_btn.setObjectName(u"z_btn")

        self.gridLayout.addWidget(self.z_btn, 3, 4, 1, 1)

        self.reiniciar_btn = QPushButton(self.layoutWidget)
        self.reiniciar_btn.setObjectName(u"reiniciar_btn")

        self.gridLayout.addWidget(self.reiniciar_btn, 3, 5, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"LETRA DIGITADAS", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"CHANCES RESTANTES", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"PALAVRA SECRETA", None))
        self.letrasDigitadasL.setText("")
        self.chancesL.setText("")
        self.palavraSecL.setText("")
        self.a_btn.setText(QCoreApplication.translate("MainWindow", u"A", None))
        self.b_btn.setText(QCoreApplication.translate("MainWindow", u"B", None))
        self.c_btn.setText(QCoreApplication.translate("MainWindow", u"C", None))
        self.d_btn.setText(QCoreApplication.translate("MainWindow", u"D", None))
        self.e_btn.setText(QCoreApplication.translate("MainWindow", u"E", None))
        self.f_btn.setText(QCoreApplication.translate("MainWindow", u"F", None))
        self.g_btn.setText(QCoreApplication.translate("MainWindow", u"G", None))
        self.h_btn.setText(QCoreApplication.translate("MainWindow", u"H", None))
        self.i_btn.setText(QCoreApplication.translate("MainWindow", u"I", None))
        self.j_btn.setText(QCoreApplication.translate("MainWindow", u"J", None))
        self.k_btn.setText(QCoreApplication.translate("MainWindow", u"K", None))
        self.l_btn.setText(QCoreApplication.translate("MainWindow", u"L", None))
        self.m_btn.setText(QCoreApplication.translate("MainWindow", u"M", None))
        self.n_btn.setText(QCoreApplication.translate("MainWindow", u"N", None))
        self.o_btn.setText(QCoreApplication.translate("MainWindow", u"O", None))
        self.p_btn.setText(QCoreApplication.translate("MainWindow", u"P", None))
        self.q_btn.setText(QCoreApplication.translate("MainWindow", u"Q", None))
        self.r_btn.setText(QCoreApplication.translate("MainWindow", u"R", None))
        self.s_btn.setText(QCoreApplication.translate("MainWindow", u"S", None))
        self.t_btn.setText(QCoreApplication.translate("MainWindow", u"T", None))
        self.u_btn.setText(QCoreApplication.translate("MainWindow", u"U", None))
        self.v_btn.setText(QCoreApplication.translate("MainWindow", u"V", None))
        self.w_btn.setText(QCoreApplication.translate("MainWindow", u"W", None))
        self.x_btn.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.y_btn.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.z_btn.setText(QCoreApplication.translate("MainWindow", u"Z", None))
        self.reiniciar_btn.setText(QCoreApplication.translate("MainWindow", u"Reiniciar", None))
    # retranslateUi

