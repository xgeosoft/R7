import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from views.fenetre_principale import FenetrePrincipale
from PyQt5.QtWidgets import QWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetrePrincipale()
    fenetre.show()
    sys.exit(app.exec_())