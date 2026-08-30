import enum

from pydantic import BaseModel, EmailStr

from database.models.user_models import UsersRole


class SignupRole(str, enum.Enum):
    """Roles a person can self-assign via POST /auth/signup.
    ADMIN and DOCTOR are deliberately excluded — those are only created
    by an existing admin via POST /auth/users."""

    VOLUNTEER = "VOLUNTEER"
    PATIENT = "PATIENT"


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    password: str
    role: SignupRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    password: str
    role: UsersRole


class UserData(BaseModel):
    id: str
    name: str
    email: str
    phone: str | None
    role: UsersRole
    is_active: bool

    class Config:
        from_attributes = True


class Identity(BaseModel):
    """What Depends(get_current_identity) resolves to on every protected route."""

    user_id: str
    email: str
    role: UsersRole


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserData


class LoginResponse(BaseModel):
    success: bool
    message: str
    data: TokenData


class UserResponse(BaseModel):
    success: bool
    message: str
    data: UserData