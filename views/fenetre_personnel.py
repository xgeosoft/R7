import sqlite3
import os
from  utils import utilitaires
from class_ui.fenetre_personnel_ui import Ui_FenetrePersonnel
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
import time
import shutil


class FenetrePersonnel(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetrePersonnel()
        self.ui.setupUi(self)
        self.ncol_tableWidget_ui = 21
        
        # initialisation du formulaire
        #nom
        #self.ui.txt_nom.setInputMask(">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        # id
        self.ui.txt_id.setEnabled(False) # vérrouiller l'id
        ## religion
        self.ui.comboBox_religion.addItems(utilitaires.liste_religions)
        self.ui.comboBox_religion.setCurrentIndex(-1) # pas de sélection par défaut
        ## ethnie        
        self.ui.comboBox_ethnie.addItems(utilitaires.groupes_ethniques_benin)
        self.ui.comboBox_ethnie.setCurrentIndex(-1) # pas de sélection par défaut
        ## nationalité
        self.ui.comboBox_nationalite.addItems(utilitaires.pays_liste_fr)
        #sexe
        self.ui.comboBox_sexe.setCurrentIndex(-1)
        # sit matrimoniale
        self.ui.comboBox_situation_matrimoniale.addItems(utilitaires.situations_matrimoniales)
        self.ui.comboBox_situation_matrimoniale.setCurrentIndex(-1)
        # boutons
        self.ui.btn_quitter.clicked.connect(self.quitter_formulaire)
        self.ui.btn_ajouter.clicked.connect(self.ajouter_personnel)
        self.ui.btn_chercher.clicked.connect(self.chercher_personnel)
        self.ui.btn_supprimer.clicked.connect(self.supprimer_personnel)
        self.ui.btn_nouveau.clicked.connect(self.initialiser_formulaire)
        self.ui.btn_afficher_tout.clicked.connect(self.afficher_table_personnel)
        self.ui.btn_modifier.clicked.connect(self.modifier_personnel)
        self.ui.btn_uploader_photo.clicked.connect(self.uploader_photo)
        
        self.ui.tableWidget_personnel.itemSelectionChanged.connect(self.selectionner_personnel)
        
        #fonctions
    def quitter_formulaire(self):
        self.close()
        
    def valider_formulaire(self,pour_ajout = True):
        erreur = []
        matricule = self.ui.txt_matricule.text()
        npi = self.ui.txt_npi.text()
        nom = self.ui.txt_nom.text()
        prenom = self.ui.txt_prenom.text()
        sexe = self.ui.comboBox_sexe.currentText()
        date_naissance = self.ui.dateEdit_date_naissance.date().toString("yyyy-MM-dd")
        situation_matrimoniale = self.ui.comboBox_situation_matrimoniale.currentText()
        religion = self.ui.comboBox_religion.currentText()
        ethnie = self.ui.comboBox_ethnie.currentText()
        nationalite = self.ui.comboBox_nationalite.currentText()
        telephone1 = self.ui.txt_telephone1.text()
        telephone2 = self.ui.txt_telephone2.text()
        adresse = self.ui.txt_adresse.text()
        email = self.ui.txt_email.text()
        url_photo = self.ui.txt_url_photo.text()
        numero_ifu = self.ui.txt_ifu.text()
        numero_cnss = self.ui.txt_cnss.text()
        numero_rib = self.ui.txt_rib.text()
        
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()        
        
        if matricule == "":
            erreur.append("Le matricule de cet employé est vide. Veuillez corriger!")
            self.ui.txt_matricule.setStyleSheet("border: 1px solid red;")
        elif npi == "":
            erreur.append("Le numéro NPI n'est pas renseigné. Veuillez corriger!")
            self.ui.txt_npi.setStyleSheet("border: 1px solid red;")
        elif nom == "":
            erreur.append("Le nom n'est pas renseigné. Veuillez corriger!")
        elif prenom == "":
            erreur.append("Le prénom n'est pas renseigné. Veuillez corriger!")
        elif sexe == "":
            erreur.append("Le sexe n'est pas renseigné. Veuillez corriger!")
        elif situation_matrimoniale == "":
            erreur.append("La situation matrimoniale n'est pas renseigné. Veuillez corriger!")
        elif nationalite == "":
            erreur.append("La nationalité n'est pas renseigné. Veuillez corriger!")
        elif telephone1 == "":
            erreur.append("Le premier numéro de téléphone doit être renseigné. Veuillez corriger!")
        elif adresse == "":
            erreur.append("Le lieu de résidence (adresse) doit être renseigné. Veuillez corriger!")
        elif numero_ifu == "":
            erreur.append("L'identifiant fiscale unique (IFU) doit être renseigné. Veuillez corriger!")
            self.ui.txt_ifu.setStyleSheet("border: 1px solid red;")
        elif numero_rib == "":
            erreur.append("Le numéro du compte bancaire (Numéro RIB) doit être renseigné. Veuillez corriger!")
            self.ui.txt_rib.setStyleSheet("border: 1px solid red;")

        if matricule != "" and pour_ajout == True:
            req = "SELECT * FROM personnel WHERE matricule = ?"
            cursor.execute(req,(matricule,))
            data = cursor.fetchone()
            if not data is None:
                erreur.append("Ce matricule est déjà utilisé pour l'individu nommé " + data[3] + ". Veuillez corriger!")
                
        if npi != "" and pour_ajout == True:
            req = "SELECT * FROM personnel WHERE npi = ?"
            cursor.execute(req,(npi,))
            data = cursor.fetchone()
            if not data is None:
                erreur.append("Ce numéro NPI est déjà utilisé pour" + data[3] + ". Veuillez corriger!")
                
        if not erreur == []:
            msg = QMessageBox()
            msg.setWindowTitle("Validation")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Champs manquants.\n" + erreur[0])
            msg.exec_()
        return(erreur == [])
        
        
    def ajouter_personnel(self):
        
        try:
            conn = sqlite3.connect("data/database.db")
            cursor = conn.cursor()
            
            id = self.ui.txt_id.text()
            matricule = self.ui.txt_matricule.text()
            npi = self.ui.txt_npi.text()
            nom = self.ui.txt_nom.text()
            prenom = self.ui.txt_prenom.text()
            sexe = self.ui.comboBox_sexe.currentText()
            date_naissance = self.ui.dateEdit_date_naissance.date().toString("yyyy-MM-dd")
            situation_matrimoniale = self.ui.comboBox_situation_matrimoniale.currentText()
            religion = self.ui.comboBox_religion.currentText()
            ethnie = self.ui.comboBox_ethnie.currentText()
            nationalite = self.ui.comboBox_nationalite.currentText()
            telephone1 = self.ui.txt_telephone1.text()
            telephone2 = self.ui.txt_telephone2.text()
            adresse = self.ui.txt_adresse.text()
            email = self.ui.txt_email.text()
            url_photo = self.ui.txt_url_photo.text()
            numero_ifu = self.ui.txt_ifu.text()
            numero_cnss = self.ui.txt_cnss.text()
            numero_rib = self.ui.txt_rib.text()
            date_creation = datetime.today()
            date_modification = datetime.today()

            if  self.valider_formulaire() == True:
                req = """
                    INSERT INTO personnel (
                        npi, matricule, nom, prenom, date_naissance, sexe,
                        situation_matrimoniale, religion, ethnie, nationalite,
                        telephone1, telephone2, email, adresse, url_photo,
                        numero_ifu, numero_cnss, numero_rib,
                        date_creation, date_modification
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                cursor.execute(req, (
                    npi, matricule, nom, prenom, date_naissance, sexe,
                    situation_matrimoniale, religion, ethnie, nationalite,
                    telephone1, telephone2, email, adresse, url_photo,
                    numero_ifu, numero_cnss, numero_rib,
                    date_creation, date_modification
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
                
                self.ui.tableWidget_personnel.clearContents() # effacer le visuel de la table et réactualiser
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

        finally:
            conn.close()
            self.ui.tableWidget_personnel.clearContents()
            self.afficher_table_personnel()
        
        


    def afficher_table_personnel(self):
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()
        
        # sélectionner données
        req = """SELECT * FROM personnel ORDER BY id DESC"""
        cursor.execute(req)
        data = cursor.fetchall() # recupérer les données
        conn.close()
        
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
                conn = sqlite3.connect("data/database.db")
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

    def supprimer_personnel(self):  
        id = self.ui.txt_id.text()  
        matricule = self.ui.txt_matricule.text()
        
        if id == "":
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle("Suppression")
            msgbox.setText("Individu non trouvé. Impossible de supprimer.")
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
                self.ui.tableWidget_personnel.clearContents() # effacer le visuel de la table et réactualiser
                self.initialiser_formulaire()
            

    def initialiser_formulaire(self):
        # Réinitialisation des champs texte
        self.ui.txt_id.setText("")
        self.ui.txt_matricule.setText("")
        self.ui.txt_npi.setText("")
        self.ui.txt_nom.setText("")
        self.ui.txt_prenom.setText("")
        self.ui.txt_telephone1.setText("")
        self.ui.txt_telephone2.setText("")
        self.ui.txt_adresse.setText("")
        self.ui.txt_email.setText("")
        self.ui.txt_url_photo.setText("")
        self.ui.txt_ifu.setText("")
        self.ui.txt_cnss.setText("")
        self.ui.txt_rib.setText("")

        # Réinitialisation des ComboBox (remettre au premier élément)
        self.ui.comboBox_sexe.setCurrentIndex(-1)
        self.ui.comboBox_situation_matrimoniale.setCurrentIndex(-1)
        self.ui.comboBox_religion.setCurrentIndex(-1)
        self.ui.comboBox_ethnie.setCurrentIndex(-1)
        self.ui.comboBox_nationalite.setCurrentIndex(-1)

        # Réinitialisation de la date de naissance à aujourd’hui
        self.ui.dateEdit_date_naissance.setDate(QDate.currentDate())
          
        pixmap = QPixmap("")
        self.ui.photo.setPixmap(pixmap)
        self.ui.photo.setScaledContents(True)


    def modifier_personnel(self):
        
        id = self.ui.txt_id.text()
        matricule = self.ui.txt_matricule.text()
        npi = self.ui.txt_npi.text()
        nom = self.ui.txt_nom.text()
        prenom = self.ui.txt_prenom.text()
        sexe = self.ui.comboBox_sexe.currentText()
        date_naissance = self.ui.dateEdit_date_naissance.date().toString("yyyy-MM-dd")
        situation_matrimoniale = self.ui.comboBox_situation_matrimoniale.currentText()
        religion = self.ui.comboBox_religion.currentText()
        ethnie = self.ui.comboBox_ethnie.currentText()
        nationalite = self.ui.comboBox_nationalite.currentText()
        telephone1 = self.ui.txt_telephone1.text()
        telephone2 = self.ui.txt_telephone2.text()
        adresse = self.ui.txt_adresse.text()
        email = self.ui.txt_email.text()
        url_photo = self.ui.txt_url_photo.text()
        numero_ifu = self.ui.txt_ifu.text()
        numero_cnss = self.ui.txt_cnss.text()
        numero_rib = self.ui.txt_rib.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()
        
        if not id == "":
            id = int(id)
            reponse = QMessageBox.question(
                None,
                "Confirmation",
                f"Voulez-vous vraiment modifier l'employé avec le matricule [{matricule}] ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reponse == QMessageBox.Yes:
                if self.valider_formulaire(pour_ajout=False) == True: # verifier si erreur est 0
                    req = "SELECT * FROM personnel WHERE (npi = ? OR matricule = ?) AND id <> ?"
                    cursor.execute(req,(npi,matricule,id,)) # voir si il y a un autre id avec le meme matricule ou npi
                    data = cursor.fetchone()
                    
                    if data is None: # si une autre personne avec les infos clées n'existe pas
                        msgbox = QMessageBox()
                        msgbox.setIcon(QMessageBox.Information)
                        msgbox.setWindowTitle("Vérification")
                        msgbox.setText("Modification éffectuée !")
                        msgbox.exec_()
                        req = """
                            UPDATE personnel SET
                            matricule = ?,
                            npi = ?,
                            nom = ?,
                            prenom = ?,
                            sexe = ?,
                            date_naissance = ?,
                            situation_matrimoniale = ?,
                            religion = ?,
                            ethnie = ?,
                            nationalite = ?,
                            telephone1 = ?,
                            telephone2 = ?,
                            adresse = ?,
                            email = ?,
                            url_photo = ?,
                            numero_ifu = ?,
                            numero_cnss = ?,
                            numero_rib = ?,
                            date_modification = ?
                            WHERE id = ?;
                        """
                        cursor.execute(req, (
                            matricule,
                            npi,
                            nom,
                            prenom,
                            sexe,
                            date_naissance,
                            situation_matrimoniale,
                            religion,
                            ethnie,
                            nationalite,
                            telephone1,
                            telephone2,
                            adresse,
                            email,
                            url_photo,
                            numero_ifu,
                            numero_cnss,
                            numero_rib,
                            date_modification,
                            id
                        ))
                        conn.commit()
                        conn.close()
            self.ui.tableWidget_personnel.clearContents() # effacer le visuel de la table et réactualiser
            self.initialiser_formulaire()
            
        


    def selectionner_personnel(self):
        item_selectionnee = self.ui.tableWidget_personnel.selectedItems()
        row_data = [item.text() for item in item_selectionnee]

        if len(row_data) == self.ncol_tableWidget_ui:
            personnel_id = row_data[0]
            conn = sqlite3.connect("data/database.db")
            cursor = conn.cursor()
            req = "SELECT * FROM  personnel WHERE id = ?"
            cursor.execute(req,(personnel_id))
            result = cursor.fetchone()

            pixmap = QPixmap(result[15])
            self.ui.photo.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.ui.photo.setScaledContents(True)
            
            
            # afficher les informations généraux
            self.ui.txt_id.setText(str(result[0]))
            self.ui.txt_matricule.setText(result[1])
            self.ui.txt_npi.setText(result[2])
            self.ui.txt_nom.setText(result[3])
            self.ui.txt_prenom.setText(result[4])
            self.ui.comboBox_sexe.setCurrentText(result[5])
            self.ui.dateEdit_date_naissance.setDate(QDate.fromString(result[6], "yyyy-MM-dd"))
            self.ui.comboBox_situation_matrimoniale.setCurrentText(result[7])
            self.ui.comboBox_religion.setCurrentText(result[8])
            self.ui.comboBox_ethnie.setCurrentText(result[9])
            self.ui.comboBox_nationalite.setCurrentText(result[10])
            self.ui.txt_telephone1.setText(result[11])
            self.ui.txt_telephone2.setText(result[12])
            self.ui.txt_adresse.setText(result[13])
            self.ui.txt_email.setText(result[14])
            self.ui.txt_url_photo.setText(result[15])
            self.ui.txt_ifu.setText(result[16])
            self.ui.txt_cnss.setText(result[17])
            self.ui.txt_rib.setText(result[18])


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

            nom_unique_fichier = str(time.time()) + extension_fichier
            chemin_destination = "images/photos/" + nom_unique_fichier

            # Copie avec renommage
            shutil.copy2(chemin_fichier[0], chemin_destination)
        
        if nom_unique_fichier != "":
            self.ui.txt_url_photo.setText(chemin_destination)
    

