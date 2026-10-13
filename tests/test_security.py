def test_authentication_and_role_boundaries(client, tokens):
    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/analyses").status_code == 401
    assert client.get("/api/v1/analyses", headers={"Authorization": "Bearer no"}).status_code == 401
    body = {
        "name": "edge change",
        "before": {"nodes": ["a", "b"], "links": [{"source": "a", "target": "b"}]},
        "after": {"nodes": ["a", "b"], "links": []},
        "intents": [{"name": "must reach", "source": "a", "destination": "b"}],
    }
    assert client.post("/api/v1/analyses", headers=tokens["viewer"], json=body).status_code == 403
    assert client.post("/api/v1/analyses", headers=tokens["analyst"], json=body).status_code == 201
    assert client.get("/api/v1/analyses", headers=tokens["viewer"]).status_code == 200


def test_analysis_route_is_not_public(client):
    assert client.get("/api/v1/analyses/nope").status_code == 401
