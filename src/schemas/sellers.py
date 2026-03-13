from pydantic import BaseModel, EmailStr

__all__ = [
    "PatchSeller",
    "IncomingSeller",
    "ReturnedSeller",
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


# Класс, валидирующий исходящие данные. содержит id
class ReturnedSeller(BaseSeller):  # {"id": 1, "first_name": "...", ...}
    id: int
    class Config:
        from_attributes = True


# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]