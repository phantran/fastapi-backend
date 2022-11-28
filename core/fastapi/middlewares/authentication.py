from typing import Optional, Tuple

import jwt
from fastapi import HTTPException
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection
from starlette.status import HTTP_401_UNAUTHORIZED

from core.config import config

from ...cache.redis import is_revoked_token
from ..schemas import CurrentUser


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    pass


class AuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> Tuple[bool, Optional[CurrentUser]]:
        current_user = CurrentUser()
        authorization: str = conn.headers.get("Authorization")
        if not authorization:
            return False, current_user

        try:
            scheme, credentials = authorization.split(" ")
            if scheme.lower() != "bearer":
                return False, current_user
        except ValueError:
            return False, current_user

        if not credentials:
            return False, current_user

        if await is_revoked_token(credentials):
            return False, current_user

        try:
            payload = jwt.decode(
                credentials,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM],
            )
            user_id = payload.get("user_id")
        except jwt.exceptions.PyJWTError:
            return False, current_user

        current_user.id = user_id
        return credentials, current_user
