from PyQt5.QtWidgets import QMainWindow, QAction,QWidget
from class_ui.fenetre_principale_ui import Ui_FenetrePrincipale
from views.fenetre_profil_personnel import FenetreProfilPersonnel
from views.fenetre_acceuil import FenetreAcceuil
from views.fenetre_demande import FenetreDemande
from views.fenetre_parametre_demande import FenetreParametreDemande
from views.fenetre_parametre_carriere import FenetreParametreSuiviCarriere
from views.fenetre_suivi_carriere import FenetreSuiviCarriere

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

    def ouvrir_formulaire_parametre_demande(self):
        fenetre = FenetreParametreDemande()
        self.setCentralWidget(fenetre)
        
    def ouvrir_formulaire_gestion_carriere(self):
        fenetre = FenetreSuiviCarriere()
        self.setCentralWidget(fenetre)
        
    def ouvrir_formulaire_parametre_suivi_carriere(self):
        fenetre = FenetreParametreSuiviCarriere()
        self.setCentralWidget(fenetre)  # widget vide = "page d'accueil"


    def configurer_barre_menu(self):
        # Barre de menu principale
        menubar = self.menuBar()

        # Menus principaux
        menu_fichier = menubar.addMenu("Fichiers")
        menu_acceuil = menubar.addMenu("Accueil")
        menu_activites = menubar.addMenu("Activités")
        menu_document = menubar.addMenu("Documents")
        menu_parametre = menubar.addMenu("Configurations")
        menu_aide = menubar.addMenu("Aides")

        ########################################################################
        # Action Accueil
        
        action_acceuil = QAction("Accueil", self)
        action_acceuil.triggered.connect(self.ouvrir_formulaire_acceuil)
        menu_acceuil.addAction(action_acceuil)

        ########################################################################
        # ACTIVITES
        
        # Action Personnel
        action_personnel = QAction("Profil personnel", self)
        action_personnel.triggered.connect(self.ouvrir_information_personnel)
        menu_activites.addAction(action_personnel)

        # Action Demande
        action_demande = QAction("Demandes", self)
        action_demande.triggered.connect(self.ouvrir_formulaire_demande)
        menu_activites.addAction(action_demande)
        
        # Action Carrière
        action_carriere = QAction("Gestion carrière", self)
        action_carriere.triggered.connect(self.ouvrir_formulaire_gestion_carriere)
        menu_activites.addAction(action_carriere)
        
        ########################################################################
        # Configurations
        
        # suivi carrière
        action_param_suivi_carriere = QAction("Carrières",self)
        action_param_suivi_carriere.triggered.connect(self.ouvrir_formulaire_parametre_suivi_carriere)
        menu_parametre.addAction(action_param_suivi_carriere)
        
        # demandes
        action_param_demande = QAction("Demandes",self)
        action_param_demande.triggered.connect(self.ouvrir_formulaire_parametre_demande)
        menu_parametre.addAction(action_param_demande)