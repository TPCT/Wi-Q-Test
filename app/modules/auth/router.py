from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, status

from app.modules.auth.dependencies import AuthServiceDep
from app.modules.auth.models import AccessToken
from app.modules.auth.service import InvalidClientCredentialsError

router = APIRouter(tags=["auth"])


@router.post("/auth_token")
async def create_auth_token(
    client_secret: Annotated[str, Form()],
    client_id: Annotated[str, Form()],
    grant_type: Annotated[str, Form()],
    auth_service: AuthServiceDep,
) -> AccessToken:
    try:
        access_token = await auth_service.create_access_token(
            client_id=client_id,
            client_secret=client_secret,
            grant_type=grant_type,
        )
    except InvalidClientCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        ) from error

    return access_token
