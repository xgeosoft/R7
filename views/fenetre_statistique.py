import sqlite3
import os
import qrcode
import tempfile
import base64
from io import BytesIO
import pandas as pd
import openpyxl
from  utils import utilitaires
from class_ui.fenetre_demande_ui import Ui_FenetreDemande
from class_ui.fenetre_statistique_ui import Ui_FenetreStatistique
from views.fenetre_parametre_demande import FenetreParametreDemande
from views.fenetre_chercher_personnel import FenetreChercherPersonnel
from PyQt5.QtWidgets import QWidget, QMessageBox,QTableWidgetItem,QFileDialog,QDialog, QVBoxLayout
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPixmap,QTextDocument
from PyQt5.QtPrintSupport import QPrinter,QPrintPreviewDialog
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
import matplotlib.pyplot as plt
import io

from utils.utilitaires import resource_path
import time
import shutil

class FenetreStatistique(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetreStatistique()
        self.ui.setupUi(self)
        self.db_path = resource_path("data/database.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # nom table
        all_report = [
           'Carrière du Personnel',
           'Base du Personnel',
           'Base du Personnel Simplifiée',
           'Effectif du personnel par service',
           'Effectif du personnel par statut',
           'Effectif du personnel par corps',
           'Effectif du personnel par responsabilité',
           'Effectif du personnel par catégorie socio professionnelle',
           'Effectif du personnel par service, corps, catégorie socio professionnelle',
           'Répartition des demandes',
        ]
        
        self.ui.comboBox_type_rapport.addItems(all_report)
        self.ui.comboBox_type_rapport.setCurrentIndex(-1)
        self.ui.btn_excel.clicked.connect(self.rapport_excel)
        self.ui.btn_pdf.clicked.connect(self.rapport_pdf)

    
    def rapport_excel(self):
        try:
            self.type_rapport = self.ui.comboBox_type_rapport.currentText()
            # Récupération des informations du personnel et de la demande à partir de la BDD
            # En utilisant les ID du formulaire, non des valeurs codées en dur
            if self.type_rapport == "":
                QMessageBox.warning(self, "Export Excel", f"Aucun rapport sélectionné.",QMessageBox.Ok)
            else:
                self.cursor.execute(f"DROP TABLE IF EXISTS base_personnel;")
                self.cursor.execute(f"CREATE TABLE base_personnel AS SELECT * FROM personnel p LEFT JOIN suivi_carriere c ON c.id_personnel = p.id WHERE c.date_prise_service = (SELECT MAX(date_prise_service) FROM suivi_carriere WHERE id_personnel = p.id LIMIT 1) AND p.personnel_actif = 'Oui';")
                match self.type_rapport:
                    case 'Carrière du Personnel':
                        req = f"SELECT * FROM personnel p LEFT JOIN suivi_carriere c ON p.id = c.id_personnel ORDER BY p.id ASC, c.date_prise_service DESC"
                    case 'Base du Personnel':
                        req = f"SELECT * FROM personnel p LEFT JOIN suivi_carriere c ON c.id_personnel = p.id WHERE c.date_prise_service = (SELECT MAX(date_prise_service) FROM suivi_carriere WHERE id_personnel = p.id LIMIT 1)"
                    case 'Base du Personnel Simplifiée':
                        req = f"SELECT id AS ID, matricule AS Matricule,npi AS NPI, nom AS Nom, prenom AS Prénoms, sexe AS Sexe, strftime('%Y', 'now') - strftime('%Y', date_naissance) - (strftime('%m-%d', 'now') < strftime('%m-%d', date_naissance)) AS Age, situation_matrimoniale AS SitMat , service AS Service, fonction AS Corps, statut AS statut, categorie||niveau_grade AS Grade, responsabilite AS Reponsabilité, date_prise_service AS 'Date de prise de service', banque AS Banque, numero_rib AS RIB, numero_ifu AS IFU, numero_cnss AS 'N° SECU', telephone1 AS 'Tel 1', telephone2 AS 'Tel 2', email AS Email  FROM base_personnel ORDER BY banque ASC"
                    case 'Effectif du personnel par service':
                        req = f"SELECT service, COUNT(*) AS Nombre FROM base_personnel GROUP BY service ORDER BY service"
                    case 'Effectif du personnel par statut':
                        req = f"SELECT statut, COUNT(*) AS Nombre FROM base_personnel GROUP BY statut ORDER BY statut"
                    case 'Effectif du personnel par corps':
                        req = f"SELECT fonction, COUNT(*) AS Nombre FROM base_personnel GROUP BY fonction ORDER BY fonction"
                    case 'Effectif du personnel par responsabilité':
                        req = f"SELECT responsabilite, COUNT(*) AS Nombre FROM base_personnel GROUP BY responsabilite ORDER BY responsabilite"
                    case 'Effectif du personnel par catégorie socio professionnelle':
                        req = f"SELECT categorie, COUNT(*) AS Nombre FROM base_personnel GROUP BY categorie ORDER BY categorie"
                    case 'Effectif du personnel par service, corps, statut, catégorie socio professionnelle':
                        req = f"SELECT service, fonction, statut, categorie, COUNT(*) AS Nombre FROM base_personnel GROUP BY service, fonction, statut, categorie ORDER BY service ASC"
                    case 'Répartition des demandes':
                        req = f"SELECT STRFTIME('%Y',date_modification) AS Année, objet AS Objets, COUNT(*) AS Nombre FROM demande GROUP BY objet ORDER BY Année DESC ,objet ASC"
                
                df = pd.read_sql_query(req, self.conn)
                if df.empty:
                    QMessageBox.warning(self, "Export Excel", f"Aucune donnée disponible.",QMessageBox.Ok)
                else:
                    # Demander à l'utilisateur où sauvegarder le fichier
                    chemin_fichier = resource_path(QFileDialog.getSaveFileName(
                        self,
                        caption="Enregistrer sous",
                        directory="",
                        filter="Fichiers Excel (*.xlsx)"
                    )[0])

                    if chemin_fichier:
                        if not chemin_fichier.endswith(".xlsx"):
                            chemin_fichier += ".xlsx"

                        # Export en Excel
                        df.to_excel(chemin_fichier, index=False, engine="openpyxl")

                        QMessageBox.information(
                            self,
                            "Export Excel",
                            f"{self.type_rapport} a été exportée avec succès vers :\n{chemin_fichier}"
                        )

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'exporter : {e}")

    
    # p.id AS ID, matricule AS Matricule, nom AS Nom, prenom AS Prénoms, sexe AS Sexe, STRFTIME('%Y', (strftime('%Y', 'now') - strftime('%Y', date_naissance)) - (strftime('%m-%d', 'now') < strftime('%m-%d', date_naissance)) AS Age, service AS Service, fonction AS Corps
    def rapport_pdf(self):
        try:
            self.type_rapport = self.ui.comboBox_type_rapport.currentText()
            # Récupération des informations du personnel et de la demande à partir de la BDD
            # En utilisant les ID du formulaire, non des valeurs codées en dur
            if self.type_rapport == "":
                QMessageBox.warning(self, "Export Excel", f"Aucun rapport sélectionné.",QMessageBox.Ok)
            else:
                self.cursor.execute(f"DROP TABLE IF EXISTS base_personnel;")
                self.cursor.execute(f"CREATE TABLE base_personnel AS SELECT * FROM personnel p LEFT JOIN suivi_carriere c ON c.id_personnel = p.id WHERE c.date_prise_service = (SELECT MAX(date_prise_service) FROM suivi_carriere WHERE id_personnel = p.id LIMIT 1) AND p.personnel_actif = 'Oui';")
                self.cursor.execute("SELECT COUNT(*) FROM base_personnel")
                self.nombre_personnel = self.cursor.fetchone()
                
                match self.type_rapport:
                    case 'Carrière du Personnel':
                        req = f"SELECT * FROM personnel p LEFT JOIN suivi_carriere c ON p.id = c.id_personnel ORDER BY p.id ASC, c.date_prise_service DESC"
                    case 'Base du Personnel':
                        req = f"SELECT id AS ID, matricule AS Matricule,npi AS NPI, nom AS Nom, prenom AS Prénoms, sexe AS Sexe, strftime('%Y', 'now') - strftime('%Y', date_naissance) - (strftime('%m-%d', 'now') < strftime('%m-%d', date_naissance)) AS Age, situation_matrimoniale AS SitMat , service AS Service, fonction AS Corps, statut AS statut, categorie||niveau_grade AS Grade, responsabilite AS Reponsabilité, date_prise_service AS 'Date de prise de service', banque AS Banque, numero_rib AS RIB, numero_ifu AS IFU, numero_cnss AS 'N° SECU', telephone1 AS 'Tel 1', telephone2 AS 'Tel 2', email AS Email  FROM base_personnel ORDER BY banque ASC"
                    case 'Base du Personnel Simplifiée':
                        req = f"SELECT id AS ID, matricule AS Matricule,npi AS NPI, nom AS Nom, prenom AS Prénoms, sexe AS Sexe, strftime('%Y', 'now') - strftime('%Y', date_naissance) - (strftime('%m-%d', 'now') < strftime('%m-%d', date_naissance)) AS Age, situation_matrimoniale AS SitMat , service AS Service, fonction AS Corps, statut AS statut, categorie||niveau_grade AS Grade, responsabilite AS Reponsabilité, date_prise_service AS 'Date de prise de service', banque AS Banque, numero_rib AS RIB, numero_ifu AS IFU, numero_cnss AS 'N° SECU', telephone1 AS 'Tel 1', telephone2 AS 'Tel 2', email AS Email  FROM base_personnel ORDER BY banque ASC"
                    case 'Effectif du personnel par service':
                        req = f"SELECT service, COUNT(*) AS Nombre FROM base_personnel GROUP BY service ORDER BY service"
                    case 'Effectif du personnel par statut':
                        req = f"SELECT statut, COUNT(*) AS Nombre FROM base_personnel GROUP BY statut ORDER BY statut"
                    case 'Effectif du personnel par corps':
                        req = f"SELECT fonction, COUNT(*) AS Nombre FROM base_personnel GROUP BY fonction ORDER BY fonction"
                    case 'Effectif du personnel par responsabilité':
                        req = f"SELECT responsabilite, COUNT(*) AS Nombre FROM base_personnel GROUP BY responsabilite ORDER BY responsabilite"
                    case 'Effectif du personnel par catégorie socio professionnelle':
                        req = f"SELECT categorie, COUNT(*) AS Nombre FROM base_personnel GROUP BY categorie ORDER BY categorie"
                    case 'Effectif du personnel par service, corps, statut, catégorie socio professionnelle':
                        req = f"SELECT service, fonction, statut, categorie, COUNT(*) AS Nombre FROM base_personnel GROUP BY service, fonction, statut, categorie ORDER BY service ASC"
                    case 'Répartition des demandes':
                        req = f"SELECT STRFTIME('%Y',date_modification) AS Année, objet AS Objets, COUNT(*) AS Nombre FROM demande GROUP BY objet ORDER BY Année DESC ,objet ASC"
                    
            # Charger en DataFrame
            df = pd.read_sql_query(req, self.conn)

            if df.empty:
                QMessageBox.warning(self, "Rapport PDF", "Aucune donnée disponible.", QMessageBox.Ok)
                return

            # Demander où sauvegarder le PDF
            chemin_fichier = resource_path(QFileDialog.getSaveFileName(
                self,
                caption="Enregistrer le rapport PDF",
                directory="",
                filter="Fichiers PDF (*.pdf)"
            )[0])

            if not chemin_fichier:
                return
            if not chemin_fichier.endswith(".pdf"):
                chemin_fichier += ".pdf"

            # Création du PDF
            doc = SimpleDocTemplate(chemin_fichier, pagesize=landscape(A4))
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name="CustomNormal",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=12,
                leading=12
            ))

            styles.add(ParagraphStyle(
                name="CustomTitle",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=12,
                alignment=TA_CENTER
            ))
            elements = []
            table_font_size = 12
            
            # Titre
            elements.append(Paragraph(f"Rapport Rh7 - {self.type_rapport}", styles["Title"]))
            elements.append(Spacer(0.5, 20))
            if self.type_rapport == 'Base du Personnel':
                elements.append(Paragraph(f"Effectif total du personnel : {self.nombre_personnel[0]}"))
                elements.append(Spacer(0.5, 20))
                table_font_size = 6
            
            # Tableau des données
            table_data = [list(df.columns)] + df.values.tolist()
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Police en gras pour l'en-tête
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), # Exemple de style pour le reste du tableau
                ("FONTSIZE", (0, 0), (-1, -1), table_font_size),  # Définit la taille de la police pour toute la table
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))

            # Si applicable → Ajouter un graphique
            if df.shape[1] == 2 and df.columns[-1] == "Nombre":
                fig, ax = plt.subplots(figsize=(6, 4))
                df.plot(kind="bar", x=df.columns[0], y="Nombre", ax=ax, legend=False, color="skyblue")
                ax.set_title(self.type_rapport)
                ax.set_ylabel("Nombre")
                buf = io.BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0)
                elements.append(Image(buf, width=400, height=250))
                plt.close(fig)

            # Génération
            doc.build(elements)

            QMessageBox.information(self, "Rapport PDF", f"Rapport généré avec succès :\n{chemin_fichier}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de générer le rapport PDF : {e}")


    
        

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