from PyQt5.QtWidgets import QMainWindow,QMessageBox,QTableWidgetItem,QFileDialog
from class_ui.parametre_demande_conge_ui import Ui_MenuParametreDemandeConge  # Interface générée de la fenêtre Personnel

import sqlite3
from datetime import datetime
import time
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDate

class FenetreParametreDemande(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MenuParametreDemandeConge()
        self.ui.setupUi(self)
                
        # Efface d'abord les éléments existants si nécessaire
        self.ui.comboBox_nombrejours.clear()
        # Ajoute les valeurs de 1 à 366
        for i in range(1, 366):
            self.ui.comboBox_nombrejours.addItem(str(i), i)  # Texte affiché = str(i), Donnée associée = i
