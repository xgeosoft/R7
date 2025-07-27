from PyQt5.QtWidgets import QApplication, QMainWindow,QWidget
from class_ui.fenetre_principale_ui import Ui_FenetrePrincipale
from views.fenetre_personnel import FenetrePersonnel


class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FenetrePrincipale()
        self.ui.setupUi(self)
        
        self.fenetre_personnel = FenetrePersonnel()
        
        self.ui.btn_information_personnel.clicked.connect(self.ouvrir_information_personnel)
        
    
    def ouvrir_information_personnel(self):
        self.setCentralWidget(self.fenetre_personnel)
        
    
    
