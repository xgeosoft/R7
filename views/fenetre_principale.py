from PyQt5.QtWidgets import QMainWindow, QAction,QWidget
from class_ui.fenetre_principale_ui import Ui_FenetrePrincipale
from views.fenetre_profil_personnel import FenetreProfilPersonnel
from views.fenetre_acceuil import FenetreAcceuil
from views.fenetre_demande import FenetreDemande

class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetrePrincipale()
        self.ui.setupUi(self)
        

        # Configuration de la barre de menu
        self.configurer_barre_menu()

    def ouvrir_information_personnel(self):
        fenetre = FenetreProfilPersonnel()
        self.setCentralWidget(fenetre)

    def ouvrir_formulaire_demande(self):
        fenetre = FenetreDemande()
        self.setCentralWidget(fenetre)

    def ouvrir_formulaire_acceuil(self):
        # Si tu veux revenir à un état vide ou un widget d'accueil, tu peux créer un QWidget vide :
        fenetre = FenetreAcceuil()
        self.setCentralWidget(fenetre)  # widget vide = "page d'accueil"

    def configurer_barre_menu(self):
        # Barre de menu principale
        menubar = self.menuBar()

        # Menus principaux
        menu_acceuil = menubar.addMenu("Accueil")
        menu_menu = menubar.addMenu("Menu")
        menu_fichiers = menubar.addMenu("Documents")

        # Action Accueil
        action_acceuil = QAction("Accueil", self)
        action_acceuil.triggered.connect(self.ouvrir_formulaire_acceuil)
        menu_acceuil.addAction(action_acceuil)

        # Action Personnel
        action_personnel = QAction("Gestion du personnel", self)
        action_personnel.triggered.connect(self.ouvrir_information_personnel)
        menu_menu.addAction(action_personnel)

        # Action Demande
        action_demande = QAction("Gestion des demandes", self)
        action_demande.triggered.connect(self.ouvrir_formulaire_demande)
        menu_menu.addAction(action_demande)
        