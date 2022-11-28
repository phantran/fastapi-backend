from typing import List, Optional

from pydantic import BaseModel, Field, validator


class ProductDeleteRequestSchema(BaseModel):
    product_id: int = Field(..., description="Product id")


class ProductUpdateRequestSchema(BaseModel):
    id: int = Field(..., description="Product id")
    product_name: str = Field(..., description="Product name")
    amount_available: int = Field(..., description="Amount available", ge=0)
    cost: int = Field(..., description="Product cost", gt=0)

    @validator("cost")
    def cost_is_multiples_of_5(cls, v):
        if v % 5 != 0:
            raise ValueError("cost of products must be in multiples of 5")
        return v


class ProductResponseSchema(BaseModel):
    id: int = Field(..., description="Product id")
    product_name: str = Field(..., description="Product name")
    seller_id: int = Field(..., description="Seller id")
    amount_available: int = Field(..., description="Amount available")
    cost: int = Field(..., description="Product cost")


class ProductCreateRequestSchema(BaseModel):
    product_name: str = Field(..., description="Product name")
    amount_available: int = Field(..., description="Amount available", ge=0)
    cost: int = Field(..., description="Product cost", gt=0)

    @validator("cost")
    def cost_is_multiples_of_5(cls, v):
        if v % 5 != 0:
            raise ValueError("cost of products must be in multiples of 5")
        return v


class ProductCreateResponseSchema(BaseModel):
    message: str = Field(..., description="Message")
    product_name: str = Field(..., description="Product name")


class BuyRequestSchema(BaseModel):
    product_id: int = Field(..., description="Product id")
    amount: int = Field(..., description="Amount to buy", gt=0)


class BuyResponseSchema(BaseModel):
    total_spent: int = Field(..., description="Total spent")
    product_name: str = Field(..., description="Product name")
    product_id: int = Field(..., description="Product id")
    change: Optional[List[int]] = Field(None, description="Change")
