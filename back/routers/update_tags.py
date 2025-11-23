from fastapi import APIRouter, HTTPException, Request
from back.db import get_db_connection
import json

router = APIRouter()

@router.post("/updateTags")
async def update_tags(request: Request):
    """
    Update the tags for a given record.
    """
    conn = None
    try:
        body = await request.json()
        record_id = body.get("id")
        tags = body.get("tags")

        if not isinstance(record_id, int):
            raise HTTPException(status_code=400, detail="Missing or invalid 'id'")
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise HTTPException(status_code=400, detail="Missing or invalid 'tags'")

        tags_json = json.dumps(tags)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE call_analyses SET tags = ? WHERE id = ?",
            (tags_json, record_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Record not found")

        return {"success": True, "id": record_id, "tags": tags}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()