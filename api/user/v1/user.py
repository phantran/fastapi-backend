from fastapi import APIRouter, Depends
from starlette.requests import Request


from app.user.schemas import (
    ExceptionResponseSchema,
    CreateUserRequestSchema,
    CreateUserResponseSchema,
    GetUserResponseSchema,
    UpdatePasswordSchema,
    UpdateProfileSchema,
    DepositRequestSchema,
    LoginRequest,
    LoginResponseSchema,
)
from app.user.services import UserService
from core.cache.redis import revoke_other_active_sessions
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

user_router = APIRouter()


@user_router.post(
    "/user",
    response_model=CreateUserResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_user(request: CreateUserRequestSchema):
    await UserService().create_user(**request.dict())
    return {"username": request.username, "role": request.role}


@user_router.delete(
    "/user",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def delete_user(request: Request):
    await UserService().delete_user(user_id=request.user.id)
    await revoke_other_active_sessions(request.user.id)
    return {"message": "successful"}


@user_router.get(
    "/user/{username}",
    response_model=GetUserResponseSchema,
    response_model_exclude={"id"},
    response_model_exclude_none=True,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_user(username: str, request: Request):
    return await UserService().get_user(
        username=username, request_user_id=request.user.id
    )


@user_router.post(
    "/login", response_model=LoginResponseSchema, response_model_exclude_none=True
)
async def login(payload: LoginRequest):
    return await UserService().login(
        username=payload.username, password=payload.password
    )


@user_router.post(
    "/logout/all",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def logout_all(request: Request):
    await UserService().logout_all(user_id=request.user.id, current_token=request.auth)
    return {"message": "successful"}


@user_router.post(
    "/user/password",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def change_password(payload: UpdatePasswordSchema, request: Request):
    await UserService().update_password(
        user_id=request.user.id,
        old_password=payload.old_password,
        password1=payload.password1,
        password2=payload.password2,
    )
    await revoke_other_active_sessions(request.user.id, request.auth)
    return {"message": "successful"}


@user_router.post(
    "/user/profile",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def update_profile(payload: UpdateProfileSchema, request: Request):
    await UserService().update_profile(
        user_id=request.user.id, payload=payload.__dict__
    )
    return {"message": "successful"}


@user_router.post(
    "/deposit",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def deposit(payload: DepositRequestSchema, request: Request):
    return await UserService().deposit(user_id=request.user.id, payload=payload)


@user_router.post(
    "/reset",
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def reset_deposit(request: Request):
    await UserService().reset_deposit(user_id=request.user.id)
    return {"message": "Deposit reset successfully"}
