import sqlite3
import os
from  utils import utilitaires
from class_ui.fenetre_chercher_personnel_ui import Ui_FenetreChercherPersonnel
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
from utils.utilitaires import resource_path
import time
import shutil


class FenetreChercherPersonnel(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetreChercherPersonnel()
        self.ui.setupUi(self)
        self.ncol_tableWidget_ui = 21
        self.id_selectionne = ""
        self.db_path = resource_path("data/database.db")


        self.ui.btn_chercher.clicked.connect(self.chercher_personnel)
        self.ui.btn_afficher_tout.clicked.connect(self.afficher_table_personnel)
        self.ui.btn_selectionner.clicked.connect(self.selectionner_personnel)
        


    def afficher_table_personnel(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # sélectionner données
        req = """SELECT * FROM personnel ORDER BY id DESC"""
        cursor.execute(req)
        data = cursor.fetchall() # recupérer les données
        conn.close()
        
        if data is not None:
            row_index = 0
            for row in data:
                for col in range(self.ncol_tableWidget_ui): #afficher toes les colonnes
                    self.ui.tableWidget_personnel.setItem(row_index,col,QTableWidgetItem(str(row[col])))
                row_index = row_index + 1
            
        
    
    def chercher_personnel(self):
        try:
            chercher = self.ui.txt_chercher.text()
            self.ui.tableWidget_personnel.clearContents() # effacer le visuel de la table et réactualiser
            
            if not chercher == "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # sélectionner données
                valeur_like = f"%{chercher}%"
                req = "SELECT * FROM personnel WHERE LOWER(npi || nom || prenom || matricule || date_naissance || telephone1 || telephone2 || adresse || email || url_photo || numero_ifu || numero_cnss || numero_rib) LIKE ?"
                cursor.execute(req,(valeur_like,))
                data = cursor.fetchall() # recupérer les données
                conn.close()
                
                if len(data) > 0:
                    row_index = 0
                    for row in data:
                        for col in range(self.ncol_tableWidget_ui): #afficher toes les colonnes
                            self.ui.tableWidget_personnel.setItem(row_index,col,QTableWidgetItem(str(row[col])))
                        row_index = row_index + 1
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

    def selectionner_personnel(self):
        personnel_id = ""
        item_selectionnee = self.ui.tableWidget_personnel.selectedItems()
        row_data = [item.text() for item in item_selectionnee]

        if len(row_data) == self.ncol_tableWidget_ui:
            personnel_id = row_data[0]
        
        if personnel_id == "":
            QMessageBox.critical(
                None,
                "Alerte",
                f"Aucun ID valide n'a été sélectionné",
                QMessageBox.Close
            )
        else:
            self.close()
        self.id_selectionne = personnel_id
        
            
            

