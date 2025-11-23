from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_retrieve_list_ordering():
    r = client.get("/api/retrieve?order=desc&limit=1")
    assert r.status_code == 200

    records = r.json()
    assert isinstance(records, list)
    assert len(records) >= 1
