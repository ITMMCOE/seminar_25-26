from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, status, Form
# FIX: Import OAuth2PasswordRequestForm for handling login form data
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Annotated
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
import os
import hashlib
import secrets
import base64
from bson import ObjectId

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client['credential_dapp']
users_collection = db['users']
credentials_collection = db['credentials']

# JWT configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 1440))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str

# This model is no longer needed for the login route
# class UserLogin(BaseModel):
#     username: str
#     password: str

class IssueCredentialRequest(BaseModel):
    student_name: str
    degree: str
    institution: str
    graduation_year: int
    grade: str
    subjects: List[dict]

class User(BaseModel):
    username: str
    email: str
    full_name: str

# Mock Blockchain Service
class MockBlockchainService:
    def __init__(self):
        self.transaction_counter = 1000
        self.block_number = 5000000
    
    def mint_nft(self, to_address: str, token_uri: str) -> dict:
        self.transaction_counter += 1
        self.block_number += 1
        
        tx_hash = '0x' + hashlib.sha256(f"{to_address}{token_uri}{self.transaction_counter}".encode()).hexdigest()
        token_id = self.transaction_counter
        
        return {
            'transaction_hash': tx_hash,
            'token_id': token_id,
            'block_number': self.block_number,
            'from': '0x0000000000000000000000000000000000000000',
            'to': to_address,
            'gas_used': 150000,
            'status': 'success',
            'network': 'Sepolia Testnet (Simulated)'
        }
    
    def verify_token(self, token_id: int) -> dict:
        return {
            'token_id': token_id,
            'exists': True,
            'verified': True,
            'network': 'Sepolia Testnet (Simulated)'
        }

# Mock IPFS Service
class MockIPFSService:
    def __init__(self):
        self.storage = {}
    
    def upload_file(self, file_content: bytes, filename: str) -> str:
        content_hash = hashlib.sha256(file_content).hexdigest()
        cid = f"Qm{content_hash[:44]}"
        
        self.storage[cid] = {
            'content': base64.b64encode(file_content).decode('utf-8'),
            'filename': filename,
            'size': len(file_content),
            'uploaded_at': datetime.utcnow().isoformat()
        }
        
        return cid
    
    def get_file(self, cid: str) -> Optional[dict]:
        return self.storage.get(cid)

blockchain_service = MockBlockchainService()
ipfs_service = MockIPFSService()

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def generate_wallet_address() -> str:
    return '0x' + secrets.token_hex(20)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = users_collection.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Academic Credential dApp API"}

@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    if users_collection.find_one({"username": user_data.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if users_collection.find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "password_hash": hash_password(user_data.password),
        "wallet_address": generate_wallet_address(),
        "created_at": datetime.utcnow().isoformat(),
        "role": "student"
    }
    
    users_collection.insert_one(user)
    
    return {
        "message": "User registered successfully",
        "username": user_data.username,
        "wallet_address": user["wallet_address"]
    }

# --- THIS IS THE FIX ---
# The function now depends on OAuth2PasswordRequestForm, which correctly
# handles the 'x-www-form-urlencoded' data from your login form.
@app.post("/api/auth/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users_collection.find_one({"username": form_data.username})
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user["username"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "wallet_address": user["wallet_address"]
        }
    }
# --- END OF FIX ---

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "wallet_address": current_user["wallet_address"]
    }

@app.post("/api/credentials/issue")
async def issue_credential(
    student_name: str = Form(...),
    degree: str = Form(...),
    institution: str = Form(...),
    graduation_year: int = Form(...),
    grade: str = Form(...),
    marksheet_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    file_content = await marksheet_file.read()
    ipfs_cid = ipfs_service.upload_file(file_content, marksheet_file.filename)
    
    metadata = {
        "name": f"Academic Credential - {student_name}",
        "description": f"{degree} from {institution}",
        "student_name": student_name,
        "degree": degree,
        "institution": institution,
        "graduation_year": graduation_year,
        "grade": grade,
        "marksheet_ipfs": ipfs_cid,
        "issued_date": datetime.utcnow().isoformat()
    }
    
    nft_result = blockchain_service.mint_nft(
        to_address=current_user["wallet_address"],
        token_uri=ipfs_cid
    )
    
    credential = {
        "owner_username": current_user["username"],
        "owner_wallet": current_user["wallet_address"],
        "token_id": nft_result["token_id"],
        "transaction_hash": nft_result["transaction_hash"],
        "block_number": nft_result["block_number"],
        "ipfs_cid": ipfs_cid,
        "metadata": metadata,
        "created_at": datetime.utcnow().isoformat(),
        "status": "confirmed"
    }
    
    result = credentials_collection.insert_one(credential)
    credential["_id"] = str(result.inserted_id)
    
    return {
        "message": "Credential issued successfully",
        "credential_id": credential["_id"],
        "token_id": nft_result["token_id"],
        "transaction_hash": nft_result["transaction_hash"],
        "block_number": nft_result["block_number"],
        "ipfs_cid": ipfs_cid,
        "network": "Sepolia Testnet"
    }

@app.get("/api/credentials/list")
async def list_credentials(current_user: dict = Depends(get_current_user)):
    credentials = list(credentials_collection.find({"owner_username": current_user["username"]}))
    
    for cred in credentials:
        cred["_id"] = str(cred["_id"])
    
    return {"credentials": credentials}

@app.get("/api/credentials/{credential_id}")
async def get_credential(credential_id: str, current_user: dict = Depends(get_current_user)):
    try:
        credential = credentials_collection.find_one({"_id": ObjectId(credential_id)})
    except:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    credential["_id"] = str(credential["_id"])
    return credential

@app.get("/api/credentials/{credential_id}/verify")
async def verify_credential(credential_id: str):
    try:
        credential = credentials_collection.find_one({"_id": ObjectId(credential_id)})
    except:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    verification = blockchain_service.verify_token(credential["token_id"])
    
    return {
        "verified": True,
        "token_id": credential["token_id"],
        "transaction_hash": credential["transaction_hash"],
        "owner_wallet": credential["owner_wallet"],
        "metadata": credential["metadata"],
        "blockchain_verification": verification,
        "ipfs_cid": credential["ipfs_cid"]
    }

@app.get("/api/credentials/{credential_id}/download")
async def download_marksheet(credential_id: str, current_user: dict = Depends(get_current_user)):
    try:
        credential = credentials_collection.find_one({"_id": ObjectId(credential_id)})
    except:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    if credential["owner_username"] != current_user["username"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_data = ipfs_service.get_file(credential["ipfs_cid"])
    
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found in IPFS")
    
    file_content = base64.b64decode(file_data["content"])
    
    return Response(
        content=file_content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_data["filename"]}"'}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
