import sqlite3

class DBManager:
    def __init__(self, db_path="data/database.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
            
        # create table query
        req_personnel = """CREATE TABLE IF NOT EXISTS personnel(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            npi TEXT,
            matricule TEXT NOT NULL UNIQUE,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            date_naissance DATE NOT NULL,
            sexe TEXT NOT NULL,
            religion TEXT NOT NULL,
            telephone1 TEXT NOT NULL,
            telephone2 TEXT,
            email TEXT,
            adresse TEXT,
            photo TEXT,
            date_creation DATE NOT NULL,
            date_modification DATE NOT NULL
            )"""
            
        self.cursor.execute(req_personnel)
        
        # create table query
        req_demande = """CREATE TABLE IF NOT EXISTS demande(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            date_debut DATE NOT NULL,
            date_fin DATE NOT NULL,
            description TEXT,
            autorisation_chef_service TEXT NOT NULL,
            validation_demande TEXT NOT NULL,
            date_creation DATE NOT NULL,
            date_modification DATE NOT NULL
            )"""
            
        self.cursor.execute(req_demande)
        
        # envoyer changement
        self.conn.commit()
        self.conn.close()

    def get_personnel(self):
        self.cursor.execute("SELECT * FROM personnel")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
        
        
