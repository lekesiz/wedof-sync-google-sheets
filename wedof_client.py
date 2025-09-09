"""
Client pour l'API Wedof
"""
import requests
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class WedofClient:
    """Client pour interagir avec l'API Wedof"""
    
    def __init__(self, api_key: str, base_url: str = "https://www.wedof.fr"):
        """
        Initialise le client Wedof
        
        Args:
            api_key: Clé API Wedof
            base_url: URL de base de l'API Wedof
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'X-Api-Key': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Gestion du rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.6  # 100 req/min = 0.6s entre les requêtes
        
    def _wait_for_rate_limit(self):
        """Attendre pour respecter les limites de taux"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Effectue une requête HTTP avec gestion des erreurs et rate limiting
        
        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint de l'API (ex: '/api/users')
            **kwargs: Arguments supplémentaires pour requests
            
        Returns:
            Réponse JSON de l'API
        """
        self._wait_for_rate_limit()
        
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Vérifier les headers de rate limiting
            if 'X-RateLimit-Remaining' in response.headers:
                remaining = int(response.headers['X-RateLimit-Remaining'])
                if remaining < 5:
                    logger.warning(f"Rate limit proche: {remaining} requêtes restantes")
                    
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP {response.status_code}: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de requête: {e}")
            raise
    
    def get_paginated_data(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Récupère toutes les données paginées d'un endpoint
        
        Args:
            endpoint: Endpoint de l'API
            params: Paramètres de requête optionnels
            
        Returns:
            Liste de tous les éléments
        """
        all_data = []
        page = 1
        params = params or {}
        
        while True:
            params['page'] = page
            params['limit'] = 100  # Maximum par page
            
            logger.info(f"Récupération page {page} de {endpoint}")
            response = self._make_request('GET', endpoint, params=params)
            
            # Les données peuvent être directement dans la réponse ou dans un champ spécifique
            if isinstance(response, list):
                data = response
            elif 'data' in response:
                data = response['data']
            else:
                data = response
                
            if not data:
                break
                
            all_data.extend(data if isinstance(data, list) else [data])
            
            # Vérifier s'il y a d'autres pages
            if len(data) < params['limit']:
                break
                
            page += 1
            
        logger.info(f"Total récupéré: {len(all_data)} éléments de {endpoint}")
        return all_data
    
    # Méthodes spécifiques pour chaque endpoint
    def get_users(self) -> List[Dict[str, Any]]:
        """Récupère tous les utilisateurs"""
        return self.get_paginated_data('/api/users')
    
    def get_trainings(self) -> List[Dict[str, Any]]:
        """Récupère toutes les formations"""
        return self.get_paginated_data('/api/trainings')
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """Récupère toutes les sessions"""
        return self.get_paginated_data('/api/sessions')
    
    def get_attendees(self) -> List[Dict[str, Any]]:
        """Récupère tous les participants"""
        return self.get_paginated_data('/api/attendees')
    
    def get_registration_folders(self) -> List[Dict[str, Any]]:
        """Récupère tous les dossiers d'inscription"""
        return self.get_paginated_data('/api/registrationFolders')
    
    def get_certification_folders(self) -> List[Dict[str, Any]]:
        """Récupère tous les dossiers de certification"""
        return self.get_paginated_data('/api/certificationFolders')
    
    def get_organisms(self) -> List[Dict[str, Any]]:
        """Récupère tous les organismes"""
        return self.get_paginated_data('/api/organisms')
    
    def get_activities(self) -> List[Dict[str, Any]]:
        """Récupère toutes les activités"""
        return self.get_paginated_data('/api/activities')
    
    def get_evaluations(self) -> List[Dict[str, Any]]:
        """Récupère toutes les évaluations"""
        return self.get_paginated_data('/api/evaluations')
    
    def get_invoices(self) -> List[Dict[str, Any]]:
        """Récupère toutes les factures"""
        return self.get_paginated_data('/api/invoices')
    
    def get_payments(self) -> List[Dict[str, Any]]:
        """Récupère tous les paiements"""
        return self.get_paginated_data('/api/payments')
    
    def get_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère toutes les données de tous les endpoints
        
        Returns:
            Dictionnaire avec toutes les données organisées par type
        """
        logger.info("Début de la récupération de toutes les données Wedof")
        
        all_data = {}
        
        endpoints = [
            ('users', self.get_users),
            ('trainings', self.get_trainings),
            ('sessions', self.get_sessions),
            ('attendees', self.get_attendees),
            ('registration_folders', self.get_registration_folders),
            ('certification_folders', self.get_certification_folders),
            ('organisms', self.get_organisms),
            ('activities', self.get_activities),
            ('evaluations', self.get_evaluations),
            ('invoices', self.get_invoices),
            ('payments', self.get_payments)
        ]
        
        for name, method in endpoints:
            try:
                logger.info(f"Récupération des {name}...")
                all_data[name] = method()
                logger.info(f"✓ {name}: {len(all_data[name])} éléments")
            except Exception as e:
                logger.error(f"✗ Erreur lors de la récupération des {name}: {e}")
                all_data[name] = []
        
        logger.info("Récupération terminée")
        return all_data

