def test_rota_raiz_responde(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_rotas_existentes_registradas(client):
    resp = client.get('/api/safras')
    assert resp.status_code == 200
