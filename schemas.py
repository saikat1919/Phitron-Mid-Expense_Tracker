from typing import Annotated, Optional, Literal
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class CreateUser(BaseModel):

    username: Annotated[str, Field(..., description="Enter an Unique Username")]
    email: EmailStr
    password: Annotated[str, Field(..., min_length=8)]

class CreateTransaction(BaseModel):
    id: int
    title: Annotated[str, Field(..., description="Enter a title", min_length=1, max_length=50)]
    amount: Annotated[float, Field(..., gt=0)]
    type: Literal["income", "expense"]
    category: Annotated[str, Field(..., description="Transaction Category")]
    date: datetime

class UpdateTransaction(BaseModel):
    title: Optional[str] = Field(default=None)
    amount: Optional[float] = Field(default=None)
    type: Optional[Literal["income", "expense"]] = Field(default=None)
    category: Optional[str] = Field(default=None)
    date: Optional[datetime] = Field(default=None)

class TransactionResponse(BaseModel):
    id: int
    title: str
    amount: float
    type: Literal["income", "expense"]
    category: str
    date: datetime

    class Config:
        from_attributes = True