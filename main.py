import models
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from models import Users, Transactions
from sqlalchemy.orm import Session
from typing import Optional
from database import engine, SessionLocal
from typing import Annotated
from router import auth
from router.auth import user_dependency
from dependencies import db_dependency
from schemas import CreateTransaction, TransactionResponse, UpdateTransaction

app = FastAPI()
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine)

@app.post("/transactions", response_model=TransactionResponse, status_code=201)
def create_transactions(user: user_dependency, db: db_dependency, new_transaction: CreateTransaction):
    if not user:
        raise HTTPException(status_code=404, detail="Authentication Failed")

    transaction_model = Transactions(**new_transaction.model_dump(), owner_id=user.get("id"))
    db.add(transaction_model)
    db.commit()
    db.refresh(transaction_model)

    return transaction_model

@app.get("/transactions")
def get_all_transactions(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    return db.query(Transactions).filter(Transactions.owner_id == user.get("id")).all()


@app.get("/transactions/filter")
def filter_transactions(
    user: user_dependency,
    db: db_dependency,
    type: Optional[str] = Query(default=None, description="Transaction type. Use Income or Expense", examples=["Income"]),
    category: Optional[str] = Query(default=None, description="Transaction category, e.g. Food, Transportation"),
    minimum_amount: Optional[float] = None,
    maximum_amount: Optional[float] = None
):
    if not user:
        raise HTTPException(status_code=404, detail="Authentication Failed")

    query = db.query(Transactions).filter(Transactions.owner_id == user.get("id"))

    if type:
        query = query.filter(Transactions.type == type)

    if category:
        query = query.filter(Transactions.category == category)

    if minimum_amount is not None:
        query = query.filter(Transactions.amount >= minimum_amount)

    if maximum_amount is not None:
        query = query.filter(Transactions.amount <= maximum_amount)

    return query.all()

@app.get("/transactions/{transaction_id}")
def get_transaction_by_id(user: user_dependency, db: db_dependency, transaction_id: int):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    transaction_by_id = db.query(Transactions).filter(Transactions.owner_id == user.get("id"), Transactions.id == transaction_id).first()
    if not transaction_by_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction_by_id


@app.put("/transactions/{transaction_id}", response_model=TransactionResponse, status_code=200)
def update_transaction(user: user_dependency, db: db_dependency, transaction_id: int, updated_transaction: UpdateTransaction):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    transaction_by_id = db.query(Transactions).filter(Transactions.owner_id == user.get("id"), Transactions.id == transaction_id).first()
    if not transaction_by_id:
        raise HTTPException(status_code=404, detail="Transaction does not exist.")

    updated_data = updated_transaction.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(transaction_by_id, key, value)

    db.commit()
    db.refresh(transaction_by_id)

    return transaction_by_id


@app.delete("/transactions/{transaction_id}")
def delete_transaction_by_id(user: user_dependency, db: db_dependency, transaction_id: int):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    transaction_by_id = db.query(Transactions).filter(Transactions.owner_id == user.get("id"), Transactions.id == transaction_id).first()
    if not transaction_by_id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction_by_id)
    db.commit()

    return JSONResponse(status_code=200, content={"Message": "Transaction Deleted Successfully"})











