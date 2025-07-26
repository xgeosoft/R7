from PyQt5.QtWidgets import QMainWindow,QMessageBox,QTableWidgetItem,QFileDialog
from class_ui.demande_conge_ui import Ui_MenuDemandeConge  # Interface générée de la fenêtre Personnel
from views.fenetre_parametre_demande_conge import FenetreParametreDemande
import sqlite3
from datetime import datetime
import time
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDate

class FenetreDemande(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MenuDemandeConge()
        self.ui.setupUi(self)
        
        self.ui.lineEdit_id.setEnabled(False)
        self.ui.pushButton_parametres.clicked.connect(self.ouvrir_parametre_demande_conge)
        
    def ouvrir_parametre_demande_conge(self):
        self.parametre_demande_conge = FenetreParametreDemande()
        self.parametre_demande_conge.show()
