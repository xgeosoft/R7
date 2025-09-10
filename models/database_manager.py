import sqlite3
from utils.utilitaires import resource_path

class DBManager():
    def __init__(self,db_path= resource_path("data/database.db")):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # create table query
        req_personnel = """CREATE TABLE IF NOT EXISTS personnel(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricule TEXT NOT NULL UNIQUE,
            npi TEXT NOT NULL UNIQUE,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            sexe TEXT NOT NULL,
            date_naissance DATE NOT NULL,
            situation_matrimoniale TEXT NOT NULL,
            religion TEXT NOT NULL,
            ethnie TEXT,
            nationalite TEXT NOT NULL,
            telephone1 TEXT NOT NULL,
            telephone2 TEXT,
            adresse TEXT,
            email TEXT,
            url_photo TEXT,
            numero_ifu TEXT NOT NULL,
            numero_cnss TEXT,
            banque TEXT NOT NULL,
            numero_rib TEXT NOT NULL,
            personnel_actif TEXT NOT NULL,
            date_creation DATE NOT NULL,
            date_modification DATE NOT NULL
            )"""
        self.cursor.execute(req_personnel)
        
        
        # create table query
        req_demande = """CREATE TABLE IF NOT EXISTS demande(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_personnel INTEGER NOT NULL,  -- Clé étrangère
            objet TEXT NOT NULL,
            date_debut DATE NOT NULL,
            date_fin DATE NOT NULL,
            description TEXT,
            autorisation_chef_service TEXT NOT NULL,
            validation_demande TEXT NOT NULL,
            date_creation DATE NOT NULL,
            date_modification DATE NOT NULL,
            FOREIGN KEY (id_personnel) REFERENCES personnel(id)
            )"""
        self.cursor.execute(req_demande)
        
        
        # create table query
        req_suivi_carriere = """CREATE TABLE IF NOT EXISTS suivi_carriere(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_personnel INTEGER NOT NULL,  -- Clé étrangère
            service TEXT NOT NULL,
            fonction TEXT NOT NULL,
            statut TEXT NOT NULL,
            categorie TEXT NOT NULL,
            niveau_grade TEXT NOT NULL,
            responsabilite TEXT NOT NULL,
            description_tache TEXT,
            date_prise_service DATE NOT NULL,
            autorisation_chef_service TEXT NOT NULL,
            autorisation_responsable_centre TEXT NOT NULL,
            date_creation DATE NOT NULL,
            date_modification DATE NOT NULL,
            FOREIGN KEY (id_personnel) REFERENCES personnel(id)
            )"""
        self.cursor.execute(req_suivi_carriere)
        
        
        # create table query
        req_config_demande = """CREATE TABLE IF NOT EXISTS liste_demande(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objet TEXT NOT NULL UNIQUE,
            nb_jours INTEGER NOT NULL,
            date_creation DATE NOT NULL,
            date_modification DATE NOT NULL
            )"""
        self.cursor.execute(req_config_demande)
        
        req_config_path = """CREATE TABLE IF NOT EXISTS file_path(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_type TEXT NOT NULL,
            path TEXT NOT NULL
            )"""
        self.cursor.execute(req_config_path)
        
        liste_parametre = [
            ("service","liste_service",),
            ("statut","liste_statut",),
            ("fonction","liste_fonction",),
            ("categorie","liste_categorie_professionnelle",),
            ("grade","liste_grade",),
            ("responsabilite","liste_autre_responsabilite",),
            ("sexe","liste_sexe",),
            ("religion","liste_religion",),
            ("pays","liste_pays",),
            ("ethnie","liste_ethnie",),
            ("banque","liste_banque",),
        ]
        
        # create table query
        for colonne,table_name in liste_parametre:   
            req_liste_parametre = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {colonne} TEXT NOT NULL UNIQUE,
                date_creation DATE NOT NULL,
                date_modification DATE NOT NULL
                )"""
            self.cursor.execute(req_liste_parametre)
            
        # envoyer changement
        self.conn.commit()
        self.conn.close()

    def get_personnel(self):
        self.cursor.execute("SELECT * FROM personnel")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
        
        
