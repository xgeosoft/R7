# views/personnel_window.py
from PyQt5.QtWidgets import QMainWindow,QMessageBox,QTableWidgetItem,QFileDialog
from class_ui.personnel_ui import Ui_Personnel  # Interface générée de la fenêtre Personnel

import sqlite3
from datetime import datetime
import time
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDate

class FenetrePersonnel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Personnel()
        self.ui.setupUi(self)

        #def ouvrir_personnel_app(self.ui: self.ui_Form):
        self.ncol_tableWidget_ui = 15 # ncol table ui
        
        self.ui.lineEdit_id.setEnabled(False) # protection case id

        self.ui.pushButton_ajouter.clicked.connect(self.ajouter_personnel)
        self.ui.pushButton_uploader.clicked.connect(self.uploader_photo)
        self.ui.tableWidget_affichage.itemSelectionChanged.connect(self.selectionner_personne)
        self.ui.pushButton_nouveau.clicked.connect(self.nouvelle_enregistrement)
        self.ui.pushButton_modifier.clicked.connect(self.modifier_enregistrement)
        self.ui.pushButton_supprimer.clicked.connect(self.supprimer_enregistrement)
        self.ui.pushButton_chercher.clicked.connect(self.chercher_enregistrement)
        self.ui.pushButton_afficher_tout.clicked.connect(self.afficher_tout_enregistrement)
        

    def ajouter_personnel(self):
        self.insert_personnel_data()
        
    def uploader_photo(self):
        photo = self.uploader_photo()
        self.ui.lineEdit_chemin_photo.setText(photo)
        
    def selectionner_personne(self):
        self.selectionner_personnel()
        
    def nouvelle_enregistrement(self):
        self.initialiser_formulaire()
        
    def modifier_enregistrement(self):
        self.modifier_personnel()
        
    def supprimer_enregistrement(self):
        self.supprimer_personnel()
        
    def chercher_enregistrement(self):
        self.chercher_personnel()
        
    def afficher_tout_enregistrement(self):
        self.afficher_table_personnel()
    

    # EXECUTION

    def insert_personnel_data(self):
        npi = self.ui.lineEdit_npi.text()
        matricule = self.ui.lineEdit_matricule.text()
        nom = self.ui.lineEdit_nom.text()
        prenom = self.ui.lineEdit_prenom.text()
        date_naissance = self.ui.dateEdit_date_naissance.date().toString("yyyy-MM-dd")
        sexe = self.ui.comboBox_sexe.currentText()
        religion = self.ui.comboBox_religion.currentText()
        telephone1 = self.ui.lineEdit_tel1.text()
        telephone2 = self.ui.lineEdit_tel2.text()
        email = self.ui.lineEdit_email.text()
        adresse = self.ui.lineEdit_adresse.text()
        photo = self.ui.lineEdit_chemin_photo.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()

        if self.formulaire_completement_rempli() == 0: # verifier si erreur est 0
            # Vérification si l'individu existe
            req = "SELECT * FROM personnel WHERE matricule = ?"
            cursor.execute(req,(matricule,))
            data = cursor.fetchone()

            if data is not None: # existe
                msgbox = QMessageBox()
                msgbox.setIcon(QMessageBox.Critical)
                msgbox.setWindowTitle("Vérification")
                msgbox.setText("Ce matricule est déjà enregistré !")
                msgbox.exec_()
            else:    
                req = """INSERT INTO personnel (npi,matricule,nom,prenom,date_naissance,sexe,religion,telephone1,telephone2,email,adresse,photo,date_creation,date_modification)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
                
                cursor.execute(req,(npi,matricule,nom,prenom,date_naissance,sexe,religion,telephone1,telephone2,email,adresse,photo,date_creation,date_modification))
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
                
                self.ui.tableWidget_affichage.clearContents() # effacer le visuel de la table et réactualiser
                
        self.initialiser_formulaire()
        conn.close()
        
        
    def afficher_table_personnel(self):
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()
        
        # sélectionner données
        req = """SELECT * FROM personnel ORDER BY ID DESC"""
        cursor.execute(req)
        data = cursor.fetchall() # recupérer les données
        conn.close()
        
        row_index = 0
        for row in data:
            for col in range(self.ncol_tableWidget_ui): #afficher toes les colonnes
                self.ui.tableWidget_affichage.setItem(row_index,col,QTableWidgetItem(str(row[col])))
            row_index = row_index + 1
            
            
            
    def uploader_photo(self):
        nom_unique_fichier = ""
        chemin_fichier = QFileDialog.getOpenFileName(
            None,
            caption = "Sélectionner image",
            directory= "",
            filter= "image (*.png *.jpg *.bmp *.gif *.jpeg)",
            options= QFileDialog.Option()
        )
        
        if len(chemin_fichier[0]) > 0:
            L = chemin_fichier[0].split(".")
            extension_fichier = "." + L[-1]
            nom_unique_fichier = str(time.time()) + extension_fichier
            os.rename(chemin_fichier[0],"images/photos/"+nom_unique_fichier)
        
        return nom_unique_fichier


    def selectionner_personnel(self):
        item_selectionnee = self.ui.tableWidget_affichage.selectedItems()
        row_data = [item.text() for item in item_selectionnee]

        if len(row_data) == self.ncol_tableWidget_ui:
            personnel_id = row_data[0]
            conn = sqlite3.connect("data/database.db")
            cursor = conn.cursor()
            req = "SELECT * FROM  personnel WHERE id = ?"
            cursor.execute(req,(personnel_id))
            result = cursor.fetchone()

            pixmap = QPixmap("images/photos/"+result[11])
            self.ui.label_photo_visualiser.setPixmap(pixmap)
            self.ui.label_photo_visualiser.setScaledContents(True)
            
            # afficher les informations généraux
            self.ui.lineEdit_id.setText(str(result[0]))
            self.ui.lineEdit_npi.setText(result[1])
            self.ui.lineEdit_matricule.setText(result[2])
            self.ui.lineEdit_nom.setText(result[3])
            self.ui.lineEdit_prenom.setText(result[4])
            self.ui.dateEdit_date_naissance.setDate(QDate.fromString(result[5],"yyyy-MM-dd"))  # lui permet de reconnaitre le format de date
            self.ui.comboBox_sexe.setCurrentText(result[6])
            self.ui.comboBox_religion.setCurrentText(result[7])
            self.ui.lineEdit_tel1.setText(result[8])
            self.ui.lineEdit_tel2.setText(result[9])
            self.ui.lineEdit_email.setText(result[10])
            self.ui.lineEdit_adresse.setText(result[11])
            self.ui.lineEdit_chemin_photo.setText(result[12])

    def initialiser_formulaire(self):
        self.ui.lineEdit_id.setEnabled(False)
        self.ui.lineEdit_id.setText("")
        self.ui.lineEdit_npi.setText("")
        self.ui.lineEdit_matricule.setText("")
        self.ui.lineEdit_nom.setText("")
        self.ui.lineEdit_prenom.setText("")
        self.ui.dateEdit_date_naissance.setDate(QDate.currentDate())
        self.ui.comboBox_sexe.setCurrentText("")
        self.ui.comboBox_religion.setCurrentText("")
        self.ui.lineEdit_tel1.setText("")
        self.ui.lineEdit_tel2.setText("")
        self.ui.lineEdit_email.setText("")
        self.ui.lineEdit_adresse.setText("")
        self.ui.lineEdit_chemin_photo.setText("")
        self.ui.label_photo_visualiser.setPixmap(QPixmap(""))
        self.ui.lineEdit_npi.setFocus()


    def formulaire_completement_rempli(self):
        erreur = 0
        erreur += int(self.ui.lineEdit_matricule.text() == "")
        erreur += int(self.ui.lineEdit_nom.text() == "")
        erreur += int(self.ui.dateEdit_date_naissance.date() == "")
        erreur += int(self.ui.lineEdit_tel1.text == "")
        return erreur

        
    def modifier_personnel(self):
        id = self.ui.lineEdit_id.text()
        npi = self.ui.lineEdit_npi.text()
        matricule = self.ui.lineEdit_matricule.text()
        nom = self.ui.lineEdit_nom.text()
        prenom = self.ui.lineEdit_prenom.text()
        date_naissance = self.ui.dateEdit_date_naissance.date().toString("yyyy-MM-dd")
        sexe = self.ui.comboBox_sexe.currentText()
        religion = self.ui.comboBox_religion.currentText()
        telephone1 = self.ui.lineEdit_tel1.text()
        telephone2 = self.ui.lineEdit_tel2.text()
        email = self.ui.lineEdit_email.text()
        adresse = self.ui.lineEdit_adresse.text()
        photo = self.ui.lineEdit_chemin_photo.text()
        date_modification = datetime.today()
        
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()

        if self.formulaire_completement_rempli() == 0: # verifier si erreur est 0
            # Vérification si l'individu existe
            req = "SELECT * FROM personnel WHERE id = ?"
            cursor.execute(req,(id,))
            data = cursor.fetchone()
            id = int(id)
            
            reponse = QMessageBox.question(
                None,
                "Confirmation",
                f"Voulez-vous vraiment modifier l'employé avec le matricule [{matricule}] ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if data is not None and reponse == QMessageBox.Yes:  # on s'assure que id existeS
                req = "SELECT * FROM personnel WHERE matricule = ?"
                cursor.execute(req,(matricule,)) # voir si le matricule modifié existe déjà
                data = cursor.fetchone()
                
                if data is not None: # si matricule existe déjà
                    msgbox = QMessageBox()
                    msgbox.setIcon(QMessageBox.Information)
                    msgbox.setWindowTitle("Vérification")
                    msgbox.setText("Matricule existe déjà. Mise à jour éffectuée avec succès à l'exception du matricule.")
                    msgbox.exec_()
                    req = """UPDATE personnel SET npi = ?,nom = ?,prenom = ?,date_naissance = ?,sexe = ?,religion = ?,telephone1 = ?,telephone2 = ?,email = ?,adresse = ?,photo = ?,date_modification = ? WHERE id = ?"""
                    cursor.execute(req,(npi,nom,prenom,date_naissance,sexe,religion,telephone1,telephone2,email,adresse,photo,date_modification,id))
                    conn.commit()
                else:
                    req = """UPDATE personnel SET npi = ?,matricule = ?,nom = ?,prenom = ?,date_naissance = ?,sexe = ?,religion = ?,telephone1 = ?,telephone2 = ?,email = ?,adresse = ?,photo = ?,date_modification = ? WHERE id = ?"""
                    cursor.execute(req,(npi,matricule,nom,prenom,date_naissance,sexe,religion,telephone1,telephone2,email,adresse,photo,date_modification,id))
                    conn.commit()
                    # vérification d'ajout
                    msgbox = QMessageBox()
                    msgbox.setIcon(QMessageBox.Information)
                    msgbox.setWindowTitle("Vérification")
                    msgbox.setText("Modification éffectuée !")
                    msgbox.exec_()
                
        self.ui.tableWidget_affichage.clearContents() # effacer le visuel de la table et réactualiser
        self.initialiser_formulaire()
        conn.close()
        

    def supprimer_personnel(self):  
        id = self.ui.lineEdit_id.text()  
        matricule = self.ui.lineEdit_matricule.text()
        
        if id == "":
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle("Suppression")
            msgbox.setText("Champ vide. Impossible de supprimer.")
            msgbox.exec_()
        else:
            reponse = QMessageBox.question(
                None,
                "Confirmation",
                f"Voulez-vous vraiment supprimer la personne avec le matricule [{matricule}] ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reponse == QMessageBox.Yes:
                conn = sqlite3.connect("data/database.db")
                cursor = conn.cursor()
                req = "DELETE FROM personnel WHERE matricule = ?;"
                cursor.execute(req,(matricule,))
                conn.commit()
                conn.close()
                self.ui.tableWidget_affichage.clearContents() # effacer le visuel de la table et réactualiser
                self.initialiser_formulaire()
            

    def chercher_personnel(self):
        valeur_chercher = self.ui.lineEdit_chercher.text()
        self.ui.tableWidget_affichage.clearContents() # effacer le visuel de la table et réactualiser
        
        if len(valeur_chercher) > 0:
            conn = sqlite3.connect("data/database.db")
            cursor = conn.cursor()
            
            # sélectionner données
            valeur_like = f"%{valeur_chercher}%"
            req = "SELECT * FROM personnel WHERE LOWER(npi || nom || prenom || matricule || date_naissance || telephone1 || telephone2 || adresse || email) LIKE ?"
            cursor.execute(req,(valeur_like,))
            data = cursor.fetchall() # recupérer les données
            conn.close()
            
            if len(data) > 0:
                row_index = 0
                for row in data:
                    for col in range(14): #afficher toes les colonnes
                        self.ui.tableWidget_affichage.setItem(row_index,col,QTableWidgetItem(str(row[col])))
                    row_index = row_index + 1
                
        
        