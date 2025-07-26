from PyQt5.QtWidgets import QApplication
from views.fenetre_principale import MenuPrincipale
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    fenetre = MenuPrincipale()
    fenetre.show()
    sys.exit(app.exec_())
    
    
