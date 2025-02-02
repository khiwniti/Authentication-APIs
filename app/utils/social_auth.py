from typing import Dict, Optional
import httpx
from fastapi import HTTPException, status

async def verify_google_token(token: str) -> Optional[Dict]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to verify Google token"
            )

async def verify_facebook_token(token: str) -> Optional[Dict]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://graph.facebook.com/me?access_token={token}"
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to verify Facebook token"
            ) 