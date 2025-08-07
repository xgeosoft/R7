import sqlite3
from utils.utilitaires import resource_path

class DBManager:
    def __init__(self, db_path=resource_path("data/database.db")):
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
            numero_rib TEXT NOT NULL,
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
        req_service = """CREATE TABLE IF NOT EXISTS service(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_personnel INTEGER NOT NULL,  -- Clé étrangère
            service_actuel TEXT NOT NULL,
            description_des_tache TEXT,
            autorisation_chef_service TEXT NOT NULL,
            autorisation_responsable_centre TEXT NOT NULL,
            date_creation DATE NOT NULL,
            date_modification DATE NOT NULL,
            FOREIGN KEY (id_personnel) REFERENCES personnel(id)
            )"""

        self.cursor.execute(req_service)
        
                
        # create table query
        req_config_demande = """CREATE TABLE IF NOT EXISTS liste_demande(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objet TEXT NOT NULL UNIQUE,
            nb_jours INTEGER NOT NULL,
            date_creation DATE NOT NULL,
            date_modification DATE NOT NULL
            )"""

        self.cursor.execute(req_config_demande)
        
        # envoyer changement
        self.conn.commit()
        self.conn.close()

    def get_personnel(self):
        self.cursor.execute("SELECT * FROM personnel")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
        
        
