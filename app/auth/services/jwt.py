from app.auth.schemas.jwt import RefreshTokenSchema
from core.exceptions.token import DecodeTokenException
from core.utils.token_helper import TokenHelper


class JwtService:
    @staticmethod
    async def verify_token(token: str) -> None:
        TokenHelper.decode(token=token)

    @staticmethod
    async def create_refresh_token(
        token: str,
        refresh_token: str,
    ) -> RefreshTokenSchema:
        token = TokenHelper.decode(token=token)
        refresh_token = TokenHelper.decode(token=refresh_token)
        if refresh_token.get("sub") != "refresh":
            raise DecodeTokenException

        return RefreshTokenSchema(
            token=TokenHelper.encode(payload={"user_id": token.get("user_id")}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
