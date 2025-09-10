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
        self.ncol_tableWidget_ui = 14
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
        self.ui.btn_ajouter.clicked.connect(self.ajouter_carriere)
        self.ui.btn_afficher_tout.clicked.connect(self.afficher_table_suivi_carriere)
        self.ui.btn_supprimer.clicked.connect(self.supprimer_carriere)
        self.ui.btn_modifier.clicked.connect(self.modifier_carriere)
        self.ui.tableWidget_affichage.itemSelectionChanged.connect(self.selectionner_carriere)
     
        # afficher table
        self.afficher_table_suivi_carriere()
     
    def ouvrir_chercher_personnel(self):
        self.chercher_personnel = FenetreChercherPersonnel()
        self.chercher_personnel.exec_()
        self.chercher_personnel.setFocus()
        self.ui.txt_id_personnel.setText(self.chercher_personnel.id_selectionne)
        self.afficher_table_suivi_carriere()
        
    
    def valider_formulaire(self):
        id = self.ui.txt_id.text()
        id_personnel = self.ui.txt_id_personnel.text()
        service = self.ui.comboBox_service.currentText()
        fonction = self.ui.comboBox_fonction.currentText()
        statut = self.ui.comboBox_statut.currentText()
        cati_socio_prof = self.ui.comboBox_cat_socio_profesionnelle.currentText()
        grade = self.ui.comboBox_grade.currentText()
        responsabilite = self.ui.comboBox_autres_fonction.currentText()
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
        self.ui.comboBox_autres_fonction.setCurrentIndex(-1)
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
            

    # table
    def afficher_table_suivi_carriere(self):
        id_personnel = self.ui.txt_id_personnel.text()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        def remplir_table(nom_table, widget):
            if id_personnel == "":
                req = f"SELECT * FROM {nom_table} ORDER BY id DESC"
                cursor.execute(req)
            else:
                req = f"SELECT * FROM {nom_table} WHERE id_personnel = ? ORDER BY id DESC"
                cursor.execute(req,(int(id_personnel),))
            
            data = cursor.fetchall()
            if data != None:
                for row_index, row in enumerate(data):
                    for col_index, value in enumerate(row):
                        widget.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        # Liste des correspondances table SQL → widget Qt
        tables_widgets = [
            ("suivi_carriere", self.ui.tableWidget_affichage),
        ]

        for table, widget in tables_widgets:
            widget.clearContents()
            remplir_table(table, widget)

        conn.close()
       
       
       
    def ajouter_carriere(self):
        id = self.ui.txt_id.text()
        id_personnel = self.ui.txt_id_personnel.text()
        service = self.ui.comboBox_service.currentText()
        fonction = self.ui.comboBox_fonction.currentText()
        statut = self.ui.comboBox_statut.currentText()
        categorie = self.ui.comboBox_cat_socio_profesionnelle.currentText()
        niveau_grade = self.ui.comboBox_grade.currentText()
        responsabilite = self.ui.comboBox_autres_fonction.currentText()
        description_tache = self.ui.txt_description_tache.toPlainText()
        autorisation_chef_service = self.ui.comboBox_autorisation_chefservice.currentText()
        autorisation_responsable_centre = "Non"
        date_prise_service = self.ui.date_prise_service.date().toString("yyyy-MM-dd")
        
        reponse = QMessageBox.information(self,"Formulaire Carrière",f"Voulez-vous ajouter ces informations pour cet l'employé [ID = {id_personnel}] ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if self.valider_formulaire() == True:
                try:
                    conn = sqlite3.connect(self.db_path)
                    cur = conn.cursor()

                    req = """
                    INSERT INTO suivi_carriere(
                        id_personnel,
                        service,
                        fonction,
                        statut,
                        categorie,
                        niveau_grade,
                        responsabilite,
                        description_tache,
                        date_prise_service,
                        autorisation_chef_service,
                        autorisation_responsable_centre,
                        date_creation,
                        date_modification
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?,?, date('now'), date('now'))
                    """

                    valeurs = (
                        id_personnel,
                        service,
                        fonction,
                        statut,
                        categorie,
                        niveau_grade,
                        responsabilite,
                        description_tache,  # description_tache, si tu n'utilises pas encore txt_description_tache
                        date_prise_service,
                        autorisation_chef_service,
                        autorisation_responsable_centre,  # exemple pour autorisation_responsable_centre
                    )

                    cur.execute(req, valeurs)
                    conn.commit()
                    conn.close()

                    QMessageBox.information(self, "Succès", "Informations ajoutées avec succès !")
                    self.initialiser_formulaire()
                    self.ui.tableWidget_affichage.clearContents()
                
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Impossible d'insérer : {e}")

        
        
        
    def modifier_carriere(self):
        id_carriere = self.ui.txt_id.text()  # ID de la ligne carrière à modifier
        id_personnel = self.ui.txt_id_personnel.text()
        service = self.ui.comboBox_service.currentText()
        fonction = self.ui.comboBox_fonction.currentText()
        statut = self.ui.comboBox_statut.currentText()
        categorie = self.ui.comboBox_cat_socio_profesionnelle.currentText()
        niveau_grade = self.ui.comboBox_grade.currentText()
        responsabilite = self.ui.comboBox_autres_fonction.currentText()
        description_tache = self.ui.txt_description_tache.toPlainText()
        autorisation_chef_service = self.ui.comboBox_autorisation_chefservice.currentText()
        autorisation_responsable_centre = "Non"  # Si besoin de rendre modifiable, mets aussi en champ UI
        date_prise_service = self.ui.date_prise_service.date().toString("yyyy-MM-dd")

        if not id_carriere:  # On vérifie qu'on a bien l'ID à modifier
            QMessageBox.warning(self, "Modification", "Aucune carrière sélectionnée pour modification.")
            return

        reponse = QMessageBox.question(
            self,
            "Formulaire Carrière",
            f"Voulez-vous modifier les informations pour l'employé [ID = {id_personnel}] ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reponse == QMessageBox.Yes:
            if self.valider_formulaire() == True:
                try:
                    conn = sqlite3.connect(self.db_path)
                    cur = conn.cursor()

                    req = """
                    UPDATE suivi_carriere
                    SET
                        id_personnel = ?,
                        service = ?,
                        fonction = ?,
                        statut = ?,
                        categorie = ?,
                        niveau_grade = ?,
                        responsabilite = ?,
                        description_tache = ?,
                        date_prise_service = ?,
                        autorisation_chef_service = ?,
                        autorisation_responsable_centre = ?,
                        date_modification = date('now')
                    WHERE id = ?
                    """

                    valeurs = (
                        id_personnel,
                        service,
                        fonction,
                        statut,
                        categorie,
                        niveau_grade,
                        responsabilite,
                        description_tache,
                        date_prise_service,
                        autorisation_chef_service,
                        autorisation_responsable_centre,
                        int(id_carriere)
                    )

                    cur.execute(req, valeurs)
                    conn.commit()
                    conn.close()

                    QMessageBox.information(self, "Succès", "Informations mises à jour avec succès !")
                    self.initialiser_formulaire()
                    self.ui.tableWidget_affichage.clearContents()
                    self.afficher_table_suivi_carriere()

                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Impossible de modifier : {e}")

                  
                  
    def supprimer_carriere(self):
        id = self.ui.txt_id.text()  # id de la ligne carrière
        id_personnel = self.ui.txt_id_personnel.text()

        if not id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une carrière à supprimer.")
            return

        reponse = QMessageBox.question(
            self,
            "Suppression Carrière",
            f"Voulez-vous vraiment supprimer cette carrière (ID = {id}) pour l'employé [ID personnel = {id_personnel}] ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reponse == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()

                req = "DELETE FROM suivi_carriere WHERE id = ?"
                cur.execute(req, (int(id),))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "Succès", "Carrière supprimée avec succès !")
                self.initialiser_formulaire()
                self.ui.tableWidget_affichage.clearContents()
                self.afficher_table_suivi_carriere()

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer : {e}")
                


    def selectionner_carriere(self):
        item_selectionnee = self.ui.tableWidget_affichage.selectedItems()
        row_data = [item.text() for item in item_selectionnee]

        if len(row_data) == self.ncol_tableWidget_ui:
            id = row_data[0]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "SELECT * FROM  suivi_carriere WHERE id = ?"
            cursor.execute(req,(int(id),))
            result = cursor.fetchone()
            
            if result != None:
                self.ui.txt_id.setText(str(result[0]))
                self.ui.txt_id_personnel.setText(str(result[1]))
                self.ui.comboBox_service.setCurrentText(result[2])
                self.ui.comboBox_fonction.setCurrentText(result[3])
                self.ui.comboBox_statut.setCurrentText(result[4])
                self.ui.comboBox_cat_socio_profesionnelle.setCurrentText(result[5])
                self.ui.comboBox_grade.setCurrentText(result[6])
                self.ui.comboBox_autres_fonction.setCurrentText(result[7])
                self.ui.txt_description_tache.setText(result[8])
                self.ui.date_prise_service.setDate(QDate.fromString(result[9], "yyyy-MM-dd"))
                self.ui.comboBox_autorisation_chefservice.setCurrentText(result[10])
                
                
                

    
        