from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class CategoryInProduct(BaseModel):
    """Category info dentro do product."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class ProductBase(BaseModel):
    """Base para criar/atualizar produto."""

    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: int


class ProductCreate(ProductBase):
    """Schema para criar produto."""

    pass


class ProductUpdate(BaseModel):
    """Schema para atualizar produto."""

    name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category_id: int | None = None
    is_active: bool | None = None


class ProductUpdateStock(BaseModel):
    """Schema para atualizar apenas o estoque."""

    stock: int = Field(..., ge=0)


class ProductResponse(ProductBase):
    """Schema de resposta do produto."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: CategoryInProduct


class ProductFilter(BaseModel):
    """Filtros para busca de produtos."""

    name: str | None = None
    category_id: int | None = None
    min_price: float | None = Field(None, ge=0)
    max_price: float | None = Field(None, ge=0)
    is_active: bool = True
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
