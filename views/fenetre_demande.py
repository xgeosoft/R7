import sqlite3
import os
from  utils import utilitaires
from class_ui.fenetre_demande_ui import Ui_FenetreDemande
from views.fenetre_parametre_demande import FenetreParametreDemande
from views.fenetre_chercher_personnel import FenetreChercherPersonnel
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
from utils.utilitaires import resource_path
import time
import shutil

class FenetreDemande(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetreDemande()
        self.ui.setupUi(self)
        self.ncol_tableWidget_ui = 10
        self.db_path = resource_path("data/database.db")

        
        # id employé
        self.ui.txt_id.setEnabled(False)
        self.ui.txt_id_personnel.setEnabled(False)
        
        # autorisation chef service
        self.ui.comboBox_autorisation_chefservice.setCurrentIndex(-1)
        
        # date
        self.ui.date_debut.setDate(QDate.currentDate())
        self.ui.date_fin.setDate(QDate.currentDate())
        
        self.ui.btn_nouveau.clicked.connect(self.initialiser_formulaire)
        self.ui.btn_parametres.clicked.connect(self.ouvrir_parametre)
        self.ui.btn_chercher_employe.clicked.connect(self.ouvrir_chercher_personnel)
        self.ui.btn_ajouter.clicked.connect(self.ajouter_demande)
        self.ui.tableWidget_affichage.itemSelectionChanged.connect(self.selectionner_demande)
        self.ui.btn_afficher_tout.clicked.connect(self.afficher_liste_demande)
        self.ui.btn_supprimer.clicked.connect(self.supprimer_demande)
        self.ui.btn_modifier.clicked.connect(self.modifier_demande)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # sélectionner données
        req = """SELECT objet FROM liste_demande ORDER BY objet ASC"""
        cursor.execute(req)
        data = cursor.fetchall() # recupérer les données
        conn.close()
        self.ui.comboBox_objet_demande.addItems([str(i[0]) for i in data])
        self.ui.comboBox_objet_demande.setCurrentIndex(-1)
        
    def ouvrir_parametre(self):
        self.parametre_demande = FenetreParametreDemande()
        self.parametre_demande.exec_()
        self.parametre_demande.setFocus()
        
    def ouvrir_chercher_personnel(self):
        self.chercher_personnel = FenetreChercherPersonnel()
        self.chercher_personnel.exec_()
        self.chercher_personnel.setFocus()
        self.ui.txt_id_personnel.setText(self.chercher_personnel.id_selectionne)
        
    
    def valider_formulaire(self,pour_ajout = True):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()  
        
        id = self.ui.txt_id.text()
        id_personnel = self.ui.txt_id_personnel.text()
        objet = self.ui.comboBox_objet_demande.currentText()
        date_debut_str = self.ui.date_debut.date().toString("yyyy-MM-dd")
        date_fin_str = self.ui.date_fin.date().toString("yyyy-MM-dd")
        autorisation_chef_service = self.ui.comboBox_autorisation_chefservice.currentText()
        date_modification = datetime.today()
        
        # Convertir les chaînes en objets datetime.date :
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
        date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()

        erreur = []
        
        if id_personnel == "":
            erreur.append("L'ID de l'employé est vide. Veuillez corriger!")
            self.ui.txt_id_personnel.setStyleSheet("border: 1px solid red;")
        elif objet == "":
            erreur.append("L'objet est vide. Veuillez corriger!")
            self.ui.comboBox_objet_demande.setStyleSheet("border: 1px solid red;")
        elif  not autorisation_chef_service == "Oui":
            erreur.append("Cette demande n'a pas reçu l'autorisation du Chef Service. Veuillez corriger!")
            self.ui.comboBox_autorisation_chefservice.setStyleSheet("border: 1px solid red;")
            
        if objet != "":
            req = """
                SELECT nb_jours
                FROM liste_demande
                WHERE objet = ?;
            """
            cursor.execute(req,(objet,))
            data = cursor.fetchone()
            
            if data is None:
                nb_jours_maximal = 0
            else:
                nb_jours_maximal = int(data[0])
                
            # date 
            if  date_fin >= date_debut and id_personnel != "":
                req = """
                    SELECT SUM(date_fin - date_debut) AS duree_utilise,
                        id_personnel,
                        strftime('%Y', date_modification) AS Annee,
                        objet
                    FROM demande
                    WHERE id_personnel = ? AND Annee = ? AND objet = ?
                    GROUP BY id_personnel, objet, Annee;
                """
                
                cursor.execute(req,(int(id_personnel),str(date_modification.year),objet,))
                data_deja_obtenue = cursor.fetchone()
                
                if data_deja_obtenue is not None:
                    if int(data_deja_obtenue[0]) <= 0:
                        nb_jours_deja_obtenue  = 0
                    else:
                        nb_jours_deja_obtenue = int(data_deja_obtenue[0]) + 1
                else:
                    nb_jours_deja_obtenue  = 0
                
                #print(nb_jours_deja_obtenue)
                nb_jours_demande = (date_fin - date_debut).days + 1
                duree_cumule =  nb_jours_demande + nb_jours_deja_obtenue
                
            else:
                return False
            
        if id == "":
            data = None
            if id_personnel != "":
                # vérifier si une autre demande de l'individu est en cours
                req = """
                    SELECT date_fin, date_debut, id_personnel, objet
                    FROM demande
                    WHERE id_personnel = ?
                    ORDER BY date_fin DESC LIMIT 1;
                """
                cursor.execute(req,(int(id_personnel),))
                data = cursor.fetchone()
                
                if date_debut < QDate.currentDate():
                    erreur.append("La date de début doit être supérieure à la date de demande. Veuillez corriger!")
                    self.ui.date_debut.setStyleSheet("border: 1px solid red;")
        else:
            
            req = "SELECT date_creation FROM demande WHERE id = ?"
            cursor.execute(req,(int(id),))
            data = cursor.fetchone()
            date_creation = datetime.fromisoformat(data[0]).date()
            
            if date_debut < date_creation:
                erreur.append(f"La date de début doit être supérieure à la date de création [{date_creation}]. Veuillez corriger!")
                self.ui.date_debut.setStyleSheet("border: 1px solid red;")
            
            # vérifier si une autre demande de l'individu est en cours
            req = """
                SELECT date_fin, date_debut, id_personnel, objet
                FROM demande
                WHERE id_personnel = ? AND id <> ?
                ORDER BY date_fin DESC LIMIT 1;
            """
            cursor.execute(req,(int(id_personnel), int(id),))
            data = cursor.fetchone()

        if data != None:
            date_fin_derniere_demande = datetime.strptime(data[0], "%Y-%m-%d").date()
            date_debut_derniere_demande = datetime.strptime(data[1], "%Y-%m-%d").date()
            if date_debut <= date_fin_derniere_demande:
                erreur.append("Une demande est en cours. [EXP: " + str(date_fin_derniere_demande) + "]. Vous ne pouvez pas creer une demande antérieure à celle-ci!") 
            
            #☼ vérification de la limite
            #print(f"deja obtenu = {nb_jours_deja_obtenue} demande = {nb_jours_demande} cumul = {duree_cumule}")
            nb_jours_restant = nb_jours_maximal - duree_cumule
            if nb_jours_restant >= 0:
                QMessageBox.information(self,"Durée",f"Cette demande est valide.\n Suite à celle-ci le nombre de jours restant est de : {nb_jours_restant} jour (s).")
            else:
                erreur.append(f"Le nombre total de jours pour cette demande dépasse de {abs(nb_jours_restant)} jour (s) la durée limite.\n Le cumul des durées est de {duree_cumule} sur {nb_jours_maximal} jour (s).")

        cursor.close()
        
        if not erreur == []:
            msg = QMessageBox()
            msg.setWindowTitle("Validation")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Champs manquants.\n" + erreur[0])
            msg.exec_()
        return(erreur == [])
    

    def ajouter_demande(self):
        
        if self.valider_formulaire() == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            id = self.ui.txt_id.text()
            id_personnel = self.ui.txt_id_personnel.text()
            objet = self.ui.comboBox_objet_demande.currentText()
            date_debut = self.ui.date_debut.date().toString("yyyy-MM-dd")
            date_fin = self.ui.date_fin.date().toString("yyyy-MM-dd")
            description = self.ui.txt_description_demande.toPlainText()
            autorisation_chef_service = self.ui.comboBox_autorisation_chefservice.currentText()
            validation_demande = "Non"
            date_creation = datetime.today()
            date_modification = datetime.today()
            
            if id == "":
                req = """
                        INSERT INTO demande (
                            id_personnel, objet,date_debut,date_fin,description,autorisation_chef_service,validation_demande,
                            date_creation, date_modification
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """
                cursor.execute(req, (
                    id_personnel, objet, date_debut,date_fin,description,autorisation_chef_service,validation_demande,
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
                msgbox = QMessageBox()
                msgbox.setIcon(QMessageBox.Critical)
                msgbox.setText("Aucun enregistrement réalisé !")
                msgbox.exec_()
            self.initialiser_formulaire()
            self.afficher_liste_demande()
            
        
        
    
    def afficher_liste_demande(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # sélectionner données
        req = """SELECT * FROM demande ORDER BY id DESC"""
        cursor.execute(req)
        data = cursor.fetchall() # recupérer les données
        conn.close()
        
        if data is not None:
            row_index = 0
            for row in data:
                for col in range(self.ncol_tableWidget_ui): #afficher toes les colonnes
                    self.ui.tableWidget_affichage.setItem(row_index,col,QTableWidgetItem(str(row[col])))
                row_index = row_index + 1
            
    
    def selectionner_demande(self):
        item_selectionnee = self.ui.tableWidget_affichage.selectedItems()
        row_data = [item.text() for item in item_selectionnee]

        if len(row_data) == self.ncol_tableWidget_ui:
            personnel_id = row_data[0]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "SELECT * FROM  demande WHERE id = ?"
            cursor.execute(req,(personnel_id,))
            result = cursor.fetchone()
            
            # afficher les informations généraux
            self.ui.txt_id.setText(str(result[0]))
            self.ui.txt_id_personnel.setText(str(result[1]))
            self.ui.comboBox_objet_demande.setCurrentText(str(result[2]))
            self.ui.date_debut.setDate(QDate.fromString(result[3], "yyyy-MM-dd"))
            self.ui.date_fin.setDate(QDate.fromString(result[4], "yyyy-MM-dd"))
            self.ui.txt_description_demande.setText(str(result[5]))
            self.ui.comboBox_autorisation_chefservice.setCurrentText(str(result[6]))
            
    
    def initialiser_formulaire(self):
        # Réinitialisation des champs texte
        self.ui.txt_id.setText("")
        self.ui.txt_id_personnel.setText("")
        self.ui.date_debut.setDate(QDate.currentDate())
        self.ui.date_fin.setDate(QDate.currentDate())
        self.ui.comboBox_objet_demande.setCurrentIndex(-1)
        self.ui.txt_description_demande.setText("")
        self.ui.comboBox_autorisation_chefservice.setCurrentIndex(-1)

    
    def supprimer_demande(self):  
        id = self.ui.txt_id.text()  
        objet = self.ui.comboBox_objet_demande.currentText()
        
        if id == "":
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setWindowTitle("Suppression")
            msgbox.setText("Demande non trouvé. Impossible de supprimer.")
            msgbox.exec_()
        else:
            reponse = QMessageBox.question(
                None,
                "Confirmation",
                f"Voulez-vous vraiment supprimer la demande : [{objet}] ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reponse == QMessageBox.Yes:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM demande WHERE id = ?;"
                cursor.execute(req,(id,))
                conn.commit()
                conn.close()
                self.ui.tableWidget_affichage.clearContents() # effacer le visuel de la table et réactualiser
                self.initialiser_formulaire()
                self.afficher_liste_demande()
            
    
    def modifier_demande(self):
        
        id = self.ui.txt_id.text()
        id_personnel = self.ui.txt_id_personnel.text()
        objet = self.ui.comboBox_objet_demande.currentText()
        date_debut = self.ui.date_debut.date().toString("yyyy-MM-dd")
        date_fin = self.ui.date_fin.date().toString("yyyy-MM-dd")
        description = self.ui.txt_description_demande.toPlainText()
        autorisation_chef_service = self.ui.comboBox_autorisation_chefservice.currentText()
        validation_demande = "Non"
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if not id == "":
            id = int(id)
            reponse = QMessageBox.question(
                None,
                "Confirmation",
                f"Voulez-vous vraiment modifier la demande ID : [{id}] ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reponse == QMessageBox.Yes:
                if self.valider_formulaire(pour_ajout=False) == True: # verifier si erreur est 0
                    req = "SELECT * FROM demande WHERE id = ?"
                    cursor.execute(req,(id,))
                    data = cursor.fetchone()
                    
                    if not data is None:
                        msgbox = QMessageBox()
                        msgbox.setIcon(QMessageBox.Information)
                        msgbox.setWindowTitle("Vérification")
                        msgbox.setText("Modification éffectuée !")
                        msgbox.exec_()
                        req = """
                            UPDATE demande SET
                            id_personnel = ?,
                            objet = ?,
                            date_debut = ?,
                            date_fin = ?,
                            description = ?,
                            autorisation_chef_service = ?,
                            validation_demande = ?,
                            date_modification = ?
                            WHERE id = ?;
                        """
                        cursor.execute(req, (
                            id_personnel,
                            objet,
                            date_debut,
                            date_fin,
                            description,
                            autorisation_chef_service,
                            validation_demande,
                            date_modification,
                            id,
                        ))
                        conn.commit()
                        conn.close()
            self.ui.tableWidget_affichage.clearContents() # effacer le visuel de la table et réactualiser
            self.initialiser_formulaire()
            
      
