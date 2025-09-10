import sqlite3
import os
from  utils import utilitaires
from views.fenetre_chercher_personnel import FenetreChercherPersonnel
from class_ui.fenetre_profil_personnel_ui import Ui_FenetreProfilPersonnel
from views.fenetre_suivi_carriere import FenetreSuiviCarriere
from views.fenetre_demande import FenetreDemande
from views.fenetre_parametre_dossier import FenetreParametreDossier
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
from utils.utilitaires import resource_path
import time
import shutil


class FenetreProfilPersonnel(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetreProfilPersonnel()
        self.ui.setupUi(self)
        self.db_path = resource_path("data/database.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.photo_path = ""
        
        self.cursor.execute('SELECT path FROM file_path WHERE file_type = ? ORDER BY id DESC LIMIT 1',('photo',))
        self.existing_file = self.cursor.fetchone()
        
        if self.existing_file == None:
            fenetre_dossier = FenetreParametreDossier()
            fenetre_dossier.choisir_dossier()
        else:
            self.photo_path = self.existing_file[0]

        # id
        self.ui.txt_id.setEnabled(False) # vérrouiller l'id
        ## religion
        self.cursor.execute("SELECT religion FROM liste_religion")
        data_religion = self.cursor.fetchall()
        if data_religion != None:
            self.ui.comboBox_religion.addItems([value[0] for value in data_religion])
        self.ui.comboBox_religion.setCurrentIndex(-1) # pas de sélection par défaut
        ## ethnie        
        self.cursor.execute("SELECT ethnie FROM liste_ethnie")
        data_ethnie = self.cursor.fetchall()
        if data_ethnie != None:
            self.ui.comboBox_ethnie.addItems([value[0] for value in data_ethnie])        
            self.ui.comboBox_ethnie.setCurrentIndex(-1) # pas de sélection par défaut
        ## nationalité
        self.cursor.execute("SELECT pays FROM liste_pays")
        data_pays = self.cursor.fetchall()
        if data_pays != None:
            self.ui.comboBox_nationalite.addItems([value[0] for value in data_pays])
        self.ui.comboBox_nationalite.setCurrentIndex(-1)
        #sexe
        self.cursor.execute("SELECT sexe FROM liste_sexe")
        data_sexe = self.cursor.fetchall()
        if data_sexe != None:
            self.ui.comboBox_sexe.addItems([value[0] for value in data_sexe])
        self.ui.comboBox_sexe.setCurrentIndex(-1)
        #photo
        self.ui.txt_url_photo.setEnabled(False)
        # sit matrimoniale
        self.ui.comboBox_situation_matrimoniale.addItems(utilitaires.situations_matrimoniales)
        self.ui.comboBox_situation_matrimoniale.setCurrentIndex(-1)
        # banque
        self.cursor.execute("SELECT banque FROM liste_banque")
        data_banque = self.cursor.fetchall()
        if data_banque != None:
            self.ui.comboBox_banque.addItems([value[0] for value in data_banque])
        self.ui.comboBox_banque.setCurrentIndex(-1)
        # personnel actif
        self.ui.comboBox_personnel_actif.addItems(["Oui","Non"])
        self.ui.comboBox_personnel_actif.setCurrentIndex(-1)
        
        # boutons
        self.ui.btn_ajouter.clicked.connect(self.ajouter_personnel)
        self.ui.btn_supprimer.clicked.connect(self.supprimer_personnel)
        self.ui.btn_nouveau.clicked.connect(self.initialiser_formulaire)
        self.ui.btn_modifier.clicked.connect(self.modifier_personnel)
        self.ui.btn_uploader_photo.clicked.connect(self.uploader_photo)
        self.ui.btn_faire_demande.clicked.connect(self.faire_une_demande)
        self.ui.btn_suivi_carriere.clicked.connect(self.suivi_carriere)
        self.ui.btn_chercher_personnel.clicked.connect(self.chercher_personnel)
        
    def valider_formulaire(self):
        try:
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
            banque = self.ui.comboBox_banque.currentText()
            numero_rib = self.ui.txt_rib.text()
            personnel_actif = self.ui.comboBox_personnel_actif.currentText()

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
            elif banque == "":
                erreur.append("La banque doit être renseignée. Veuillez corriger!")
                self.ui.comboBox_banque.setStyleSheet("border: 1px solid red;")
            elif numero_rib == "":
                erreur.append("Le numéro du compte bancaire (Numéro RIB) doit être renseigné. Veuillez corriger!")
                self.ui.txt_rib.setStyleSheet("border: 1px solid red;")
            elif personnel_actif == "":
                erreur.append("Vous devez préciser si le personnel est toujours en fonction. Veuillez corriger!")
                self.ui.comboBox_personnel_actif.setStyleSheet("border: 1px solid red;")
                    
            if not erreur == []:
                QMessageBox.critical(self,"Validité du formulaire","Champs manquants.\n" + erreur[0])
            return(erreur == [])
        except Exception as e:
            print(e)
        
        
    def ajouter_personnel(self):
        
        try:
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
            banque = self.ui.comboBox_banque.currentText()
            numero_rib = self.ui.txt_rib.text()
            personnel_actif = self.ui.comboBox_personnel_actif.currentText()
            date_creation = datetime.today()
            date_modification = datetime.today()

            reponse = QMessageBox.information(
                self,"Enregistrement","Voulez-vous enregistrer cette personne.",QMessageBox.Yes,QMessageBox.No
            )
            
            if reponse == QMessageBox.Yes:
                if  self.valider_formulaire() == True:
                    
                    # test pour evaluer l'existance du npi et du matricule dans la base
                    req = "SELECT * FROM personnel WHERE matricule = ? OR npi = ?"
                    self.cursor.execute(req,(matricule,npi,))
                    data = self.cursor.fetchone()
                    
                    if data != None:
                        QMessageBox.warning(self,"Validité",f"Le NPI {npi} ou le Matricule {matricule} sont déjà utilisés !")
                    else:
                        req = """
                            INSERT INTO personnel (
                                npi, matricule, nom, prenom, date_naissance, sexe,
                                situation_matrimoniale, religion, ethnie, nationalite,
                                telephone1, telephone2, email, adresse, url_photo,
                                numero_ifu, numero_cnss, banque, numero_rib, personnel_actif,
                                date_creation, date_modification
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """
                        self.cursor.execute(req, (
                            npi, matricule, nom, prenom, date_naissance, sexe,
                            situation_matrimoniale, religion, ethnie, nationalite,
                            telephone1, telephone2, email, adresse, url_photo,
                            numero_ifu, numero_cnss, banque, numero_rib,personnel_actif,
                            date_creation, date_modification,
                        ))
                    
                        self.conn.commit()
                        
                        # vérification d'ajout
                        if self.cursor.rowcount > 0: # verifier sur une ligne  est affecté à la table
                            QMessageBox.information(self,"Enregistrement","Succès !")
                            self.initialiser_formulaire()
                        else:
                            QMessageBox.critical(self,"Enregistrement","Echec d'enregistrement !")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

        finally:
            print(0)
        

    def supprimer_personnel(self): 
        try:
            id = self.ui.txt_id.text()  
            matricule = self.ui.txt_matricule.text()
            
            if id == "":
                QMessageBox.critical(self, "Individu non trouvé. Impossible de supprimer.")
            else:
                reponse = QMessageBox.question(
                    None,
                    "Confirmation",
                    f"Voulez-vous vraiment supprimer le matricule [{matricule}] ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                int_id = int(id)
                
                if reponse == QMessageBox.Yes:
                    req = "DELETE FROM personnel WHERE id = ?;"
                    self.cursor.execute(req,(int_id,))
                    self.conn.commit()
                    
            self.initialiser_formulaire()
        except Exception as e:
            print(e)
            

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
        self.ui.comboBox_banque.setCurrentIndex(-1)
        self.ui.comboBox_personnel_actif.setCurrentIndex(-1)

        # Réinitialisation de la date de naissance à aujourd’hui
        self.ui.dateEdit_date_naissance.setDate(QDate.currentDate())
        self.ui.photo.setPixmap(QPixmap(""))
        self.ui.photo.setScaledContents(True)


    def modifier_personnel(self):
        try:
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
            banque = self.ui.comboBox_banque.currentText()
            numero_rib = self.ui.txt_rib.text()
            personnel_actif = self.ui.comboBox_personnel_actif.currentText()
            date_creation = datetime.today()
            date_modification = datetime.today()
            
            if id != "":
                id = int(id)
                reponse = QMessageBox.question(
                    self,
                    "Confirmation",
                    f"Voulez-vous vraiment modifier l'employé avec le matricule [{matricule}] ?",
                    QMessageBox.Yes | QMessageBox.No
                )
                    
                if reponse == QMessageBox.Yes:
                    if  self.valider_formulaire() == True:
                        
                        # test pour evaluer l'existance du npi et du matricule dans la base
                        req = "SELECT * FROM personnel WHERE (matricule = ? OR npi = ?) AND id <> ?"
                        self.cursor.execute(req,(matricule,npi,id,))
                        data = self.cursor.fetchone()
                        
                        if data != None:
                            QMessageBox.warning(self,"Validité",f"Le NPI {npi} ou le Matricule {matricule} sont déjà utilisés !")
                        else:   
                            req = """
                                UPDATE personnel SET
                                matricule = ?, npi = ?, nom = ?, prenom = ?, sexe = ?, date_naissance = ?, 
                                situation_matrimoniale = ?, religion = ?, ethnie = ?, nationalite = ?, telephone1 = ?, 
                                telephone2 = ?, adresse = ?, email = ?, url_photo = ?, numero_ifu = ?, numero_cnss = ?, 
                                banque = ?, numero_rib = ?, personnel_actif = ?, date_modification = ? WHERE id = ?;
                            """
                            self.cursor.execute(req, ( matricule, npi, nom, prenom, sexe, date_naissance, situation_matrimoniale, 
                                                religion, ethnie, nationalite, telephone1, telephone2, adresse, email, 
                                                url_photo, numero_ifu, numero_cnss, banque, numero_rib, personnel_actif, date_modification, id,
                            ))
                            QMessageBox.information(self,"Vérification","Modification éffectuée !")                                            
                            self.conn.commit()
                            self.initialiser_formulaire()

        
        except Exception as e:
            print(e)
            
        

    def uploader_photo(self):
        nom_unique_fichier = ""
        original_path = QFileDialog.getOpenFileName(
            None,
            caption = "Sélectionner image",
            directory= "",
            filter= "image (*.png *.jpg *.bmp *.gif *.jpeg)",
            options= QFileDialog.Option())[0]
        
        if original_path:
            chemin_fichier = resource_path(original_path)
            
            if len(chemin_fichier) > 0:
                L = chemin_fichier.split(".")
                extension_fichier = "." + L[-1]
                nom_unique_fichier = str(time.time()) + extension_fichier

                nom_unique_fichier = str(time.time()) + extension_fichier
                chemin_destination = self.photo_path +"/"+ nom_unique_fichier

                # Copie avec renommage
                shutil.copy2(chemin_fichier, chemin_destination)
            
            if nom_unique_fichier != "":
                self.ui.txt_url_photo.setText(chemin_destination)
    


    def faire_une_demande(self):
        id = self.ui.txt_id.text()
        if id != "":
            self.fenetre_demande = FenetreDemande()
            self.fenetre_demande.ui.txt_id_personnel.setText(id)
            self.fenetre_demande.exec_()
        else:
            QMessageBox.information(self,"Demande","Veuillez sélectionner un membre du personnel.")
        
        
    def suivi_carriere(self):
        id = self.ui.txt_id.text()
        if id == "":
            QMessageBox.information(self,"Suivi carrière","Veuillez sélectionner un membre du personnel.")
        else:
            fenetre = FenetreSuiviCarriere()
            fenetre.ui.txt_id_personnel.setText(id)
            fenetre.afficher_table_suivi_carriere()
            #fenetre.ui.btn_chercher_employe.setEnabled(False)
            fenetre.exec_()
            
        
    def chercher_personnel(self):
        try:
            self.fenetre = FenetreChercherPersonnel()
            self.fenetre.exec_()
            self.fenetre.setFocus()
            self.ui.txt_id.setText(self.fenetre.id_selectionne)
 
            personnel_id = int(self.fenetre.id_selectionne)
            req = "SELECT * FROM  personnel WHERE id = ?"
            self.cursor.execute(req,(personnel_id,))
            result = self.cursor.fetchone()
            
            if result != None:
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
                self.ui.comboBox_banque.setCurrentText(result[18])
                self.ui.txt_rib.setText(result[19])
                self.ui.comboBox_personnel_actif.setCurrentText(result[20])
                
        except Exception as e:
            print(e)
        
        
        