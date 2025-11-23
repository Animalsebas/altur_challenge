from fastapi.testclient import TestClient
from back.main import app
from back.db import get_db_connection, initialize_db, DB_NAME
import json
import os

client = TestClient(app)

def test_retrieve_single():
    # Insert record using the SAME DB methods as the app
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO call_analyses (file_name, full_transcript, tags)
        VALUES (?, ?, ?)
    """, ("test.wav", "test transcript", json.dumps(["ExampleTag"])))

    conn.commit()
    last_id = cursor.execute("SELECT MAX(id) FROM call_analyses").fetchone()[0]
    conn.close()

    # Call API endpoint
    r = client.get(f"/api/retrieve/{last_id}")

    assert r.status_code == 200

    data = r.json()
    assert data["id"] == last_id
    assert data["full_transcript"] == "test transcript"
    assert data["tags"] == ["ExampleTag"]

    # Clean up
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM call_analyses WHERE id = ?", (last_id,))
    conn.commit()
