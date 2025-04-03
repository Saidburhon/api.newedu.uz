import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class TokenPayload(BaseModel):
    token: str


@router.post("/decode")
async def test_decode_token(payload: TokenPayload):
    """Debug endpoint to test JWT decoding"""
    try:
        # Log token info
        print(f"Received token: {payload.token[:20]}...")
        print(f"Secret key being used: {settings.SECRET_KEY[:10]}...")
        
        # First try without verification to see what's inside
        try:
            decoded_content = jwt.decode(
                payload.token, 
                options={"verify_signature": False}
            )
            print(f"Token payload (unverified): {decoded_content}")
        except Exception as e:
            print(f"Cannot decode token content: {str(e)}")
            return {"error": "Malformed token", "details": str(e)}
        
        # Now try with verification
        try:
            verified_payload = jwt.decode(
                payload.token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return {
                "success": True,
                "message": "Token decoded successfully",
                "payload": verified_payload,
                "secret_used": settings.SECRET_KEY[:5] + "..." # Show first few chars for debugging
            }
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}
        except jwt.InvalidSignatureError:
            return {
                "error": "Invalid signature", 
                "token_header": decoded_content,
                "secret_used": settings.SECRET_KEY[:5] + "..."
            }
        except Exception as e:
            return {"error": "Verification error", "details": str(e)}
            
    except Exception as e:
        return {"error": "General error", "details": str(e)}


@router.post("/encode")
async def test_encode_token(payload: dict):
    """Debug endpoint to test JWT encoding"""
    try:
        # Encode a token with the same settings used in the real app
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return {
            "success": True,
            "token": token,
            "secret_used": settings.SECRET_KEY[:5] + "..."
        }
    except Exception as e:
        return {"error": "Encoding error", "details": str(e)}
