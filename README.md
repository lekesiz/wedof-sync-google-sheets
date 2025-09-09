# Synchronisation Wedof vers Google Sheets

Ce projet permet de synchroniser automatiquement les données de votre compte Wedof vers un Google Sheet. La synchronisation est effectuée via l'API Wedof et l'API Google Sheets, et peut être exécutée manuellement ou planifiée pour une mise à jour quotidienne.

## Fonctionnalités

- **Synchronisation complète** : Récupère toutes les données des principaux endpoints de l'API Wedof (utilisateurs, formations, sessions, etc.).
- **Intégration Google Sheets** : Crée automatiquement des feuilles pour chaque type de données et y écrit les informations.
- **Mise à jour intelligente** : Vide les feuilles avant chaque synchronisation pour garantir que les données sont toujours à jour.
- **Planification quotidienne** : Peut être configuré pour s'exécuter automatiquement chaque jour à une heure précise.
- **Configuration flexible** : Utilise un fichier `.env` pour gérer les clés d'API et autres paramètres.
- **Gestion des erreurs** : Logging détaillé pour suivre le processus de synchronisation et identifier les problèmes.

## Prérequis

- Python 3.7+
- Un compte Wedof avec une clé API
- Un compte Google avec l'API Google Sheets activée
- Un Google Sheet et un compte de service Google avec les droits d'accès au Sheet

## Installation

1.  **Clonez le dépôt :**

    ```bash
    git clone https://github.com/votre-utilisateur/wedof-sync-google-sheets.git
    cd wedof-sync-google-sheets
    ```

2.  **Créez un environnement virtuel et installez les dépendances :**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## Configuration

1.  **Créez un fichier `.env`** à partir de l'exemple :

    ```bash
    cp .env.example .env
    ```

2.  **Modifiez le fichier `.env`** avec vos informations :

    -   `WEDOF_API_KEY` : Votre clé API Wedof.
    -   `GOOGLE_CREDENTIALS_PATH` : Le chemin absolu vers votre fichier de credentials JSON de Google (pour le compte de service).
    -   `GOOGLE_SPREADSHEET_ID` : L'ID de votre Google Sheet.
    -   `SYNC_TIME` (optionnel) : L'heure de la synchronisation quotidienne (ex: `09:00`).

3.  **Assurez-vous que votre compte de service Google** a les permissions "Éditeur" sur votre Google Sheet.

## Utilisation

Le script principal `main.py` peut être exécuté de plusieurs manières.

### Exécuter une synchronisation unique

Pour lancer une synchronisation manuelle immédiate :

```bash
./main.py --mode once
```

### Lancer le planificateur quotidien

Pour démarrer le service en mode planificateur, qui effectuera une synchronisation chaque jour à l'heure définie dans `.env` :

```bash
./main.py --mode scheduler
```

Le service effectuera une première synchronisation au démarrage, puis attendra l'heure planifiée.

### Tester les connexions

Pour vérifier que vos clés d'API et vos configurations sont correctes sans effectuer de synchronisation complète :

```bash
./main.py --test-connection
```

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` for plus de détails.


