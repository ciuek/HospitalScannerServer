from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Sekret do generowania tokenów JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Schemat danych pacjenta
class Patient(BaseModel):
    id: int
    name: str
    age: int
    medical_history: str

# Schemat danych użytkownika
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Schemat danych użytkownika z tokenem
class UserInDB(User):
    hashed_password: str
    password: Optional[str] = None

# Tworzenie instancji FastAPI
app = FastAPI()

# Tworzenie instancji OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Tworzenie instancji CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Symulacja bazy danych
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": pwd_context.hash("secret"),
    }
}

# Symulacja bazy danych pacjentów
fake_patient_db = {
    1: {"id": 1, "name": "twoja stara", "age": 30, "medical_history": "pali blanty kurwa jebana xd"},
    2: {"id": 2, "name": "Jane Doe", "age": 25, "medical_history": "None"},
}

# Funkcje pomocnicze
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = User(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Ścieżki API
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/patient/{patient_id}", response_model=Patient)
async def read_patient(patient_id: int, current_user: User = Depends(get_current_user)):
    if patient_id not in fake_patient_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    return fake_patient_db[patient_id]