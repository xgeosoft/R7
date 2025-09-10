import sqlite3
import os
from  utils.utilitaires import resource_path
from class_ui.fenetre_reinitialisation_ui import Ui_FenetreReinitialisation
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
import time
import shutil


class FenetreReinitialiser(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetreReinitialisation()
        self.ui.setupUi(self)
        self.db_path = resource_path("data/database.db")
        
        self.supprimer_donnees()
        self.ui.btn_reinitialiser_donnee.clicked.connect(self.supprimer_donnees)
        
    def supprimer_donnees(self):
        tables = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if self.ui.checkBox_personnel.isChecked() == True:
            QMessageBox.information(self,"Réinitialisation","Voulez-vous vraiment supprimer tous le personnel ? Cette action est irréversible.")
            tables.append("personnel")
            tables.append("suivi_carriere")
            tables.append("demande")
            
            # supprimer les photos
            photo_path = resource_path("images/photos")

            if os.path.exists(photo_path):
                # Supprime seulement le contenu
                for element in os.listdir(photo_path):
                    chemin_element = os.path.join(photo_path, element)
                    if os.path.isfile(chemin_element) or os.path.islink(chemin_element):
                        os.remove(chemin_element)
                    elif os.path.isdir(chemin_element):
                        shutil.rmtree(chemin_element)
        if self.ui.checkBox_demande.isChecked() == True:
            QMessageBox.information(self,"Réinitialisation","Voulez-vous vraiment supprimer toutes les demandes ? Cette action est irréversible.")
            tables.append("demande")   
        if self.ui.checkBox_carriere.isChecked() == True:
            QMessageBox.information(self,"Réinitialisation","Voulez-vous vraiment supprimer les carrières ? Cette action est irréversible.")
            tables.append("suivi_carriere")
        if self.ui.checkBox_parametrage.isChecked() == True:
            QMessageBox.information(self,"Réinitialisation","Voulez-vous vraiment supprimer les données de paramétrage ? Cette action est irréversible.")
            tables += ["liste_demande","liste_service","liste_statut","liste_fonction","liste_categorie_professionnelle","liste_grade","liste_autre_responsabilite"]
        
        if tables != [] and QMessageBox.warning(self,"Finalisation du processus de réinitialisation","Je souhaite poursuivre !",QMessageBox.No | QMessageBox.Yes) == QMessageBox.Yes:
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
            QMessageBox.information(self,"Réinitialisation","Les données sélectionnées ont été vidées.")
                
        conn.commit()
        conn.close()

