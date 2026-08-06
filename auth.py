from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

OAuth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "Fbue1cahV/B68ZiCgJl4cxw1DWtq9np/mrbXxCA13MY="  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2160

def criar_token(dados: dict):
    to_encode = dados.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
     
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def usuario_atual(token:str = Depends(OAuth2_scheme)):
    payload = verificar_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail= 'Token Invalido ou expirado')
    return payload

def exigir_cargo_admin(usuario:dict = Depends(usuario_atual)):
    if usuario.get('cargo') != 'admin':
        raise HTTPException(status_code=403, detail='Acesso permitido somente a administradores')
    return usuario