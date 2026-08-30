import uuid

from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password, verify_password
from database.models.user_models import Users, UsersRole
from .auth_schema import UserCreateRequest


def authenticate_user(db: Session, email: str, password: str) -> Users | None:
    user = db.query(Users).filter(Users.email == email).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def issue_token_for_user(user: Users) -> str:
    return create_access_token({"user_id": user.id, "email": user.email, "role": user.role.value})


def create_user(db: Session, payload: UserCreateRequest) -> Users:
    existing = db.query(Users).filter(Users.email == payload.email).first()
    if existing:
        raise ValueError(f"A user with email {payload.email} already exists")

    user = Users(
        id=str(uuid.uuid4()),  # Users.id has no server/app default in the generated model -- must set it here
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: str) -> Users | None:
    return db.query(Users).filter(Users.id == user_id).first()


def bootstrap_first_admin_if_none_exists(db: Session, name: str, email: str, password: str) -> Users | None:
    """
    One-time convenience: if there are zero users in the table yet, create
    the first ADMIN account so someone can log in and create the rest via
    POST /auth/users. No-op if any user already exists.
    """
    any_user = db.query(Users).first()
    if any_user:
        return None

    admin = Users(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=UsersRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin