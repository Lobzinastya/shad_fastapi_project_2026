from pydantic import BaseModel, EmailStr, ConfigDict
from .books import ReturnedBook

__all__ = [
    "PatchSeller",
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "ReturnedAllSellers",
]


# Базовый класс "Продавец"
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


# Класс для обработки входных данных для частичного обновления данных о продавце
class PatchSeller(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    e_mail: EmailStr | None = None


# Класс для валидации входящих данных. Без id
class IncomingSeller(BaseSeller):
    password: str


# # Класс, валидирующий исходящие данные. содержит id
# # Возвращаемый продавец (без password)
# class ReturnedSeller(BaseSeller):
#     id: int
#     books: list["ReturnedBook"] = []
#
#     model_config = ConfigDict(from_attributes=True)
#
# # Класс для возврата массива объектов "Продавец"
# class ReturnedAllSellers(BaseModel):
#     sellers: list[ReturnedSeller]
#
# ReturnedSeller.model_rebuild()


class ReturnedSeller(BaseSeller):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook] = []


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]