import sqlite3
import os
from  utils import utilitaires
from class_ui.fenetre_acceuil_ui import Ui_FenetreAcceuil
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
import time
import shutil


class FenetreAcceuil(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetreAcceuil()
        self.ui.setupUi(self)
            
            

