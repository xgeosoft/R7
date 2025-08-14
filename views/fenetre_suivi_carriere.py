import sqlite3
import os
from  utils import utilitaires
from class_ui.fenetre_gestion_carriere_ui import Ui_FenetreSuiviCarriere
from views.fenetre_parametre_demande import FenetreParametreDemande
from views.fenetre_chercher_personnel import FenetreChercherPersonnel
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
from utils.utilitaires import resource_path
import time
import shutil

class FenetreSuiviCarriere(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetreSuiviCarriere()
        self.ui.setupUi(self)
        self.ncol_tableWidget_ui = 10
        self.db_path = resource_path("data/database.db")
        
        # configuration des options
        self.configurer_option()

        # id employé
        self.ui.txt_id.setEnabled(False)
        self.ui.txt_id_personnel.setEnabled(False)
        
        # combobox
        self.ui.comboBox_service.setCurrentIndex(-1)
        self.ui.comboBox_statut.setCurrentIndex(-1)
        self.ui.comboBox_fonction.setCurrentIndex(-1)
        self.ui.comboBox_cat_socio_profesionnelle.setCurrentIndex(-1)
        self.ui.comboBox_grade.setCurrentIndex(-1)
        self.ui.comboBox_autres_fonction.setCurrentIndex(-1)
        self.ui.comboBox_autorisation_chefservice.setCurrentIndex(-1)
        
        
        # date
        self.ui.date_prise_service.setDate(QDate.currentDate()) 
                
        # Bouton
        self.ui.btn_nouveau.clicked.connect(self.initialiser_formulaire)
        self.ui.btn_chercher_employe.clicked.connect(self.ouvrir_chercher_personnel)
        #self.ui.btn_ajouter.clicked.connect(self.ajouter_demande)
        #self.ui.tableWidget_affichage.itemSelectionChanged.connect(self.selectionner_demande)
        #self.ui.btn_afficher_tout.clicked.connect(self.afficher_liste_demande)
        #self.ui.btn_supprimer.clicked.connect(self.supprimer_demande)
        #self.ui.btn_modifier.clicked.connect(self.modifier_demande)
     
     
    def ouvrir_chercher_personnel(self):
        self.chercher_personnel = FenetreChercherPersonnel()
        self.chercher_personnel.exec_()
        self.chercher_personnel.setFocus()
        self.ui.txt_id_personnel.setText(self.chercher_personnel.id_selectionne)
        
    
    def valider_formulaire(self):
        id = self.ui.txt_id.text()
        id_personnel = self.ui.txt_id_personnel.text()
        service = self.ui.comboBox_service.currentText()
        fonction = self.ui.comboBox_fonction.currentText()
        statut = self.ui.comboBox_statut.currentText()
        cati_socio_prof = self.ui.comboBox_cat_socio_profesionnelle.currentText()
        grade = self.ui.comboBox_grade.currentText()
        #description_tache = self.ui.txt_description_tache.text()
        autorisation_chef_service = self.ui.comboBox_autorisation_chefservice.currentText()
        date_prise_service = self.ui.date_prise_service.date()
        
        erreur = []
        
        if id_personnel == "":
            erreur.append("L'ID de l'employé est vide. Veuillez corriger!")
            self.ui.txt_id_personnel.setStyleSheet("border: 1px solid red;")
        
        if service == "":
            erreur.append("Le service n'est pas renseigné. Veuillez corriger!")
            self.ui.comboBox_service.setStyleSheet("border: 1px solid red;")
            
        if fonction == "":
            erreur.append("La fonction n'est pas renseignée. Veuillez corriger!")
            self.ui.comboBox_fonction.setStyleSheet("border: 1px solid red;")
            
        if statut == "":
            erreur.append("Le statut n'est pas renseigné. Veuillez corriger!")
            self.ui.comboBox_statut.setStyleSheet("border: 1px solid red;")
            
        if cati_socio_prof == "":
            erreur.append("La catégorie socio professionnelle n'est pas renseigné. Veuillez corriger!")
            self.ui.comboBox_cat_socio_profesionnelle.setStyleSheet("border: 1px solid red;")
            
        if grade == "":
            erreur.append("Le grade n'est pas renseigné. Veuillez corriger!")
            self.ui.comboBox_grade.setStyleSheet("border: 1px solid red;")
            
        if autorisation_chef_service == "":
            erreur.append("Cette procédure n'a pas reçu l'autorisation du chef service. Veuillez corriger!")
            self.ui.comboBox_autorisation_chefservice.setStyleSheet("border: 1px solid red;")
        
        if erreur != []:
            QMessageBox.critical(self,"Suivi des carrières",erreur[0])
            
        return erreur == []
    
    
    def initialiser_formulaire(self):
        self.ui.txt_id.setText("")
        self.ui.txt_id_personnel.setText("")
        self.ui.comboBox_service.setCurrentIndex(-1)
        self.ui.comboBox_fonction.setCurrentIndex(-1)
        self.ui.comboBox_statut.setCurrentIndex(-1)
        self.ui.comboBox_cat_socio_profesionnelle.setCurrentIndex(-1)
        self.ui.comboBox_grade.setCurrentIndex(-1)
        self.ui.txt_description_tache.setText("")
        self.ui.comboBox_autorisation_chefservice.setCurrentIndex(-1)
        self.ui.date_prise_service.setDate(QDate.currentDate())
            
    
    def configurer_option(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # colonnes   table   combobox associé
        correspondances = [
            ("service","liste_service","comboBox_service"),
            ("statut","liste_statut","comboBox_statut"),
            ("fonction","liste_fonction","comboBox_fonction"),
            ("categorie","liste_categorie_professionnelle","comboBox_cat_socio_profesionnelle"),
            ("grade","liste_grade","comboBox_grade"),
            ("responsabilite","liste_autre_responsabilite","comboBox_autres_fonction"),
        ]
        
        for colonne, sql_table, combobox_name in correspondances:
            # Service
            req = "SELECT " + colonne +  " FROM " + sql_table
            cursor.execute(req)
            data = cursor.fetchall()
            if data != None:
                getattr(self.ui,combobox_name).addItems([item[0] for item in data])
            
        
        