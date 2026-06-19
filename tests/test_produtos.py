import pytest

# 1. Listar produtos quando o banco está vazio
def test_listar_produtos_banco_vazio(client):
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []

# 2. Criar produto e verificar persistência no banco
def test_criar_produto_persistência(client):
    payload = {"nome": "Teclado Mecânico", "preco": 250.00, "estoque": 5}
    response = client.post("/produtos", json=payload)
    assert response.status_code == 201
    assert response.json()["id"] is not None

# 3. Criar produto e verificar que aparece na listagem
def test_criar_produto_aparece_na_listagem(client):
    payload = {"nome": "Mouse Gamer", "preco": 120.00}
    client.post("/produtos", json=payload)
    response = client.get("/produtos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nome"] == "Mouse Gamer"

# 4. Buscar produto por id — caso de sucesso
def test_buscar_produto_por_id_sucesso(client, produto_existente):
    p_id = produto_existente["id"]
    response = client.get(f"/produtos/{p_id}")
    assert response.status_code == 200
    assert response.json()["nome"] == "Produto Base"

# 5. Buscar produto com id inexistente — deve retornar 404
def test_buscar_produto_id_inexistente(client):
    response = client.get("/produtos/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"

# 6. Deletar produto — deve retornar 204
def test_deletar_produto_sucesso(client, produto_existente):
    p_id = produto_existente["id"]
    response = client.delete(f"/produtos/{p_id}")
    assert response.status_code == 204

# 7. Deletar produto e confirmar remoção com GET subsequente
def test_deletar_produto_confirmar_remocao(client, produto_existente):
    p_id = produto_existente["id"]
    client.delete(f"/produtos/{p_id}")
    response = client.get(f"/produtos/{p_id}")
    assert response.status_code == 404

# 8. Deletar produto inexistente — deve retornar 404
def test_deletar_produto_inexistente(client):
    response = client.delete("/produtos/88888")
    assert response.status_code == 404

# 9. Teste parametrizado cobrindo payloads inválidos (status 422)
@pytest.mark.parametrize("payload_invalido", [
    {"nome": "   ", "preco": 10.0},
    {"nome": "", "preco": 10.0},
    {"nome": "Erro", "preco": 0.0},
    {"nome": "Erro", "preco": -5.0},
    {"preco": 10.0}
])
def test_criar_produto_payloads_invalidos(client, payload_invalido):
    response = client.post("/produtos", json=payload_invalido)
    assert response.status_code == 422

# 10. Validar que o banco está isolado entre execuções
def test_validar_isolamento_do_banco(client, produto_existente):
    response = client.get("/produtos")
    assert len(response.json()) == 1
