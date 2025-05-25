from typing import Dict, Type, Any
from functools import lru_cache
import logging

from ..services.anthropic_service import AnthropicService
from ..services.validation_service import ValidationService
from ..services.template_service import TemplateService
from ..services.mongodb_service import MongoDBService
from ..services.ocr_service import OCRService


class ServiceContainer:
    """
    Service container for managing application dependencies and their lifecycle.
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False
        logging.info("Service container initialized")

    def initialize_services(self):
        """
        Initialize all services in the container.
        This should be called during application startup.
        """
        if self._initialized:
            return
            
        try:
            logging.info("Initializing application services...")
            
            # Initialize services in order of dependencies
            self._services['template'] = TemplateService()
            self._services['validation'] = ValidationService()
            self._services['anthropic'] = AnthropicService()
            self._services['mongodb'] = MongoDBService()
            self._services['ocr'] = OCRService()
            
            self._initialized = True
            logging.info("All services initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize services: {str(e)}")
            raise

    def get_service(self, service_name: str) -> Any:
        """
        Get a service instance by name.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service is not found
            RuntimeError: If services are not initialized
        """
        if not self._initialized:
            raise RuntimeError("Services not initialized. Call initialize_services() first.")
            
        if service_name not in self._services:
            raise KeyError(f"Service '{service_name}' not found")
            
        return self._services[service_name]

    def get_anthropic_service(self) -> AnthropicService:
        """Get the Anthropic service instance."""
        return self.get_service('anthropic')

    def get_validation_service(self) -> ValidationService:
        """Get the Validation service instance."""
        return self.get_service('validation')

    def get_template_service(self) -> TemplateService:
        """Get the Template service instance."""
        return self.get_service('template')

    def get_mongodb_service(self) -> MongoDBService:
        """Get the MongoDB service instance."""
        return self.get_service('mongodb')

    def get_ocr_service(self) -> OCRService:
        """Get the OCR service instance."""
        return self.get_service('ocr')

    def shutdown_services(self):
        """
        Shutdown all services and cleanup resources.
        This should be called during application shutdown.
        """
        logging.info("Shutting down services...")
        
        # Cleanup services that need explicit shutdown
        for service_name, service in self._services.items():
            try:
                if hasattr(service, 'shutdown'):
                    service.shutdown()
                    logging.info(f"Service '{service_name}' shut down successfully")
            except Exception as e:
                logging.error(f"Error shutting down service '{service_name}': {str(e)}")
        
        self._services.clear()
        self._initialized = False
        logging.info("All services shut down")


# Global service container instance
_service_container: ServiceContainer = ServiceContainer()


@lru_cache()
def get_service_container() -> ServiceContainer:
    """
    Get the global service container instance.
    
    Returns:
        ServiceContainer instance
    """
    return _service_container


# Convenience functions for getting specific services
def get_anthropic_service() -> AnthropicService:
    """Get Anthropic service instance."""
    return get_service_container().get_anthropic_service()


def get_validation_service() -> ValidationService:
    """Get Validation service instance."""
    return get_service_container().get_validation_service()


def get_template_service() -> TemplateService:
    """Get Template service instance."""
    return get_service_container().get_template_service()


def get_mongodb_service() -> MongoDBService:
    """Get MongoDB service instance."""
    return get_service_container().get_mongodb_service()


def get_ocr_service() -> OCRService:
    """Get OCR service instance."""
    return get_service_container().get_ocr_service()


def initialize_services():
    """Initialize all application services."""
    get_service_container().initialize_services()


def shutdown_services():
    """Shutdown all application services."""
    get_service_container().shutdown_services() 