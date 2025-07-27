import sqlite3
from  utils import utilitaires
from class_ui.fenetre_personnel_ui import Ui_FenetrePersonnel
from PyQt5.QtWidgets import QWidget, QMessageBox

class FenetrePersonnel(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetrePersonnel()
        self.ui.setupUi(self)
        
        
        # initialisation du formulaire
        # id
        self.ui.txt_id.setEnabled(False) # vérrouiller l'id
        ## religion
        self.ui.comboBox_religion.setCurrentIndex(-1) # pas de sélection par défaut
        ## ethnie        
        self.ui.comboBox_ethnie.addItems(utilitaires.groupes_ethniques_benin)
        self.ui.comboBox_ethnie.setCurrentIndex(-1) # pas de sélection par défaut
        ## nationalité
        self.ui.comboBox_nationalite.addItems(utilitaires.pays_liste_fr)
        self.ui.comboBox_nationalite.setCurrentText('Bénin')
        #sexe
        self.ui.comboBox_sexe.setCurrentIndex(-1)

        # boutons
        self.ui.btn_quitter.clicked.connect(self.quitter_formulaire)
        self.ui.btn_ajouter.clicked.connect(self.ajouter_personnel)
        
    def quitter_formulaire(self):
        self.close()
        
    def valider_formulaire(self):
        erreur = []
        matricule = self.ui.txt_matricule.text()
        nom = self.ui.txt_nom.text()
        date_naissance = self.ui.dateEdit_date_naissance.date().toString("yyyy-MM-dd")
        telephone1 = self.ui.txt_telephone1.text()
        
        if matricule == "":
            erreur.append("Le matricule de cet employé est vide. Veuillez corriger.")
            self.ui.txt_matricule.setStyleSheet("border: 1px solid red;")
        elif nom == "":
            erreur.append("Le nom n'est pas renseigné.")
        elif date_naissance == "":
            erreur.append("La date de naissance n'est pas renseigné.")
        elif telephone1 == "":
            erreur.append("Le premier numéro de téléphone doit être renseigné.")

        print(len(erreur))
        if erreur == []:
            QMessageBox.information(self, "Succès", "Formulaire soumis avec succès !")
        else:
            QMessageBox.warning(self, "Champs manquants", "\n".join(erreur))
        return(erreur == [])
        
        
    def ajouter_personnel(self):
        #conn = sqlite3.connect("data/database.db")
        #cursor = conn.cursor()
        
        id = self.ui.txt_id.text()
        matricule = self.ui.txt_matricule.text()
        nom = self.ui.txt_nom.text()
        prenom = self.ui.txt_prenom.text()
        sexe = self.ui.comboBox_sexe.currentText()
        date_naissance = self.ui.dateEdit_date_naissance.date().toString("yyyy-MM-dd")
        religion = self.ui.comboBox_religion.currentText()
        ethnie = self.ui.comboBox_ethnie.currentText()
        nationalite = self.ui.comboBox_nationalite.currentText()
        telephone1 = self.ui.txt_telephone1.text()
        telephone2 = self.ui.txt_telephone2.text()
        email = self.ui.txt_email.text()
        url_photo = self.ui.txt_url_photo.text()
        
        self.valider_formulaire
        
    
    
    
        

        
