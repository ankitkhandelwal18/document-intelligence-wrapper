# document_intelligence_wrapper/document_intelligence_client.py

import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

class DocumentIntelligenceClientWrapper:
    """
    A wrapper for the Azure Document Intelligence Client.
    
    Attributes:
        endpoint (str): The endpoint for the Azure Document Intelligence API.
        key (str): The key for the Azure Document Intelligence API.
    """
    def __init__(self, endpoint: str, key: str):
        self.client = None
        self.endpoint = endpoint
        self.key = key
        self.initialize_document_intelligence_client()

    def initialize_document_intelligence_client(self):
        """
        Initialize the Document Intelligence Client with the given endpoint and key.
        """
        try:
            self.client = DocumentIntelligenceClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.key)
            )
        except Exception as e:
            logging.error("Exception while initializing DocumentIntelligenceClient: %s", e)
            raise

    def get_document_intelligence_client(self):
        """
        Returns the initialized Document Intelligence Client.
        """
        return self.client
