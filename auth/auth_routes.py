from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import get_current_identity, require_roles
from database.db_session import get_db
from database.models.user_models import UsersRole
from .auth_services import (
    authenticate_user,
    issue_token_for_user,
    get_user_by_id,
    create_user,
    bootstrap_first_admin_if_none_exists,
)
from .auth_schema import (
    Identity,
    LoginRequest,
    LoginResponse,
    SignupRequest,
    TokenData,
    UserCreateRequest,
    UserData,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = issue_token_for_user(user)
    return LoginResponse(
        success=True,
        message="Logged in successfully",
        data=TokenData(access_token=token, user=UserData.model_validate(user)),
    )


@router.get("/me", response_model=UserResponse)
def me(identity: Identity = Depends(get_current_identity), db: Session = Depends(get_db)):
    user = get_user_by_id(db, identity.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(success=True, message="OK", data=UserData.model_validate(user))


@router.post("/signup", response_model=UserResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """
    Public self-serve signup. Role is limited to VOLUNTEER or PATIENT —
    ADMIN and DOCTOR accounts can only be created by an existing admin/doctor
    via POST /auth/users.
    """
    create_payload = UserCreateRequest(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password=payload.password,
        role=UsersRole(payload.role.value),
    )
    try:
        user = create_user(db, create_payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UserResponse(success=True, message="Account created", data=UserData.model_validate(user))


@router.post("/users", response_model=UserResponse)
def create_staff_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    identity: Identity = Depends(require_roles(UsersRole.ADMIN, UsersRole.DOCTOR)),
):
    """Admin/Doctor: create a DOCTOR / VOLUNTEER / COORDINATOR / ADMIN / PATIENT account directly."""
    try:
        user = create_user(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UserResponse(success=True, message="User created", data=UserData.model_validate(user))


@router.post("/bootstrap-admin", response_model=UserResponse)
def bootstrap_admin(payload: UserCreateRequest, db: Session = Depends(get_db)):
    """
    One-time setup route: only works if the users table is completely empty.
    Use this once to create your very first ADMIN login, then create
    everyone else via POST /auth/users. Consider removing/disabling this
    route once your first admin exists.
    """
    user = bootstrap_first_admin_if_none_exists(
        db, name=payload.name, email=payload.email, password=payload.password
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Users already exist — use POST /auth/users (as an admin or doctor) instead",
        )
    return UserResponse(success=True, message="First admin created", data=UserData.model_validate(user))