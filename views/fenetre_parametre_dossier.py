import sqlite3
import os
from  utils.utilitaires import resource_path
from class_ui.fenetre_chemin_dossier_ui import Ui_FenetreCheminDossier
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
import time
import shutil


class FenetreParametreDossier(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetreCheminDossier()
        self.ui.setupUi(self)
        self.db_path = resource_path("data/database.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.photo_path = ""
        
        self.cursor.execute('SELECT path FROM file_path WHERE file_type = ? ORDER BY id DESC LIMIT 1',('photo',))
        self.existing_file = self.cursor.fetchone()
        
        if self.existing_file != None:
            self.photo_path = self.existing_file[0]
            self.ui.txt_url_photo.setText(self.photo_path)
        
        self.ui.btn_select_photo.clicked.connect(self.choisir_dossier)

    def choisir_dossier(self):
        try:
            self.dossier = QFileDialog.getExistingDirectory(
                self,
                "Sélectionner le dossier pour les photos",
                "."  # dossier par défaut
            )
            
            
            if self.dossier != "":
                self.photo_path = self.dossier
                self.cursor.execute("INSERT INTO file_path (file_type, path) VALUES (?,?)",('photo',self.photo_path,))
                self.conn.commit()
                self.ui.txt_url_photo.setText(self.photo_path)
        except Exception as e:
            print(e)   
        