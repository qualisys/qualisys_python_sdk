# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainXtezAc.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDockWidget, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(905, 537)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_5 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout_2.addWidget(self.label_6)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(9, 9, 9, 9)
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setLayoutDirection(Qt.LeftToRight)
        self.label_4.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.label_4, 1, 1, 1, 1)

        self.y_trajectory = QLineEdit(self.groupBox)
        self.y_trajectory.setObjectName(u"y_trajectory")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.y_trajectory.sizePolicy().hasHeightForWidth())
        self.y_trajectory.setSizePolicy(sizePolicy)
        self.y_trajectory.setReadOnly(True)

        self.gridLayout_2.addWidget(self.y_trajectory, 1, 2, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setLayoutDirection(Qt.LeftToRight)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.label_5, 0, 1, 1, 1)

        self.x_trajectory = QLineEdit(self.groupBox)
        self.x_trajectory.setObjectName(u"x_trajectory")
        sizePolicy.setHeightForWidth(self.x_trajectory.sizePolicy().hasHeightForWidth())
        self.x_trajectory.setSizePolicy(sizePolicy)
        self.x_trajectory.setReadOnly(True)

        self.gridLayout_2.addWidget(self.x_trajectory, 0, 2, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setLayoutDirection(Qt.LeftToRight)
        self.label_3.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.label_3, 2, 1, 1, 1)

        self.z_trajectory = QLineEdit(self.groupBox)
        self.z_trajectory.setObjectName(u"z_trajectory")
        sizePolicy.setHeightForWidth(self.z_trajectory.sizePolicy().hasHeightForWidth())
        self.z_trajectory.setSizePolicy(sizePolicy)
        self.z_trajectory.setReadOnly(True)

        self.gridLayout_2.addWidget(self.z_trajectory, 2, 2, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_2)

        self.trajectory_combo = QComboBox(self.groupBox)
        self.trajectory_combo.setObjectName(u"trajectory_combo")

        self.verticalLayout_2.addWidget(self.trajectory_combo)


        self.horizontalLayout_5.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_3.addWidget(self.label_7)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(9, 9, 9, 9)
        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.label_8, 0, 0, 1, 1)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.label_10, 2, 0, 1, 1)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.label_9, 1, 0, 1, 1)

        self.x_sixdof = QLineEdit(self.groupBox)
        self.x_sixdof.setObjectName(u"x_sixdof")
        sizePolicy.setHeightForWidth(self.x_sixdof.sizePolicy().hasHeightForWidth())
        self.x_sixdof.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.x_sixdof, 0, 1, 1, 1)

        self.y_sixdof = QLineEdit(self.groupBox)
        self.y_sixdof.setObjectName(u"y_sixdof")
        sizePolicy.setHeightForWidth(self.y_sixdof.sizePolicy().hasHeightForWidth())
        self.y_sixdof.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.y_sixdof, 1, 1, 1, 1)

        self.z_sixdof = QLineEdit(self.groupBox)
        self.z_sixdof.setObjectName(u"z_sixdof")
        sizePolicy.setHeightForWidth(self.z_sixdof.sizePolicy().hasHeightForWidth())
        self.z_sixdof.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.z_sixdof, 2, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_4)

        self.sixdof_combo = QComboBox(self.groupBox)
        self.sixdof_combo.setObjectName(u"sixdof_combo")

        self.verticalLayout_3.addWidget(self.sixdof_combo)


        self.horizontalLayout_5.addLayout(self.verticalLayout_3)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_11 = QLabel(self.centralwidget)
        self.label_11.setObjectName(u"label_11")

        self.verticalLayout_4.addWidget(self.label_11)

        self.settings_combo = QComboBox(self.centralwidget)
        self.settings_combo.setObjectName(u"settings_combo")

        self.verticalLayout_4.addWidget(self.settings_combo)

        self.settings_viewer = QTextEdit(self.centralwidget)
        self.settings_viewer.setObjectName(u"settings_viewer")
        self.settings_viewer.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.settings_viewer)


        self.gridLayout.addLayout(self.verticalLayout_4, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.dockWidget_2 = QDockWidget(MainWindow)
        self.dockWidget_2.setObjectName(u"dockWidget_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.dockWidget_2.sizePolicy().hasHeightForWidth())
        self.dockWidget_2.setSizePolicy(sizePolicy1)
        self.dockWidget_2.setMinimumSize(QSize(240, 180))
        self.dockWidget_2.setFeatures(QDockWidget.DockWidgetMovable)
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, -1, 9, -1)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.dockWidgetContents_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.qtm_combo = QComboBox(self.dockWidgetContents_2)
        self.qtm_combo.setObjectName(u"qtm_combo")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.qtm_combo.sizePolicy().hasHeightForWidth())
        self.qtm_combo.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.qtm_combo)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.discover_button = QPushButton(self.dockWidgetContents_2)
        self.discover_button.setObjectName(u"discover_button")

        self.verticalLayout.addWidget(self.discover_button)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.connect_button = QPushButton(self.dockWidgetContents_2)
        self.connect_button.setObjectName(u"connect_button")
        self.connect_button.setEnabled(False)

        self.horizontalLayout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton(self.dockWidgetContents_2)
        self.disconnect_button.setObjectName(u"disconnect_button")
        self.disconnect_button.setEnabled(False)

        self.horizontalLayout.addWidget(self.disconnect_button)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_2)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Streaming Info", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Trajectories", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Y:", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"X:", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Z:", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"6DOF", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"X:", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Z:", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Y:", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"QTM Settings", None))
        self.dockWidget_2.setWindowTitle(QCoreApplication.translate("MainWindow", u"QTM Controls", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"QTM: ", None))
        self.discover_button.setText(QCoreApplication.translate("MainWindow", u"Discover QTM", None))
        self.connect_button.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.disconnect_button.setText(QCoreApplication.translate("MainWindow", u"Disconnect", None))
    # retranslateUi

