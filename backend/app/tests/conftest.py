import pytest

from testcontainers.mongodb import MongoDbContainer

from app.core.config import settings
from app.core.dependencies import ServiceContainer, get_mongodb_service


@pytest.fixture(scope="session")
def mongodb_container():
    """Create a MongoDB container for testing."""
    container = MongoDbContainer("mongo:latest")
    container.start()
    
    # Override the MongoDB connection string for testing
    settings.MONGODB_URL = container.get_connection_url()
    
    yield container
    
    container.stop()

@pytest.fixture(scope="function")
def service_container(mongodb_container):
    """Create a fresh service container for each test."""
    container = ServiceContainer()
    container.initialize_services()
    return container 