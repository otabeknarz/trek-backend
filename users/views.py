from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreateSchema, UserCheckPasswordSchema, UserResponseSchema
from trek.database import get_db

router = APIRouter()


@router.post("/sign-up/")
async def register(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    existing_user = User.get(db, username=user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(username=user_data.username, phone_number=user_data.phone_number)
    new_user.set_password(user_data.password)
    new_user.save(db)
    return {"message": "User created successfully", "user_id": new_user.id}


@router.post("/check_password/", response_model=UserResponseSchema, status_code=200)
async def check_password(
    user_data: UserCheckPasswordSchema, db: Session = Depends(get_db)
) -> User:
    if user_data.username_or_phone_number.isdigit():
        user = User.get(db, phone_number=user_data.username_or_phone_number)
    else:
        user = User.get(db, username=user_data.username_or_phone_number)
    if not user or not user.check_password(user_data.password):
        raise HTTPException(
            status_code=400, detail="Invalid credentials or password is not correct"
        )

    return user


@router.get("/", response_model=list[UserResponseSchema])
async def get_users(db: Session = Depends(get_db)) -> [User]:
    users = User.all(db)
    return users


@router.get("/@{username}", response_model=UserResponseSchema)
async def get_user_by_username(username: str, db: Session = Depends(get_db)) -> User:
    user = User.get(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/{id}")
async def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = User.get(db, id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "phone_number": user.phone_number,
    }
