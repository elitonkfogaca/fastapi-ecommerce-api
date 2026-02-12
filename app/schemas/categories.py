from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Base para criar/atualizar categoria."""

    name: str = Field(..., min_length=3, max_length=100)


class CategoryCreate(CategoryBase):
    """Schema para criar categoria."""

    pass


class CategoryUpdate(BaseModel):
    """Schema para atualizar categoria."""

    name: str | None = Field(None, min_length=3, max_length=100)


class CategoryResponse(CategoryBase):
    """Schema de resposta da categoria."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str


class CategoryWithProductCount(CategoryResponse):
    """Categoria com contagem de produtos."""

    product_count: int = 0
