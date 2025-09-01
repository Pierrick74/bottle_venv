
# Bottle Todo App

Application web de gestion de tâches développée avec le framework Python Bottle pour l'apprentissage et l'entraînement.

## 🚀 Installation

### Prérequis
- Python 3.x
- pip

### Configuration de l'environnement

1. **Cloner le projet**
   ```bash
   git clone https://github.com/Pierrick74/bottle_venv.git
   cd bottle_venv
   ```

2. **Créer l'environnement virtuel**
   ```bash
   sudo apt install python3-venv
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip3 install bottle waitress
   ```

## 🗄️ Base de données

Initialiser la base de données avant le premier lancement :

```bash
python3 Database_init.py
```

## 🏃 Lancement

```bash
python3 todo.py
```

L'application sera accessible à l'adresse : `http://localhost:8080`

## 📁 Structure du projet

```
bottle_venv/
├── .venv/              # Environnement virtuel
├── Database_init.py    # Script d'initialisation de la DB
├── todo.py            # Application principale
├── todo.db            # base de données en SQLite
└── README.md          # Documentation
```

## 🛠️ Technologies utilisées

- **Bottle** : Framework web minimaliste Python
- **Waitress** : Serveur WSGI de production
- **SQLite** : Base de données (supposée)

## 📝 Fonctionnalités

- Gestion de tâches (CRUD)
- Interface web simple
- Base de données intégrée

## 🔧 Développement

### Activation de l'environnement virtuel
```bash
source .venv/bin/activate
```

### Désactivation
```bash
deactivate
```

## 📜 Licence

Projet éducatif - Utilisation libre pour l'apprentissage.