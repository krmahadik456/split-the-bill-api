from datetime import datetime, timedelta, timezone
from typing import Annotated, List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Field, Session, SQLModel, create_engine, select
from passlib.context import CryptContext
import jwt
import bcrypt

bcrypt.__about__ = type("About", (), {"__version__": "4.0.1"})

SECRET_KEY = "super_secret_key_do_not_share" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI(title="Split the Bill API")

# --- DATABASE MODELS ---
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str

class Bill(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    owner_id: int = Field(foreign_key="user.id") 

class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    description: str
    amount: float
    bill_id: int = Field(foreign_key="bill.id")
    payer_id: int = Field(foreign_key="user.id")

class BillCreate(SQLModel):
    name: str

class ExpenseCreate(SQLModel):
    description: str
    amount: float

sqlite_url = "sqlite:///split.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

create_db_and_tables()

# --- AUTH HELPERS ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    with Session(engine) as session:
        yield session

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --- ENDPOINTS ---
@app.post("/register")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.exec(select(User).where(User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully!", "user_id": new_user.id}

@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}! You are authenticated."}

@app.post("/bills")
def create_bill(bill_data: BillCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_bill = Bill(name=bill_data.name, owner_id=current_user.id)
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return {"message": "Bill created successfully!", "bill": new_bill}

@app.get("/bills")
def get_my_bills(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bills = db.exec(select(Bill).where(Bill.owner_id == current_user.id)).all()
    return {"bills": bills}

@app.post("/bills/{bill_id}/expenses")
def add_expense(bill_id: int, expense_data: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bill = db.get(Bill, bill_id)
    if not bill or bill.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bill not found or unauthorized")

    new_expense = Expense(
        description=expense_data.description,
        amount=expense_data.amount,
        bill_id=bill.id,
        payer_id=current_user.id
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return {"message": "Expense added successfully!", "expense": new_expense}

@app.get("/bills/{bill_id}/expenses", response_model=List[Expense])
def get_bill_expenses(bill_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bill = db.get(Bill, bill_id)
    if not bill or bill.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bill not found or unauthorized")
    expenses = db.exec(select(Expense).where(Expense.bill_id == bill_id)).all()
    return expenses

# --- NEW: CALCULATE TOTAL ENDPOINT ---
@app.get("/bills/{bill_id}/summary")
def get_bill_summary(bill_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bill = db.get(Bill, bill_id)
    if not bill or bill.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bill not found or unauthorized")
    
    # Fetch all expenses for this bill
    expenses = db.exec(select(Expense).where(Expense.bill_id == bill_id)).all()
    
    # Calculate the total using Python's sum() function
    total = sum(expense.amount for expense in expenses)
    
    return {
        "bill_name": bill.name,
        "total_expenses": len(expenses),
        "total_amount": total
    }