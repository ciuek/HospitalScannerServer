from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import uvicorn
import schemas, oauth, crud, models
from database import SessionLocal, engine
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# fake_users_db = {
#     "Maciej": {
#         "username": "Maciej",
#         "hashed_password": oauth.pwd_context.hash("haslo123"),
#     }
# }

# fake_patient_db = {
#     1: {"id": 1, "name": "Jacek", "age": 50, "medical_history": "nie może się odnaleźć"},
#     2: {"id": 2, "name": "Grzegorz", "age": 65, "medical_history": "problemy ze świecami"},
# }


async def get_current_user(token: Annotated[str, Depends(oauth.oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, oauth.SECRET_KEY, algorithms=[oauth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# async def get_current_active_user(
#     current_user: Annotated[schemas.User, Depends(get_current_user)],
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> schemas.Token:
    user = oauth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=oauth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = oauth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

@app.get("/patient/{patient_id}", response_model=schemas.Patient)
async def read_patient(patient_id: int, current_user: schemas.User = Depends(get_current_user), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_user = crud.get_patient(db, patient_id=patient_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_user

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.1.228", port=8000)