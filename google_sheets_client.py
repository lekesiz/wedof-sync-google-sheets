"""
Client pour Google Sheets API
"""
import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
import os
import json

logger = logging.getLogger(__name__)

class GoogleSheetsClient:
    """Client pour interagir avec Google Sheets API"""
    
    # Scopes nécessaires pour Google Sheets
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """
        Initialise le client Google Sheets
        
        Args:
            credentials_path: Chemin vers le fichier de credentials JSON
            spreadsheet_id: ID du Google Sheet à utiliser
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authentification avec Google Sheets API"""
        creds = None
        
        # Vérifier si c'est un fichier de service account
        try:
            with open(self.credentials_path, 'r') as f:
                cred_data = json.load(f)
                
            if 'type' in cred_data and cred_data['type'] == 'service_account':
                # Utiliser les credentials de service account
                creds = ServiceAccountCredentials.from_service_account_file(
                    self.credentials_path, scopes=self.SCOPES
                )
                logger.info("Authentification avec service account")
            else:
                # Utiliser OAuth2 flow pour les credentials utilisateur
                token_path = 'token.json'
                
                if os.path.exists(token_path):
                    creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, self.SCOPES
                        )
                        creds = flow.run_local_server(port=0)
                    
                    # Sauvegarder les credentials pour la prochaine fois
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
                
                logger.info("Authentification OAuth2 réussie")
                
        except Exception as e:
            logger.error(f"Erreur d'authentification: {e}")
            raise
        
        self.service = build('sheets', 'v4', credentials=creds)
    
    def create_sheet_if_not_exists(self, sheet_name: str) -> bool:
        """
        Crée une feuille si elle n'existe pas
        
        Args:
            sheet_name: Nom de la feuille à créer
            
        Returns:
            True si la feuille a été créée, False si elle existait déjà
        """
        try:
            # Obtenir la liste des feuilles existantes
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            existing_sheets = [sheet['properties']['title'] 
                             for sheet in spreadsheet['sheets']]
            
            if sheet_name in existing_sheets:
                logger.info(f"La feuille '{sheet_name}' existe déjà")
                return False
            
            # Créer la nouvelle feuille
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            logger.info(f"Feuille '{sheet_name}' créée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la feuille '{sheet_name}': {e}")
            raise
    
    def clear_sheet(self, sheet_name: str):
        """
        Vide le contenu d'une feuille
        
        Args:
            sheet_name: Nom de la feuille à vider
        """
        try:
            range_name = f"{sheet_name}!A:ZZ"
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            logger.info(f"Feuille '{sheet_name}' vidée")
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage de la feuille '{sheet_name}': {e}")
            raise
    
    def write_data_to_sheet(self, sheet_name: str, data: List[Dict[str, Any]], 
                           clear_first: bool = True):
        """
        Écrit des données dans une feuille Google Sheets
        
        Args:
            sheet_name: Nom de la feuille
            data: Liste de dictionnaires contenant les données
            clear_first: Si True, vide la feuille avant d'écrire
        """
        if not data:
            logger.warning(f"Aucune donnée à écrire dans '{sheet_name}'")
            return
        
        try:
            # Créer la feuille si elle n'existe pas
            self.create_sheet_if_not_exists(sheet_name)
            
            # Vider la feuille si demandé
            if clear_first:
                self.clear_sheet(sheet_name)
            
            # Convertir les données en DataFrame pour faciliter la manipulation
            df = pd.DataFrame(data)
            
            # Préparer les données pour Google Sheets
            # En-têtes
            headers = [list(df.columns)]
            
            # Données (convertir tout en string pour éviter les erreurs de type)
            values = []
            for _, row in df.iterrows():
                row_values = []
                for value in row:
                    if pd.isna(value):
                        row_values.append('')
                    elif isinstance(value, (dict, list)):
                        row_values.append(str(value))
                    else:
                        row_values.append(str(value))
                values.append(row_values)
            
            # Combiner en-têtes et données
            all_values = headers + values
            
            # Écrire dans Google Sheets
            range_name = f"{sheet_name}!A1"
            body = {
                'values': all_values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            rows_updated = result.get('updatedRows', 0)
            logger.info(f"✓ {rows_updated} lignes écrites dans '{sheet_name}'")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture dans '{sheet_name}': {e}")
            raise
    
    def format_sheet_headers(self, sheet_name: str):
        """
        Formate les en-têtes d'une feuille (gras, couleur de fond)
        
        Args:
            sheet_name: Nom de la feuille à formater
        """
        try:
            # Obtenir l'ID de la feuille
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheet_id = None
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                logger.warning(f"Feuille '{sheet_name}' non trouvée pour le formatage")
                return
            
            # Formater la première ligne (en-têtes)
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {
                                'bold': True
                            },
                            'backgroundColor': {
                                'red': 0.9,
                                'green': 0.9,
                                'blue': 0.9
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            }]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            logger.info(f"En-têtes formatés pour '{sheet_name}'")
            
        except Exception as e:
            logger.error(f"Erreur lors du formatage de '{sheet_name}': {e}")
    
    def sync_wedof_data(self, wedof_data: Dict[str, List[Dict[str, Any]]]):
        """
        Synchronise toutes les données Wedof avec Google Sheets
        
        Args:
            wedof_data: Dictionnaire contenant toutes les données Wedof
        """
        logger.info("Début de la synchronisation avec Google Sheets")
        
        for data_type, data_list in wedof_data.items():
            try:
                sheet_name = data_type.replace('_', ' ').title()
                logger.info(f"Synchronisation de {len(data_list)} éléments vers '{sheet_name}'")
                
                if data_list:
                    self.write_data_to_sheet(sheet_name, data_list)
                    self.format_sheet_headers(sheet_name)
                else:
                    logger.warning(f"Aucune donnée pour '{sheet_name}'")
                    
            except Exception as e:
                logger.error(f"Erreur lors de la synchronisation de '{data_type}': {e}")
                continue
        
        logger.info("Synchronisation terminée")
    
    def get_spreadsheet_url(self) -> str:
        """
        Retourne l'URL du Google Sheet
        
        Returns:
            URL du Google Sheet
        """
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit"

