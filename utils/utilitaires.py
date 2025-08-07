import os
import sys

def resource_path(relative_path):
    """Retourne le chemin absolu pour les ressources (images, db...)"""
    if getattr(sys, 'frozen', False):  # PyInstaller
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


pays_liste_fr = [
    'Aruba', 'Afghanistan', 'Angola', 'Anguilla', 'Îles Åland', 'Albanie', 'Andorre',
    'Émirats arabes unis', 'Argentine', 'Arménie', 'Samoa américaines', 'Antarctique',
    'Terres australes françaises', 'Antigua-et-Barbuda', 'Australie', 'Autriche', 'Azerbaïdjan',
    'Burundi', 'Belgique', 'Bénin', 'Burkina Faso', 'Bangladesh', 'Bulgarie', 'Bahreïn',
    'Bahamas', 'Bosnie-Herzégovine', 'Saint-Barthélemy', 'Bélarus', 'Belize', 'Bermudes',
    'Bolivie', 'Brésil', 'Barbade', 'Brunei Darussalam', 'Bhoutan', 'Île Bouvet',
    'Botswana', 'République centrafricaine', 'Canada', 'Îles Cocos (Keeling)', 'Suisse',
    'Chili', 'Chine', 'Côte d’Ivoire', 'Cameroun', 'Congo (République démocratique du)',
    'Congo', 'Îles Cook', 'Colombie', 'Comores', 'Cap-Vert', 'Costa Rica', 'Cuba',
    'Curaçao', 'Île Christmas', 'Îles Caïmans', 'Chypre', 'Tchéquie', 'Allemagne', 'Djibouti',
    'Dominique', 'Danemark', 'République dominicaine', 'Algérie', 'Équateur', 'Égypte', 'Érythrée',
    'Sahara occidental', 'Espagne', 'Estonie', 'Éthiopie', 'Finlande', 'Fidji', 'Îles Malouines',
    'France', 'Îles Féroé', 'Micronésie', 'Gabon', 'Royaume-Uni', 'Géorgie', 'Guernesey',
    'Ghana', 'Gibraltar', 'Guinée', 'Guadeloupe', 'Gambie', 'Guinée-Bissau', 'Guinée équatoriale',
    'Grèce', 'Grenade', 'Groenland', 'Guatemala', 'Guyane française', 'Guam', 'Guyana', 'Hong Kong',
    'Îles Heard et McDonald', 'Honduras', 'Croatie', 'Haïti', 'Hongrie', 'Indonésie',
    'Irlande', 'Israël', 'Île de Man', 'Inde', 'Territoire britannique de l’océan Indien', 'Irak',
    'Iran', 'Islande', 'Italie', 'Jersey', 'Jamaïque', 'Jordanie', 'Japon', 'Kenya', 'Kirghizistan',
    'Cambodge', 'Kiribati', 'Comores', 'Saint-Kitts-et-Nevis', 'Corée du Nord', 'Corée du Sud',
    'Koweït', 'Kazakhstan', 'République démocratique populaire lao', 'Liban', 'Sainte-Lucie',
    'Liechtenstein', 'Sri Lanka', 'Libéria', 'Lesotho', 'Lituanie', 'Luxembourg', 'Lettonie',
    'Libye', 'Maroc', 'Monaco', 'Moldavie', 'Monténégro', 'Saint-Martin (partie française)',
    'Madagascar', 'Îles Marshall', 'Macédoine du Nord', 'Mali', 'Myanmar', 'Mongolie',
    'Macao', 'Îles Mariannes du Nord', 'Martinique', 'Mauritanie', 'Montserrat', 'Malte',
    'Maurice', 'Maldives', 'Malawi', 'Mexique', 'Malaisie', 'Mozambique', 'Namibie', 'Nouvelle-Calédonie',
    'Niger', 'Île Norfolk', 'Nigéria', 'Nicaragua', 'Pays-Bas', 'Norvège', 'Népal',
    'Nauru', 'Niue', 'Nouvelle-Zélande', 'Oman', 'Panama', 'Pérou', 'Polynésie française', 'Papouasie-Nouvelle-Guinée',
    'Philippines', 'Pakistan', 'Pologne', 'Saint-Pierre-et-Miquelon', 'Pitcairn', 'Porto Rico',
    'Palestine', 'Portugal', 'Palaos', 'Paraguay', 'Qatar', 'La Réunion', 'Roumanie',
    'Serbie', 'Fédération de Russie', 'Rwanda', 'Arabie saoudite', 'Îles Salomon', 'Seychelles',
    'Soudan', 'Suède', 'Singapour', 'Sainte-Hélène', 'Slovénie', 'Svalbard et Jan Mayen',
    'Slovaquie', 'Sierra Leone', 'Saint-Marin', 'Sénégal', 'Somalie', 'Suriname', 'Soudan du Sud',
    'Sao Tomé-et-Principe', 'Salvador', 'Saint-Martin (partie néerlandaise)', 'Syrie',
    'Eswatini', 'Îles Turques-et-Caïques', 'Tchad', 'Terres australes françaises', 'Togo',
    'Thaïlande', 'Tadjikistan', 'Tokelau', 'Timor oriental', 'Turkménistan', 'Tunisie', 'Tonga',
    'Turquie', 'Trinité-et-Tobago', 'Tuvalu', 'Taïwan', 'Tanzanie', 'Ukraine', 'Ouganda',
    'Îles mineures éloignées des États-Unis', 'États-Unis', 'Uruguay', 'Ouzbékistan',
    'Vatican', 'Saint-Vincent-et-les-Grenadines', 'Venezuela', 'Îles Vierges britanniques',
    'Îles Vierges des États-Unis', 'Viêt Nam', 'Vanuatu', 'Wallis-et-Futuna', 'Samoa', 'Yémen',
    'Mayotte', 'Afrique du Sud', 'Zambie', 'Zimbabwe'
]

groupes_ethniques_benin = [
    "Fon (et groupes apparentés)",
    "Adja (et apparentés)",
    "Yoruba (et apparentés)",
    "Bariba (Baatombu)",
    "Fulani (Peul/Fulbé)",
    "Ottamari (Otammari / Betammaribè / Somba)",
    "Yoa‑Lokpa",
    "Dendi (Songhai)",
    "Goun (Gun)",
    "Autres ethnies"
]
        
situations_matrimoniales = [
    "Célibataire",
    "Marié(e)",
    "Veuf / Veuve",
    "Divorcé(e)",
    "Séparé(e)",
    "Pacsé(e)",
    "Union libre",
    "Fiancé(e)"
]


liste_religions = [
    "Athé (e)",
    "Christianisme",
    "Islam",
    "Religions traditionnelles",
    "Autres religions",
    "Sans religion"
]