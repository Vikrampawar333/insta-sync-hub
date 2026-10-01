import json
from fastapi import APIRouter, Request, Response, HTTPException, status
from app.config import settings
from app.instagram_service import instagram_service

router = APIRouter(prefix="/api/webhook", tags=["Webhook"])

# Global event listeners queue for SSE real-time broadcast
event_listeners = []

def broadcast_event(event_type: str, data: dict):
    """Pushes real-time events to all active connected browsers via SSE."""
    payload = json.dumps({"event": event_type, "data": data})
    for queue in event_listeners:
        try:
            queue.put_nowait(payload)
        except Exception:
            pass

@router.get("")
async def verify_webhook(request: Request):
    """
    Meta Webhook Verification (Handshake).
    Meta calls this GET request when you register the webhook in the Developer Portal.
    100% compliant with official Meta requirements.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.META_VERIFY_TOKEN:
        print("[Webhook] Meta handshake verified successfully!")
        return Response(content=challenge, media_type="text/plain")
        
    print(f"[Webhook Error] Verification token mismatch. Received: {token}, Expected: {settings.META_VERIFY_TOKEN}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")

@router.post("")
async def receive_webhook_event(request: Request):
    """
    Meta Webhook Event Handler.
    Called by Meta when a new Instagram post, reel, or comment is published.
    """
    try:
        payload = await request.json()
        print("[Webhook Event Received]:", json.dumps(payload, indent=2))
        
        # Meta event structure
        obj = payload.get("object")
        entries = payload.get("entry", [])
        
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                field = change.get("field")
                value = change.get("value", {})
                
                # If new media / post / reel is uploaded
                if field == "media":
                    media_id = value.get("media_id")
                    print(f"[Webhook] New Instagram Media Detected: {media_id}")
                    # Trigger async sync to cache post locally
                    await instagram_service.sync_media_from_instagram()
                    broadcast_event("new_post", {"media_id": media_id})
                    
                # If new comment is posted
                elif field == "comments":
                    comment_id = value.get("id")
                    text = value.get("text")
                    print(f"[Webhook] New Instagram Comment: {comment_id} - '{text}'")
                    broadcast_event("new_comment", value)
                    
        return {"status": "success", "message": "Event processed"}
    except Exception as e:
        print(f"[Webhook Error]: {e}")
        # Always return 200 so Meta does not keep retrying and suspend the webhook
        return {"status": "error", "message": str(e)}
