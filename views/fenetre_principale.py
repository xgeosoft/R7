# views/main_window.py
from PyQt5.QtWidgets import QMainWindow
from class_ui.menu_principale_ui import Ui_MenuPrincipale  # Fichier .py généré depuis Qt Designer
from models.database_manager import DBManager
from views.fenetre_personnel import FenetrePersonnel
from views.fenetre_demande_conge import FenetreDemande

#UI ACTUEL ET VIEUW D4AUTRE FONCTION 

class MenuPrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        DBManager.__init__(self,db_path="data/database.db")

        # Charger l'interface depuis la classe générée
        self.ui = Ui_MenuPrincipale()
        self.ui.setupUi(self)

        # Connexion de l'action menu vers la méthode de navigation
        self.ui.pushButton_ouvrir_personnel.clicked.connect(self.ouvrir_personnel)
        self.ui.pushButton_ouvrir_conge.clicked.connect(self.ouvrir_demande_conge)

    def ouvrir_personnel(self):
        self.fenetrepersonnel = FenetrePersonnel()
        self.fenetrepersonnel.show()
        
    def ouvrir_demande_conge(self):
        self.fenetredemandeconge = FenetreDemande()
        self.fenetredemandeconge.show()