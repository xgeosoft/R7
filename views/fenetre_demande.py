import sqlite3
import os
import qrcode
import tempfile
import base64
from io import BytesIO
from  utils import utilitaires
from class_ui.fenetre_demande_ui import Ui_FenetreDemande
from views.fenetre_parametre_demande import FenetreParametreDemande
from views.fenetre_chercher_personnel import FenetreChercherPersonnel
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog, QVBoxLayout
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPixmap,QTextDocument
from PyQt5.QtPrintSupport import QPrinter,QPrintPreviewDialog
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
        self.ui.btn_demande_pdf.clicked.connect(self.generer_demande_pdf)
        
        
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
            
            return result[0]
    
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
        validation_demande = "Oui"
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
        
    def generer_demande_pdf(self):
        id_demande = self.selectionner_demande()
        if not id_demande is None:
              return self.demande_pdf(id_demande=id_demande)

    def demande_pdf(self,id_demande):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if not id_demande:
            QMessageBox.information(self, "Erreur", "Vous devez sélectionner une demande.")
        else:
            # Récupération des informations du personnel et de la demande à partir de la BDD
            # En utilisant les ID du formulaire, non des valeurs codées en dur
            cursor.execute("""
                SELECT objet, date_debut, date_fin, date_modification,description,id_personnel
                FROM demande WHERE id = ?
            """, (id_demande,))
            info_demande = cursor.fetchone()
            
            if info_demande:
                id_personnel = int(info_demande[5])
                cursor.execute("""
                    SELECT id, matricule, nom, prenom, sexe,
                        (strftime('%Y', 'now') - strftime('%Y', date_naissance)) - 
                        (strftime('%m-%d', 'now') < strftime('%m-%d', date_naissance)) AS Age
                    FROM personnel WHERE id = ?
                """, (id_personnel,))
                info_personnel = cursor.fetchone()
                
                if not info_personnel or not info_demande:
                    QMessageBox.critical(self, "Erreur", "Informations sur la demande ou le personnel non trouvées.")
                    return

                cursor.execute("""
                    SELECT service, fonction, statut,responsabilite
                    FROM suivi_carriere WHERE id_personnel = ? ORDER BY id DESC LIMIT 1
                """, (id_personnel,))
                info_dernier_poste = cursor.fetchone()
                print(info_dernier_poste)
                if not info_dernier_poste is None:
                    html_poste = f"""
                        <tr><th>Poste</th><th>-</th></tr>
                        <tr><td>Service</td><td>{info_dernier_poste[0]} </td></tr>
                        <tr><td>Corps</td><td>{info_dernier_poste[1]} </td></tr>
                        <tr><td>Fonction</td><td>{info_dernier_poste[3]} </td></tr>
                        <tr><td>Statut</td><td>{info_dernier_poste[2]} </td></tr>
                        
                    """
                else:
                    html_poste = ""
                
                # Génération du code QR
                data_qr = f"ID_Demande={id_demande}&ID_Personnel={id_personnel}"
                qr = qrcode.QRCode(
                    version=3,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=1,
                )
                qr.add_data(data_qr)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convertir l'image PIL en base64 pour l'intégrer dans le HTML
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                qr_code_src = f"data:image/png;base64,{img_str}"

                # Génération HTML avec CSS injecté et le code QR en base64
                html = f"""
                    <!DOCTYPE html>
                    <html lang="fr">
                    <head>
                        <meta charset="UTF-8">
                        <title>Demande d'acte administratif</title>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <img src="{resource_path("images/ressources/entete.jpg")}" alt="Entête" width=800 height=165>
                                <h1>Centre Hospitalier Universitaire Départemental Borgou-Alibori</h1>
                                <div class="document_name">DEMANDE D'ACTE ADMINISTRATIF</div>
                            </div>
                            
                            <table class = "tabledemande" width=800>
                                <tr><td>Demande N°</td><td>{id_demande}</td>
                                <td>Fait le : </td><td>{datetime.fromisoformat(info_demande[3]).strftime("%d/%m/%Y %H:%M:%S")}</td></tr>
                            </table>

                            <table class = "tabledemande" width=800 line-height=0.05 border=1 border-color="#ddd">
                                <tr><th>Identification</th><th>-</th></tr>
                                <tr><td>Matricule</td><td>{info_personnel[1]}</td></tr>
                                <tr><td>Nom et Prénom (s)</td><td>{info_personnel[2] + " " + info_personnel[3]}</td></tr>
                                <tr><td>Sexe</td><td>{info_personnel[4]}</td></tr>
                                { html_poste }
                                <tr><th>Demande</th><th>-</th></tr>
                                <tr><td>Objet</td><td>{info_demande[0]}</td></tr>
                                <tr><td>Description</td><td>{"-" if info_demande[4] == "" else info_demande[4]}</td></tr>
                                <tr><td>Date de début</td><td>{datetime.fromisoformat(info_demande[1]).strftime("%d/%m/%Y")}</td></tr>
                                <tr><td>Date de fin</td><td>{datetime.fromisoformat(info_demande[2]).strftime("%d/%m/%Y")}</td></tr>
                            </table>

                            <table class = "responsable" width = 800 border= "#fff">
                                <tr>
                                    <td>Le Chef service</td>
                                    <td>Le DAF</td>
                                    <td>Le DG</td>
                                    <td><img src="{qr_code_src}" alt="Code QR de la demande"></td>
                                </tr>
                            </table>
                            <div class="footer">
                                <h4>Le CHUD-BA vous remercie !</h4>
                            </div>
                        </div>
                    </body>
                    </html>
                """
                
                document = QTextDocument()
                document.setDefaultStyleSheet(utilitaires.css_code)
                document.setHtml(html)

                # Créer un aperçu de l'imprimante
                printer = QPrinter()
                marge = -1000
                printer.setPageMargins(marge, marge, marge, marge, QPrinter.Millimeter)

                preview_dialog = QPrintPreviewDialog(printer, self)
                preview_dialog.paintRequested.connect(document.print_)
                preview_dialog.exec_()