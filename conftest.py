import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuração da variável de ambiente exclusiva de teste
TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5433/ecommerce_test_db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from main import app, Base, get_db

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def client():
    """
    (a) Cria as tabelas via metadata.create_all
    (b) Substitui get_db via dependency_overrides
    (c) Realiza o yield do TestClient
    (d) Executa o drop_all no teardown da fixture
    """
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def produto_existente(client):
    """Cria previamente um produto usando a rota do cliente de teste."""
    payload = {"nome": "Produto Base", "preco": 49.90, "estoque": 10, "ativo": True}
    response = client.post("/produtos", json=payload)
    return response.json()
