import sys
import os
from PyQt5.QtWidgets import QApplication
from views.fenetre_principale import FenetrePrincipale
from models.database_manager import DBManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetrePrincipale()
    data_base_object = DBManager()
    fenetre.show()
    sys.exit(app.exec_())
    
    