#!/usr/bin/env python3
"""
Script principal pour la synchronisation Wedof -> Google Sheets
"""
import os
import sys
import logging
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
import argparse

from wedof_client import WedofClient
from google_sheets_client import GoogleSheetsClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wedof_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class WedofSyncService:
    """Service de synchronisation Wedof -> Google Sheets"""
    
    def __init__(self):
        """Initialise le service de synchronisation"""
        # Charger les variables d'environnement
        load_dotenv()
        
        # Vérifier les variables d'environnement requises
        required_vars = [
            'WEDOF_API_KEY',
            'GOOGLE_CREDENTIALS_PATH',
            'GOOGLE_SPREADSHEET_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Variables d'environnement manquantes: {', '.join(missing_vars)}")
        
        # Initialiser les clients
        self.wedof_client = WedofClient(
            api_key=os.getenv('WEDOF_API_KEY'),
            base_url=os.getenv('WEDOF_BASE_URL', 'https://www.wedof.fr')
        )
        
        self.sheets_client = GoogleSheetsClient(
            credentials_path=os.getenv('GOOGLE_CREDENTIALS_PATH'),
            spreadsheet_id=os.getenv('GOOGLE_SPREADSHEET_ID')
        )
        
        logger.info("Service de synchronisation initialisé")
    
    def sync_data(self):
        """Effectue une synchronisation complète"""
        try:
            logger.info("=" * 50)
            logger.info("DÉBUT DE LA SYNCHRONISATION")
            logger.info(f"Timestamp: {datetime.now().isoformat()}")
            logger.info("=" * 50)
            
            # Récupérer toutes les données de Wedof
            logger.info("Récupération des données Wedof...")
            wedof_data = self.wedof_client.get_all_data()
            
            # Calculer le total d'éléments
            total_items = sum(len(data_list) for data_list in wedof_data.values())
            logger.info(f"Total d'éléments récupérés: {total_items}")
            
            # Synchroniser avec Google Sheets
            logger.info("Synchronisation avec Google Sheets...")
            self.sheets_client.sync_wedof_data(wedof_data)
            
            # Afficher l'URL du Google Sheet
            sheet_url = self.sheets_client.get_spreadsheet_url()
            logger.info(f"Google Sheet disponible à: {sheet_url}")
            
            logger.info("=" * 50)
            logger.info("SYNCHRONISATION TERMINÉE AVEC SUCCÈS")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {e}")
            logger.error("=" * 50)
            logger.error("SYNCHRONISATION ÉCHOUÉE")
            logger.error("=" * 50)
            raise
    
    def run_once(self):
        """Exécute une synchronisation unique"""
        logger.info("Exécution d'une synchronisation unique")
        self.sync_data()
    
    def run_scheduler(self):
        """Lance le planificateur pour les synchronisations quotidiennes"""
        # Planifier la synchronisation quotidienne
        sync_time = os.getenv('SYNC_TIME', '09:00')
        schedule.every().day.at(sync_time).do(self.sync_data)
        
        logger.info(f"Planificateur démarré - Synchronisation quotidienne à {sync_time}")
        logger.info("Appuyez sur Ctrl+C pour arrêter")
        
        # Exécuter une première synchronisation immédiatement
        logger.info("Exécution de la première synchronisation...")
        try:
            self.sync_data()
        except Exception as e:
            logger.error(f"Erreur lors de la première synchronisation: {e}")
        
        # Boucle principale du planificateur
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Vérifier toutes les minutes
                
        except KeyboardInterrupt:
            logger.info("Arrêt du planificateur demandé")
        except Exception as e:
            logger.error(f"Erreur dans le planificateur: {e}")
            raise

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Synchronisation Wedof -> Google Sheets'
    )
    parser.add_argument(
        '--mode',
        choices=['once', 'scheduler'],
        default='once',
        help='Mode d\'exécution: once (une fois) ou scheduler (planificateur quotidien)'
    )
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Teste uniquement les connexions aux APIs'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialiser le service
        service = WedofSyncService()
        
        if args.test_connection:
            logger.info("Test des connexions...")
            
            # Test Wedof
            try:
                users = service.wedof_client.get_users()
                logger.info(f"✓ Connexion Wedof OK - {len(users)} utilisateurs trouvés")
            except Exception as e:
                logger.error(f"✗ Connexion Wedof échouée: {e}")
                return 1
            
            # Test Google Sheets
            try:
                sheet_url = service.sheets_client.get_spreadsheet_url()
                logger.info(f"✓ Connexion Google Sheets OK - {sheet_url}")
            except Exception as e:
                logger.error(f"✗ Connexion Google Sheets échouée: {e}")
                return 1
            
            logger.info("Tous les tests de connexion ont réussi!")
            return 0
        
        # Exécuter selon le mode choisi
        if args.mode == 'once':
            service.run_once()
        elif args.mode == 'scheduler':
            service.run_scheduler()
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

