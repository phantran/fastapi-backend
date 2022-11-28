from typing import Optional

from pydantic import BaseModel, Field, validator

from core.config import config


class CreateUserRequestSchema(BaseModel):
    username: str = Field(..., description="Username", min_length=5, max_length=100)
    password1: str = Field(..., description="Password1", min_length=5, max_length=255)
    password2: str = Field(..., description="Password2", min_length=5, max_length=255)
    role: str = Field(..., description="Role")
    deposit: Optional[int] = Field(None, description="Deposit")

    @validator("username")
    def username_alphanumeric(cls, v):
        assert v.isalnum(), "must be alphanumeric"
        return v

    @validator("role")
    def supported_role(cls, v):
        if v not in config.SUPPORTED_ROLES:
            raise ValueError("unsupported role")
        return v


class CreateUserResponseSchema(BaseModel):
    username: str = Field(..., description="Username")
    role: str = Field(..., description="Role")

    class Config:
        orm_mode = True


class UpdatePasswordSchema(BaseModel):
    password1: str = Field(..., description="Password1", min_length=5, max_length=255)
    password2: str = Field(..., description="Password2", min_length=5, max_length=255)
    old_password: str = Field(
        ..., description="Old Password", min_length=5, max_length=255
    )

    @validator("old_password")
    def passwords_check(cls, v, values, **kwargs):
        if v == values["password1"] and v == values["password2"]:
            raise ValueError("new and old password should be different")
        return v


class UpdateProfileSchema(BaseModel):
    role: str = Field(..., description="Role")

    @validator("role")
    def supported_role(cls, v):
        if v not in config.SUPPORTED_ROLES:
            raise ValueError("unsupported role")
        return v


class LoginResponseSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
    message: Optional[str] = Field(None, description="Additional message")


class GetUserResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="Role")
    deposit: Optional[int] = Field(..., description="Deposit")

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    username: str = Field(..., description="username")
    password: str = Field(..., description="Password")


class DepositRequestSchema(BaseModel):
    value: int = Field(..., description="Value of deposited coin")

    @validator("value")
    def allowed_coin_value(cls, v):
        if v not in config.SUPPORTED_COINS:
            raise ValueError(
                f"deposited coin must have one of the following values {config.SUPPORTED_COINS}"
            )
        return v
