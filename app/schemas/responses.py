from typing import Generic, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Resposta de sucesso padronizada."""

    success: bool = True
    data: T
    message: str | None = None


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada."""

    success: bool = False
    error: str
    details: Any | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada."""

    success: bool = True
    data: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
