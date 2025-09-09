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




## Configuration de Google Sheets API

### 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API Google Sheets pour votre projet

### 2. Créer un compte de service

1. Dans la console Google Cloud, allez dans "IAM et administration" > "Comptes de service"
2. Cliquez sur "Créer un compte de service"
3. Donnez un nom à votre compte de service
4. Cliquez sur "Créer et continuer"
5. Attribuez le rôle "Éditeur" (ou un rôle personnalisé avec les permissions nécessaires)
6. Cliquez sur "Continuer" puis "Terminé"

### 3. Générer une clé JSON

1. Cliquez sur le compte de service que vous venez de créer
2. Allez dans l'onglet "Clés"
3. Cliquez sur "Ajouter une clé" > "Créer une nouvelle clé"
4. Sélectionnez "JSON" et cliquez sur "Créer"
5. Le fichier JSON sera téléchargé automatiquement

### 4. Partager votre Google Sheet

1. Ouvrez votre Google Sheet
2. Cliquez sur "Partager" en haut à droite
3. Ajoutez l'adresse email de votre compte de service (visible dans le fichier JSON sous `client_email`)
4. Donnez les permissions "Éditeur"

### 5. Obtenir l'ID du Google Sheet

L'ID du Google Sheet se trouve dans l'URL :
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
```

## Configuration de l'API Wedof

1. Connectez-vous à votre compte Wedof
2. Allez dans "Mon compte" > "Jetons d'API"
3. Copiez votre jeton d'API existant ou créez-en un nouveau
4. Utilisez ce jeton comme valeur pour `WEDOF_API_KEY` dans votre fichier `.env`

## Données synchronisées

Le script synchronise les données suivantes depuis Wedof :

- **Users** : Utilisateurs du système
- **Trainings** : Formations disponibles
- **Sessions** : Sessions de formation
- **Attendees** : Participants aux formations
- **Registration Folders** : Dossiers d'inscription
- **Certification Folders** : Dossiers de certification
- **Organisms** : Organismes de formation
- **Activities** : Activités de formation
- **Evaluations** : Évaluations des formations
- **Invoices** : Factures
- **Payments** : Paiements

Chaque type de données est placé dans une feuille séparée du Google Sheet avec un formatage automatique des en-têtes.

## Planification avec cron (Linux/macOS)

Pour automatiser l'exécution quotidienne sur un serveur, vous pouvez utiliser cron :

```bash
# Éditer la crontab
crontab -e

# Ajouter une ligne pour exécuter le script chaque jour à 9h00
0 9 * * * cd /chemin/vers/wedof-sync-google-sheets && ./main.py --mode once
```

## Dépannage

### Erreur d'authentification Wedof
- Vérifiez que votre clé API est correcte
- Assurez-vous que votre compte a les permissions nécessaires

### Erreur d'authentification Google Sheets
- Vérifiez que le fichier de credentials JSON est correct
- Assurez-vous que le compte de service a accès au Google Sheet
- Vérifiez que l'API Google Sheets est activée dans votre projet

### Erreur de rate limiting
- Le script respecte automatiquement les limites de taux de l'API Wedof
- Si vous rencontrez des erreurs, vérifiez votre type d'abonnement Wedof

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

