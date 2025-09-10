import sqlite3
import os
from  utils import utilitaires
from class_ui.fenetre_parametre_carriere_ui import Ui_ParametreSuiviCarriere
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
from utils.utilitaires import resource_path
import time
import shutil

class FenetreParametreSuiviCarriere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ParametreSuiviCarriere()
        self.ui.setupUi(self)
        self.ncol_tableWidget_ui = 4
        
        self.ui.txt_id_service.setEnabled(False)
        self.ui.txt_id_statut.setEnabled(False)
        self.ui.txt_id_fonction.setEnabled(False)
        self.ui.txt_id_cat_socio_professionnelle.setEnabled(False)
        self.ui.txt_id_grade.setEnabled(False)
        self.ui.txt_id_autre_responsabilite.setEnabled(False)
        self.db_path = resource_path("data/database.db")
        
        # Service
        self.ui.btn_nouveau_service.clicked.connect(self.nouveau_service)
        self.ui.btn_ajouter_service.clicked.connect(self.ajouter_service)
        self.ui.btn_modifier_service.clicked.connect(self.modifier_service)
        self.ui.btn_supprimer_service.clicked.connect(self.supprimer_service)
        
        # Statut
        self.ui.btn_nouveau_statut.clicked.connect(self.nouveau_statut)
        self.ui.btn_ajouter_statut.clicked.connect(self.ajouter_statut)
        self.ui.btn_modifier_statut.clicked.connect(self.modifier_statut)
        self.ui.btn_supprimer_statut.clicked.connect(self.supprimer_statut)
        
        # Fonctions
        self.ui.btn_nouveau_fonction.clicked.connect(self.nouveau_fonction)
        self.ui.btn_ajouter_fonction.clicked.connect(self.ajouter_fonction)
        self.ui.btn_modifier_fonction.clicked.connect(self.modifier_fonction)
        self.ui.btn_supprimer_fonction.clicked.connect(self.supprimer_fonction)
        
        # catégorie professionnelle
        self.ui.btn_nouveau_cat_socio_professionnelle.clicked.connect(self.nouveau_categorie_professionnelle)
        self.ui.btn_ajouter_cat_socio_professionnelle.clicked.connect(self.ajouter_categorie_professionnelle)
        self.ui.btn_modifier_cat_socio_professionnelle.clicked.connect(self.modifier_categorie_professionnelle)
        self.ui.btn_supprimer_cat_socio_professionnelle.clicked.connect(self.supprimer_categorie_professionnelle)
        
        # grade
        self.ui.btn_nouveau_grade.clicked.connect(self.nouveau_grade)
        self.ui.btn_ajouter_grade.clicked.connect(self.ajouter_grade)
        self.ui.btn_modifier_grade.clicked.connect(self.modifier_grade)
        self.ui.btn_supprimer_grade.clicked.connect(self.supprimer_grade)
        
        # autre responsabilité
        self.ui.btn_nouveau_autre_responsabilite.clicked.connect(self.nouveau_autre_responsabilite)
        self.ui.btn_ajouter_autre_responsabilite.clicked.connect(self.ajouter_autre_responsabilite)
        self.ui.btn_modifier_autre_responsabilite.clicked.connect(self.modifier_autre_responsabilite)
        self.ui.btn_supprimer_autre_responsabilite.clicked.connect(self.supprimer_autre_responsabilite)
        
        
        # tables
        self.afficher_liste()
        self.ui.tableWidget_affichage_service.itemSelectionChanged.connect(self.selectionner_liste)
        self.ui.tableWidget_affichage_statut.itemSelectionChanged.connect(self.selectionner_liste)
        self.ui.tableWidget_affichage_fonction.itemSelectionChanged.connect(self.selectionner_liste)
        self.ui.tableWidget_affichage_cat_socio_professionnelle.itemSelectionChanged.connect(self.selectionner_liste)
        self.ui.tableWidget_affichage_grade.itemSelectionChanged.connect(self.selectionner_liste)
        self.ui.tableWidget_affichage_autre_responsabilite.itemSelectionChanged.connect(self.selectionner_liste)

    def valider_form_service(self):
        erreur = []
        id = self.ui.txt_id_service.text()
        service = self.ui.txt_service.text()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        req = "SELECT * FROM liste_service WHERE service = ?"
        cursor.execute(req,(service,))
        data = cursor.fetchone()
        
        if data != None and service != "":  # service existe
            erreur.append("Le service existe déjà!\n Veuillez corriger!")
            
        if service == "":
            erreur.append("Le nom du service doit être renseigné. Veuillez corriger!")
        if id != "":
            if service == "":
                erreur.append("Le nom du service doit être renseigné. Veuillez corriger!")
        if erreur != []:
            QMessageBox.critical(self,"Configuration",erreur[0])
        return erreur == []
    
    def valider_form_statut(self):
        erreur = []
        id = self.ui.txt_id_statut.text()
        statut = self.ui.txt_statut.text()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        req = "SELECT * FROM liste_statut WHERE statut = ?"
        cursor.execute(req,(statut,))
        data = cursor.fetchone()
        
        if data != None and statut != "":  # statut existe
            erreur.append("Le statut existe déjà!\n Veuillez corriger!")
        
        if statut == "":
            erreur.append("Le nom du statut doit être renseigné. Veuillez corriger!")
        if id != "":
            if statut == "":
                erreur.append("Le nom du statut doit être renseigné. Veuillez corriger!") 
        if erreur != []:
            QMessageBox.critical(self,"Configuration",erreur[0])
        return erreur == []
    
    def valider_form_fonction(self):
        erreur = []
        id = self.ui.txt_id_fonction.text()
        fonction = self.ui.txt_fonction.text()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        req = "SELECT * FROM liste_fonction WHERE fonction = ?"
        cursor.execute(req,(fonction,))
        data = cursor.fetchone()
        
        if data != None and fonction != "":  # fonction existe
            erreur.append("La fonction existe déjà!\n Veuillez corriger!")
        
        if fonction == "":
            erreur.append("Le nom de la fonction doit être renseigné. Veuillez corriger!")
        if id != "":
            if fonction == "":
                erreur.append("Le nom de la fonction doit être renseigné. Veuillez corriger!") 
        if erreur != []:
            QMessageBox.critical(self,"Configuration",erreur[0])
        return erreur == []
    
        
    def valider_form_categorie_professionnelle(self):
        erreur = []
        id = self.ui.txt_id_cat_socio_professionnelle.text()
        categorie = self.ui.txt_cat_socio_professionnelle.text()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        req = "SELECT * FROM liste_categorie_professionnelle WHERE categorie = ?"
        cursor.execute(req,(categorie,))
        data = cursor.fetchone()
        
        if data != None and categorie != "":  # fonction existe
            erreur.append("La catégorie existe déjà!\n Veuillez corriger!")
        
        if categorie == "":
            erreur.append("Le nom de la catégorie doit être renseigné. Veuillez corriger!")
        if id != "":
            if categorie == "":
                erreur.append("Le nom de la catégorie doit être renseigné. Veuillez corriger!") 
        if erreur != []:
            QMessageBox.critical(self,"Configuration",erreur[0])
        return erreur == []
    
      
    def valider_form_grade(self):
        erreur = []
        id = self.ui.txt_id_grade.text()
        grade = self.ui.txt_grade.text()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        req = "SELECT * FROM liste_grade WHERE grade = ?"
        cursor.execute(req,(grade,))
        data = cursor.fetchone()
        
        if data != None and grade != "":  # fonction existe
            erreur.append("Le grade existe déjà!\n Veuillez corriger!")
        
        if grade == "":
            erreur.append("La valeur du grade doit être renseigné. Veuillez corriger!")
        if id != "":
            if grade == "":
                erreur.append("La valeur du grade doit être renseigné. Veuillez corriger!") 
        if erreur != []:
            QMessageBox.critical(self,"Configuration",erreur[0])
        return erreur == []
    
    
      
    def valider_form_autre_responsabilite(self):
        erreur = []
        id = self.ui.txt_id_autre_responsabilite.text()
        responsabilite = self.ui.txt_autre_responsabilite.text()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        req = "SELECT * FROM liste_autre_responsabilite WHERE responsabilite = ?"
        cursor.execute(req,(responsabilite,))
        data = cursor.fetchone()
        
        if data != None and responsabilite != "":  # fonction existe
            erreur.append("Cette tâche existe déjà!\n Veuillez corriger!")
        
        if responsabilite == "":
            erreur.append("La tâche doit être renseigné. Veuillez corriger!")
        if id != "":
            if responsabilite == "":
                erreur.append("La tâche doit être renseigné. Veuillez corriger!") 
        if erreur != []:
            QMessageBox.critical(self,"Configuration",erreur[0])
        return erreur == []
    
    
    
    # liste
    def afficher_liste(self):
        
        def remplir_table(nom_table, widget):
            cursor.execute(f"SELECT * FROM {nom_table} ORDER BY id DESC")
            for row_index, row in enumerate(cursor.fetchall()):
                for col_index, value in enumerate(row):
                    widget.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Liste des correspondances table SQL → widget Qt
        tables_widgets = [
            ("liste_service", self.ui.tableWidget_affichage_service),
            ("liste_statut", self.ui.tableWidget_affichage_statut),
            ("liste_fonction", self.ui.tableWidget_affichage_fonction),
            ("liste_categorie_professionnelle", self.ui.tableWidget_affichage_cat_socio_professionnelle),
            ("liste_grade", self.ui.tableWidget_affichage_grade),
            ("liste_autre_responsabilite", self.ui.tableWidget_affichage_autre_responsabilite),
        ]

        for table, widget in tables_widgets:
            widget.clearContents()
            widget.setRowCount(1000)
            remplir_table(table, widget)

        conn.close()

    def selectionner_liste(self):
        # Liste des correspondances : (nom_table, champs_ui)
        correspondances = [
            ("tableWidget_affichage_service", ["txt_id_service", "txt_service"]),
            ("tableWidget_affichage_statut",  ["txt_id_statut",  "txt_statut"]),
            ("tableWidget_affichage_fonction",["txt_id_fonction","txt_fonction"]),
            ("tableWidget_affichage_cat_socio_professionnelle",["txt_id_cat_socio_professionnelle","txt_cat_socio_professionnelle"]),
            ("tableWidget_affichage_grade",["txt_id_grade","txt_grade"]),
            ("tableWidget_affichage_autre_responsabilite",["txt_id_autre_responsabilite","txt_autre_responsabilite"]),
        ]
        
        for nom_table, champs in correspondances:
            table_widget = getattr(self.ui, nom_table)  # Récupère la table par son nom
            items_selectionnes = table_widget.selectedItems()
            row_data = [item.text() for item in items_selectionnes]

            if len(row_data) == self.ncol_tableWidget_ui:
                getattr(self.ui, champs[0]).setText(row_data[0])
                getattr(self.ui, champs[1]).setText(row_data[1])

    
        
    # Service
    def nouveau_service(self):
        self.ui.txt_id_service.setText("")
        self.ui.txt_service.setText("")
    
    def ajouter_service(self):
        id = self.ui.txt_id_service.text()
        service = self.ui.txt_service.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
            
        if self.valider_form_service() == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_service (service,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(service,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration service","Succès !")

        self.nouveau_service()
        self.afficher_liste()
         
    def modifier_service(self):
        id = self.ui.txt_id_service.text()
        service = self.ui.txt_service.text()
        date_modification = datetime.today()
            
        if self.valider_form_service() == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_service SET service = ?, date_modification = ?  WHERE id = ?"
                conn.execute(req,(service,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration service","Succès !")
            else:
                QMessageBox.critical(self,"Configuration service","Aucune modification effectuée !")

        self.nouveau_service()
        self.afficher_liste()
        
    def supprimer_service(self):
        id = self.ui.txt_id_service.text()
        reponse = QMessageBox.information(self,"Configuration service","Voulez-vous supprimer ce service ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_service WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration service","Succès !")

        self.nouveau_service()
        self.afficher_liste()
                  
         
    # Statut
    def nouveau_statut(self):
        self.ui.txt_id_statut.setText("")
        self.ui.txt_statut.setText("")
        
    def ajouter_statut(self):
        id = self.ui.txt_id_statut.text()
        statut = self.ui.txt_statut.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        if self.valider_form_statut() == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_statut (statut,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(statut,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration statut","Succès !")

        self.nouveau_statut()
        self.afficher_liste()
            
            
    def modifier_statut(self):
        id = self.ui.txt_id_statut.text()
        statut = self.ui.txt_statut.text()
        date_modification = datetime.today()
            
        if self.valider_form_statut() == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_statut SET statut = ?, date_modification = ? WHERE id = ?"
                conn.execute(req,(statut,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration statut","Succès !")
            else:
                QMessageBox.critical(self,"Configuration statut","Aucune modification effectuée !")

        self.nouveau_statut()
        self.afficher_liste()
            
        
    def supprimer_statut(self):
        id = self.ui.txt_id_statut.text()
        reponse = QMessageBox.information(self,"Configuration statut","Voulez-vous supprimer ce statut ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_statut WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration statut","Succès !")

        self.nouveau_statut()
        self.afficher_liste()   
    
            
    # Fonction (Corps)
    def nouveau_fonction(self):
        self.ui.txt_id_fonction.setText("")
        self.ui.txt_fonction.setText("")
        
    def ajouter_fonction(self):
        id = self.ui.txt_id_fonction.text()
        fonction = self.ui.txt_fonction.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        if self.valider_form_fonction() == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_fonction (fonction,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(fonction,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration fonction","Succès !")
            
        self.nouveau_fonction()
        self.afficher_liste()
        

    def modifier_fonction(self):
        id = self.ui.txt_id_fonction.text()
        fonction = self.ui.txt_fonction.text()
        date_modification = datetime.today()
            
        if self.valider_form_fonction() == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_fonction SET fonction = ?, date_modification = ? WHERE id = ?"
                conn.execute(req,(fonction,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration fonction","Succès !")
            else:
                QMessageBox.critical(self,"Configuration fonction","Aucune modification effectuée !")

        self.nouveau_fonction()
        self.afficher_liste()
    
            
    def supprimer_fonction(self):
        id = self.ui.txt_id_fonction.text()
        reponse = QMessageBox.information(self,"Configuration fonction","Voulez-vous supprimer cette fonction ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_fonction WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration fonction","Succès !")

        self.nouveau_fonction()
        self.afficher_liste()
        
        
    # Catégorie socio professionnelle
    def nouveau_categorie_professionnelle(self):
        self.ui.txt_id_cat_socio_professionnelle.setText("")
        self.ui.txt_cat_socio_professionnelle.setText("")
        
    def ajouter_categorie_professionnelle(self):
        id = self.ui.txt_id_cat_socio_professionnelle.text()
        categorie = self.ui.txt_cat_socio_professionnelle.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        if self.valider_form_categorie_professionnelle() == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_categorie_professionnelle (categorie,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(categorie,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration catégorie","Succès !")
            
        self.nouveau_categorie_professionnelle()
        self.afficher_liste()
        

    def modifier_categorie_professionnelle(self):
        id = self.ui.txt_id_cat_socio_professionnelle.text()
        categorie = self.ui.txt_cat_socio_professionnelle.text()
        date_modification = datetime.today()
            
        if self.valider_form_categorie_professionnelle() == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_categorie_professionnelle SET categorie = ?, date_modification = ? WHERE id = ?"
                conn.execute(req,(categorie,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration catégorie","Succès !")
            else:
                QMessageBox.critical(self,"Configuration catégorie","Aucune modification effectuée !")

        self.nouveau_categorie_professionnelle()
        self.afficher_liste()
    
            
    def supprimer_categorie_professionnelle(self):
        id = self.ui.txt_id_cat_socio_professionnelle.text()
        reponse = QMessageBox.information(self,"Configuration catégorie","Voulez-vous supprimer cette catégorie ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_categorie_professionnelle WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration catégorie","Succès !")

        self.nouveau_categorie_professionnelle()
        self.afficher_liste()
    
    
    # grade
    def nouveau_grade(self):
        self.ui.txt_id_grade.setText("")
        self.ui.txt_grade.setText("")
        
    def ajouter_grade(self):
        id = self.ui.txt_id_grade.text()
        grade = self.ui.txt_grade.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        if self.valider_form_grade() == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_grade (grade,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(grade,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration grade","Succès !")
            
        self.nouveau_grade()
        self.afficher_liste()
        

    def modifier_grade(self):
        id = self.ui.txt_id_grade.text()
        grade = self.ui.txt_grade.text()
        date_modification = datetime.today()
            
        if self.valider_form_grade() == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_grade SET grade = ?, date_modification = ? WHERE id = ?"
                conn.execute(req,(grade,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration grade","Succès !")
            else:
                QMessageBox.critical(self,"Configuration grade","Aucune modification effectuée !")

        self.nouveau_grade()
        self.afficher_liste()
    
            
    def supprimer_grade(self):
        id = self.ui.txt_id_grade.text()
        reponse = QMessageBox.information(self,"Configuration grade","Voulez-vous supprimer ce grade ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_grade WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration grade","Succès !")

        self.nouveau_grade()
        self.afficher_liste()
    
            
    # autre responsabilite
    def nouveau_autre_responsabilite(self):
        self.ui.txt_id_autre_responsabilite.setText("")
        self.ui.txt_autre_responsabilite.setText("")
        
    def ajouter_autre_responsabilite(self):
        id = self.ui.txt_id_autre_responsabilite.text()
        responsabilite = self.ui.txt_autre_responsabilite.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        if self.valider_form_autre_responsabilite() == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_autre_responsabilite (responsabilite,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(responsabilite,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration grade","Succès !")
            
        self.nouveau_autre_responsabilite()
        self.afficher_liste()
        

    def modifier_autre_responsabilite(self):
        id = self.ui.txt_id_autre_responsabilite.text()
        responsabilite = self.ui.txt_autre_responsabilite.text()
        date_modification = datetime.today()
            
        if self.valider_form_autre_responsabilite() == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_autre_responsabilite SET responsabilite = ?, date_modification = ? WHERE id = ?"
                conn.execute(req,(responsabilite,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration responsabilité","Succès !")
            else:
                QMessageBox.critical(self,"Configuration responsabilité","Aucune modification effectuée !")

        self.nouveau_autre_responsabilite()
        self.afficher_liste()
    
            
    def supprimer_autre_responsabilite(self):
        id = self.ui.txt_id_grade.text()
        reponse = QMessageBox.information(self,"Configuration responsabilité","Voulez-vous supprimer cette responsabilité ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_autre_responsabilite WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration responsabilité","Succès !")

        self.nouveau_autre_responsabilite()
        self.afficher_liste()
        
        
      