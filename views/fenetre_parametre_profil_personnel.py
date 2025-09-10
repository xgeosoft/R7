import sqlite3
import os
from  utils import utilitaires
from class_ui.fenetre_parametre_profil_personnel_ui import Ui_ParametreProfilPersonnel
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPixmap
from datetime import datetime
from utils.utilitaires import resource_path
import time
import shutil

class FenetreParametreProfilPersonnel(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ParametreProfilPersonnel()
        self.ui.setupUi(self)
        self.ncol_tableWidget_ui = 4
        self.db_path = resource_path("data/database.db")
        self.initialiser_valeur_formulaire()
        
        self.all_parameter_forms = [
            ('Banque','banque','liste_banque',),
            ('Sexe','sexe',"liste_sexe"),
            ('Religion','religion',"liste_religion"),
            ('Ethnie','ethnie',"liste_ethnie"),
            ('Pays','pays',"liste_pays"),
        ]
        
        for nom_form, champs, nom_table in self.all_parameter_forms:
            getattr(self.ui, f"txt_id_{champs}").setEnabled(False)
            getattr(self.ui,f"btn_nouveau_{champs}").clicked.connect(getattr(self,f"nouveau_{champs}"))
            getattr(self.ui,f"btn_modifier_{champs}").clicked.connect(getattr(self,f"modifier_{champs}"))
            getattr(self.ui,f"btn_ajouter_{champs}").clicked.connect(getattr(self,f"ajouter_{champs}"))
            getattr(self.ui,f"btn_supprimer_{champs}").clicked.connect(getattr(self,f"supprimer_{champs}"))
            getattr(self.ui,f"tableWidget_affichage_{champs}").itemSelectionChanged.connect(self.selectionner_liste)

        
        # tables
        self.afficher_liste()

    def initialiser_valeur_formulaire(self):
        all_data = [
            ('pays',utilitaires.pays_liste_fr,),
            ('religion',utilitaires.liste_religions,),
            ('ethnie',utilitaires.groupes_ethniques_benin,),
            ('sexe',utilitaires.sexe,)
        ]
        
        for champs,data in all_data:
            self.remplir_parametre(champs=champs,data=data)
            

    def valider_form(self,champs,pour_modifier = False):
        erreur = []
        id = getattr(self.ui,"txt_id_"+champs).text()
        label = getattr(self.ui,"txt_"+champs).text()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if id == "":
            req = f"SELECT * FROM liste_{champs} WHERE {champs} = ?"
        elif pour_modifier == True:
            req = f"SELECT * FROM liste_{champs} WHERE {champs} = ? AND id <> {int(id)}"
        
        cursor.execute(req,(label,))
        data = cursor.fetchone()
        
        if data != None and label != "":  # valeur existe
            erreur.append("La valeur existe déjà!\n Veuillez corriger!")
        
        if label == "":
            erreur.append("La valeur doit être renseigné. Veuillez corriger!")
        if id != "":
            if label == "":
                erreur.append("La valeur doit être renseigné. Veuillez corriger!")
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
            ("liste_sexe", self.ui.tableWidget_affichage_sexe),
            ("liste_pays", self.ui.tableWidget_affichage_pays),
            ("liste_ethnie", self.ui.tableWidget_affichage_ethnie),
            ("liste_banque", self.ui.tableWidget_affichage_banque),
            ("liste_religion", self.ui.tableWidget_affichage_religion),
        ]

        for table, widget in tables_widgets:
            widget.clearContents()
            widget.setRowCount(1000)
            remplir_table(table, widget)

        conn.close()

    def selectionner_liste(self):
        # Liste des correspondances : (nom_table, champs_ui)
        correspondances = [
            ("tableWidget_affichage_pays", ["txt_id_pays", "txt_pays"]),
            ("tableWidget_affichage_sexe",  ["txt_id_sexe",  "txt_sexe"]),
            ("tableWidget_affichage_religion",["txt_id_religion","txt_religion"]),
            ("tableWidget_affichage_banque",["txt_id_banque","txt_banque"]),
            ("tableWidget_affichage_ethnie",["txt_id_ethnie","txt_ethnie"]),
        ]
        
        for nom_table, champs in correspondances:
            table_widget = getattr(self.ui, nom_table)  # Récupère la table par son nom
            items_selectionnes = table_widget.selectedItems()
            row_data = [item.text() for item in items_selectionnes]

            if len(row_data) == self.ncol_tableWidget_ui:
                getattr(self.ui, champs[0]).setText(row_data[0])
                getattr(self.ui, champs[1]).setText(row_data[1])

    
        
    # Service
    def nouveau_sexe(self):
        self.ui.txt_id_sexe.setText("")
        self.ui.txt_sexe.setText("")
    
    def ajouter_sexe(self):
        id = self.ui.txt_id_sexe.text()
        sexe = self.ui.txt_sexe.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
            
        if self.valider_form(champs = "sexe") == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_sexe (sexe,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(sexe,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration sexe","Succès !")

        self.nouveau_sexe()
        self.afficher_liste()
         
    def modifier_sexe(self):
        id = self.ui.txt_id_sexe.text()
        sexe = self.ui.txt_sexe.text()
        date_modification = datetime.today()
            
        if self.valider_form(champs = "sexe",pour_modifier = True) == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_sexe SET sexe = ?, date_modification = ?  WHERE id = ?"
                conn.execute(req,(sexe,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration sexe","Succès !")
            else:
                QMessageBox.critical(self,"Configuration sexe","Aucune modification effectuée !")

        self.nouveau_sexe()
        self.afficher_liste()
        
    def supprimer_sexe(self):
        id = self.ui.txt_id_sexe.text()
        reponse = QMessageBox.information(self,"Configuration sexe","Voulez-vous supprimer ce sexe ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_sexe WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration sexe","Succès !")

        self.nouveau_sexe()
        self.afficher_liste()
                  
         
    # pays
    def nouveau_pays(self):
        self.ui.txt_id_pays.setText("")
        self.ui.txt_pays.setText("")
        
    def ajouter_pays(self):
        id = self.ui.txt_id_pays.text()
        pays = self.ui.txt_pays.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        if self.valider_form(champs = "pays") == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_pays (pays,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(pays,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration pays","Succès !")

        self.nouveau_pays()
        self.afficher_liste()
            
            
    def modifier_pays(self):
        id = self.ui.txt_id_pays.text()
        pays = self.ui.txt_pays.text()
        date_modification = datetime.today()
            
        if self.valider_form(champs = "pays",pour_modifier = True) == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_pays SET pays = ?, date_modification = ? WHERE id = ?"
                conn.execute(req,(pays,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration pays","Succès !")
            else:
                QMessageBox.critical(self,"Configuration pays","Aucune modification effectuée !")

        self.nouveau_pays()
        self.afficher_liste()
            
        
    def supprimer_pays(self):
        id = self.ui.txt_id_pays.text()
        reponse = QMessageBox.information(self,"Configuration pays","Voulez-vous supprimer ce pays ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_pays WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration pays","Succès !")

        self.nouveau_pays()
        self.afficher_liste()   
    
            
    # religion (Corps)
    def nouveau_religion(self):
        self.ui.txt_id_religion.setText("")
        self.ui.txt_religion.setText("")
        
    def ajouter_religion(self):
        id = self.ui.txt_id_religion.text()
        religion = self.ui.txt_religion.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        if self.valider_form(champs = "religion") == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_religion (religion,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(religion,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration religion","Succès !")
            
        self.nouveau_religion()
        self.afficher_liste()
        

    def modifier_religion(self):
        id = self.ui.txt_id_religion.text()
        religion = self.ui.txt_religion.text()
        date_modification = datetime.today()
            
        if self.valider_form(champs = "religion",pour_modifier = True) == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_religion SET religion = ?, date_modification = ? WHERE id = ?"
                conn.execute(req,(religion,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration religion","Succès !")
            else:
                QMessageBox.critical(self,"Configuration religion","Aucune modification effectuée !")

        self.nouveau_religion()
        self.afficher_liste()
    
            
    def supprimer_religion(self):
        id = self.ui.txt_id_religion.text()
        reponse = QMessageBox.information(self,"Configuration religion","Voulez-vous supprimer cette religion ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_religion WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration religion","Succès !")

        self.nouveau_religion()
        self.afficher_liste()
        
        
    # Catégorie socio professionnelle
    def nouveau_banque(self):
        self.ui.txt_id_banque.setText("")
        self.ui.txt_banque.setText("")
        
    def ajouter_banque(self):
        id = self.ui.txt_id_banque.text()
        banque = self.ui.txt_banque.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        if self.valider_form(champs = "banque") == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_banque (banque,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(banque,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration Banque","Succès !")
            
        self.nouveau_banque()
        self.afficher_liste()
        

    def modifier_banque(self):
        id = self.ui.txt_id_cat_socio_professionnelle.text()
        banque = self.ui.txt_cat_socio_professionnelle.text()
        date_modification = datetime.today()
            
        if self.valider_form(champs = "banque",pour_modifier = True) == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_banque SET banque = ?, date_modification = ? WHERE id = ?"
                conn.execute(req,(banque,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration catégorie","Succès !")
            else:
                QMessageBox.critical(self,"Configuration catégorie","Aucune modification effectuée !")

        self.nouveau_banque()
        self.afficher_liste()
    
            
    def supprimer_banque(self):
        id = self.ui.txt_id_cat_socio_professionnelle.text()
        reponse = QMessageBox.information(self,"Configuration catégorie","Voulez-vous supprimer cette banque ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_banque WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration banque","Succès !")

        self.nouveau_banque()
        self.afficher_liste()
    
    
    # ethnie
    def nouveau_ethnie(self):
        self.ui.txt_id_ethnie.setText("")
        self.ui.txt_ethnie.setText("")
        
    def ajouter_ethnie(self):
        id = self.ui.txt_id_ethnie.text()
        ethnie = self.ui.txt_ethnie.text()
        date_creation = datetime.today()
        date_modification = datetime.today()
        
        if self.valider_form(champs = "ethnie") == True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            req = "INSERT INTO liste_ethnie (ethnie,date_creation, date_modification) VALUES (?, ?, ?)"
            conn.execute(req,(ethnie,date_creation,date_modification,))
            conn.commit()
            conn.close()
            QMessageBox.information(self,"Configuration ethnie","Succès !")
            
        self.nouveau_ethnie()
        self.afficher_liste()
        

    def modifier_ethnie(self):
        id = self.ui.txt_id_ethnie.text()
        ethnie = self.ui.txt_ethnie.text()
        date_modification = datetime.today()
            
        if self.valider_form(champs = "ethnie",pour_modifier = True) == True:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "UPDATE liste_ethnie SET ethnie = ?, date_modification = ? WHERE id = ?"
                conn.execute(req,(ethnie,date_modification,int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration ethnie","Succès !")
            else:
                QMessageBox.critical(self,"Configuration ethnie","Aucune modification effectuée !")

        self.nouveau_ethnie()
        self.afficher_liste()
    
            
    def supprimer_ethnie(self):
        id = self.ui.txt_id_ethnie.text()
        reponse = QMessageBox.information(self,"Configuration ethnie","Voulez-vous supprimer ce ethnie ?",QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if id != "":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                req = "DELETE FROM liste_ethnie WHERE id = ?"
                conn.execute(req,(int(id),))
                conn.commit()
                conn.close()
                QMessageBox.information(self,"Configuration ethnie","Succès !")

        self.nouveau_ethnie()
        self.afficher_liste()
    
    def remplir_parametre(self,champs,data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        req = f"SELECT * FROM liste_{champs}"
        cursor.execute(req)
        table_data = cursor.fetchone()
        if table_data == None: #table vide            
            for row_data in data:
                req = f"SELECT * FROM liste_{champs} WHERE {champs} = ?"
                cursor.execute(req,(row_data,))
                if cursor.fetchone() == None:
                    req = f"INSERT INTO liste_{champs} ({champs},date_creation, date_modification) VALUES (?, ?, ?)"
                    conn.execute(req,(row_data,datetime.now(),datetime.now(),))
                    conn.commit()
        conn.close()
        
    
        
    