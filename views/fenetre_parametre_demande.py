import sqlite3
import os
from  utils import utilitaires
from class_ui.fenetre_parametre_demande_ui import Ui_ParametreDemande
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
from utils.utilitaires import resource_path
import time
import shutil

class FenetreParametreDemande(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ParametreDemande()
        self.ui.setupUi(self)
        self.ncol_tableWidget_ui = 5
        self.ui.txt_id.setEnabled(False)
        self.db_path = resource_path("data/database.db")

        
        self.ui.comboBox_nombrejours.addItems([str(i) for i in range(1,366)])
        self.ui.comboBox_nombrejours.setCurrentIndex(-1)
        self.ui.btn_ajouter.clicked.connect(self.ajouter_configuration_demande)
        self.ui.tableWidget_affichage.itemSelectionChanged.connect(self.selectionner_type_demande)
        self.ui.btn_afficher_tout.clicked.connect(self.afficher_liste_configuration_demande)
        self.ui.btn_nouveau.clicked.connect(self.initialiser_formulaire)
        self.ui.btn_modifier.clicked.connect(self.modifier_configuration_demande)
        self.ui.btn_supprimer.clicked.connect(self.supprimer_configuration_demande)
    
    def valider_formulaire(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()  
        
        objet = self.ui.txt_objet.text()
        nbjours = self.ui.comboBox_nombrejours.currentText()
        
        erreur = []
        
        if objet != "":
            req = "SELECT * FROM personnel WHERE matricule = ?"
            cursor.execute(req,(objet,))
            data = cursor.fetchone()
            if not data is None:
                erreur.append("Cet objet est déjà utilisé pour l'ID = " + data[0] + ". Veuillez corriger!")
                
        if objet == "":
            erreur.append("L'objet est vide. Veuillez corriger!")
            self.ui.txt_objet.setStyleSheet("border: 1px solid red;")
        elif nbjours == "":
            erreur.append("Le nombre de jours n'est pas renseigné. Veuillez corriger!")
            self.ui.comboBox_nombrejours.setStyleSheet("border: 1px solid red;")
            
        if not erreur == []:
            msg = QMessageBox()
            msg.setWindowTitle("Validation")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Champs manquants.\n" + erreur[0])
            msg.exec_()
        return(erreur == [])
    
    
    def afficher_liste_configuration_demande(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # sélectionner données
        req = """SELECT * FROM liste_demande ORDER BY id DESC"""
        cursor.execute(req)
        data = cursor.fetchall() # recupérer les données
        conn.close()
        
        if data is not None:
            row_index = 0
            for row in data:
                for col in range(self.ncol_tableWidget_ui): #afficher toes les colonnes
                    self.ui.tableWidget_affichage.setItem(row_index,col,QTableWidgetItem(str(row[col])))
                row_index = row_index + 1
    
    def ajouter_configuration_demande(self):
        
        if self.valider_formulaire() == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            id = self.ui.txt_id.text()
            objet = self.ui.txt_objet.text()
            nbjours = self.ui.comboBox_nombrejours.currentText()
            date_creation = datetime.today()
            date_modification = datetime.today()
            
            if id == "":
                req = """
                        INSERT INTO liste_demande (
                            objet, nb_jours,
                            date_creation, date_modification
                        ) VALUES (?, ?, ?, ?);
                    """
                cursor.execute(req, (
                    objet, nbjours,
                    date_creation, date_modification,
                ))
                
                conn.commit()
                    
                # vérification d'ajout
                if cursor.rowcount > 0: # verifier sur une ligne  est affecté à la table
                    msgbox = QMessageBox()
                    msgbox.setIcon(QMessageBox.Information)
                    msgbox.setWindowTitle("Vérification")
                    msgbox.setText("Succès !")
                    msgbox.exec_()
                else:
                    msgbox = QMessageBox()
                    msgbox.setIcon(QMessageBox.Critical)
                    msgbox.setText("Echec d'enregistrement !")
                    msgbox.exec_()
            else:
                QMessageBox.critical(self,"Vérification","Ce type de demande existe déjà.")
        self.afficher_liste_configuration_demande()
    
    
        
    def modifier_configuration_demande(self):
        id = self.ui.txt_id.text()
        objet = self.ui.txt_objet.text()
        nbjours = self.ui.comboBox_nombrejours.currentText()
        date_modification = datetime.today()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if id == "":
            QMessageBox.information(
                None,
                "Alerte",
                f"Aucun élément sélectionné",
                QMessageBox.Close
            )
        else:
            id = int(id)
            reponse = QMessageBox.question(
                None,
                "Confirmation",
                f"Voulez-vous vraiment modifier ce type de demande ID = [{id}] ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reponse == QMessageBox.Yes:
                if self.valider_formulaire() == True: # verifier si erreur est 0
                    req = "SELECT * FROM liste_demande WHERE objet = ? AND id <> ?"
                    cursor.execute(req,(objet,id,)) # voir si il y a un autre id avec le meme matricule ou npi
                    data = cursor.fetchone()
                    
                    if data is None: # si une autre personne avec les infos clées n'existe pas
                        msgbox = QMessageBox()
                        msgbox.setIcon(QMessageBox.Information)
                        msgbox.setWindowTitle("Vérification")
                        msgbox.setText("Modification éffectuée !")
                        msgbox.exec_()
                        req = """
                            UPDATE liste_demande SET
                            objet = ?,
                            nb_jours = ?,
                            date_modification = ?
                            WHERE id = ?;
                        """
                        cursor.execute(req, (
                            objet,
                            nbjours,
                            date_modification,
                            id
                        ))
                        conn.commit()
                        conn.close()
            self.ui.tableWidget_affichage.clearContents() # effacer le visuel de la table et réactualiser
            self.initialiser_formulaire()
            

    def selectionner_type_demande(self):
        item_selectionnee = self.ui.tableWidget_affichage.selectedItems()
        row_data = [item.text() for item in item_selectionnee]

        if len(row_data) == self.ncol_tableWidget_ui:
            personnel_id = row_data[0]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "SELECT * FROM  liste_demande WHERE id = ?"
            cursor.execute(req,(personnel_id))
            result = cursor.fetchone()
            
            # afficher les informations généraux
            self.ui.txt_id.setText(str(result[0]))
            self.ui.txt_objet.setText(result[1])
            self.ui.comboBox_nombrejours.setCurrentText(str(result[2]))
    
    
    def initialiser_formulaire(self):
        # Réinitialisation des champs texte
        self.ui.txt_id.setText("")
        self.ui.txt_objet.setText("")
        self.ui.comboBox_nombrejours.setCurrentIndex(-1)
    
    
    
    def supprimer_configuration_demande(self):  
        id = self.ui.txt_id.text()  
        objet = self.ui.txt_objet.text()
        
        if id == "":
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle("Suppression")
            msgbox.setText("Type de demande non trouvé. Impossible de supprimer.")
            msgbox.exec_()
        else:
            reponse = QMessageBox.question(
                None,
                "Confirmation",
                f"Voulez-vous vraiment supprimer le type de demande = [{objet}] ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reponse == QMessageBox.Yes:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_demande WHERE id = ?;"
                cursor.execute(req,(id,))
                conn.commit()
                conn.close()
                self.ui.tableWidget_affichage.clearContents() # effacer le visuel de la table et réactualiser
                self.initialiser_formulaire()
            