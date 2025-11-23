from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from db import get_db_connection
import json

router = APIRouter()

@router.get("/")
def retrieve_all(tags: Optional[List[str]] = Query(default=None), order: str = "desc"):
    """
    Return full records, optionally filtered by tags, ordered by uploaded_at.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM call_analyses"
        params = []

        # Filter by tags
        if tags:
            query += " WHERE " + " AND ".join(["tags LIKE ?" for _ in tags])
            params.extend([f'%"{t}"%' for t in tags])

        # Sort
        if order.lower() not in ("asc", "desc"):
            order = "desc"

        query += f" ORDER BY uploaded_at {order.upper()}"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            item = dict(r)

            raw_tags = item.get("tags")
            try:
                item["tags"] = json.loads(raw_tags) if raw_tags else []
            except Exception:
                item["tags"] = []
            results.append(item)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


@router.get("/{record_id}")
def retrieve_one(record_id: int):
    """
    Return full single record in a JSON.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM call_analyses WHERE id = ?", (record_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Record not found")

        result = dict(row)
        raw_tags = result.get("tags")
        try:
            result["tags"] = json.loads(raw_tags) if raw_tags else []
        except:
            result["tags"] = []
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
