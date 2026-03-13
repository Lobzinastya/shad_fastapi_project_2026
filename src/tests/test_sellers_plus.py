import pytest
from fastapi import status
from sqlalchemy import select

from src.models.sellers import Seller
from src.models.books import Book

API_V1_URL_PREFIX = "/api/v1/seller"

# НОВЫЕ ТЕСТЫ, про sellers, relations, доп



#Тест на ручку регистрации продавца
@pytest.mark.asyncio()
async def test_create_seller(async_client):

    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "test@test.com",
        "password": "1234"
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()

    seller_id = result.pop("id")

    assert seller_id is not None

    assert result == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "test@test.com",
    }

# Тест на ручку получения списка продавцов
@pytest.mark.asyncio()
async def test_get_sellers(db_session, async_client):
    seller1 = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="test1@test.com",
        password="1234"
    )

    seller2 = Seller(
        first_name="Petr",
        last_name="Petrov",
        e_mail="test2@test.com",
        password="1234"
    )

    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    data = response.json()["sellers"]

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 2
    assert {s["e_mail"] for s in data} == {"test1@test.com", "test2@test.com"}


#Тест на ручку получения одного продавца по id
@pytest.mark.asyncio()
async def test_get_single_seller(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="test@test.com",
        password="1234"
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == seller.id
    assert "password" not in data

#Тест на ручку обновления данных продавца
@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):

    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="test@test.com",
        password="1234"
    )

    db_session.add(seller)
    await db_session.flush()

    data = {
        "id": seller.id,
        "first_name": "Petr",
        "last_name": "Petrov",
        "e_mail": "new@test.com",
        "password": "5678"
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        json=data
    )
    assert response.status_code == status.HTTP_200_OK
    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Petr"
    assert res.last_name == "Petrov"

#Тест на ручку удаления продавца
@pytest.mark.asyncio()
async def test_delete_seller(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="test@test.com",
        password="1234"
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    sellers = await db_session.execute(select(Seller))
    res = sellers.scalars().all()
    assert len(res) == 0

#Тест проверки связи Seller - Book
@pytest.mark.asyncio()
async def test_seller_books_relation(db_session):

    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="test@test.com",
        password="1234"
    )

    db_session.add(seller)
    await db_session.flush()

    book = Book(
        title="Test Book",
        author="Pushkin",
        pages=100,
        year=2024,
        seller_id=seller.id
    )

    db_session.add(book)
    await db_session.flush()

    res = await db_session.get(Book, book.id)

    assert res.seller_id == seller.id

#Тест на получение продавца вместе со списком его книг
@pytest.mark.asyncio()
async def test_get_seller_with_books(db_session, async_client):
        seller = Seller(
            first_name="Ivan",
            last_name="Ivanov",
            e_mail="test@test.com",
            password="1234"
        )

        db_session.add(seller)
        await db_session.flush()

        book1 = Book(
            title="Test Book",
            author="Pushkin",
            pages=100,
            year=2024,
            seller_id=seller.id
        )

        book2 = Book(
            title="War and Peace",
            author="Tolstoy",
            pages=500,
            year=2023,
            seller_id=seller.id
        )

        db_session.add_all([book1, book2])
        await db_session.flush()

        response = await async_client.get(f"/api/v1/seller/{seller.id}")

        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert len(data["books"]) == 2
        assert "password" not in data
        titles = {b["title"] for b in data["books"]}
        assert titles == {"Test Book", "War and Peace"}


#Тест, что поле password не возвращается
@pytest.mark.asyncio()
async def test_seller_password_not_returned(async_client):
    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "test@test.com",
        "password": "1234"
    }
    response = await async_client.post("/api/v1/seller/", json=data)
    result = response.json()
    assert "password" not in result

#Тест, что создание книги невозможно без seller_id
@pytest.mark.asyncio()
async def test_book_requires_seller(async_client):

    data = {
        "title": "Test Book",
        "author": "Pushkin",
        "count_pages": 100,
        "year": 2024
    }

    response = await async_client.post("/api/v1/books/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

#Тест каскадного удаления книг при удалении продавца
@pytest.mark.asyncio()
async def test_delete_seller_cascade_books(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="test@test.com",
        password="1234"
    )

    db_session.add(seller)
    await db_session.flush()

    book1 = Book(
        title="Book1",
        author="Pushkin",
        pages=100,
        year=2024,
        seller_id=seller.id
    )

    book2 = Book(
        title="Book2",
        author="Tolstoy",
        pages=200,
        year=2023,
        seller_id=seller.id
    )

    db_session.add_all([book1, book2])
    await db_session.commit()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    sellers = await db_session.execute(select(Seller))
    books = await db_session.execute(select(Book))

    assert len(sellers.scalars().all()) == 0
    assert len(books.scalars().all()) == 0

#Тест получения продавца с несуществующим id
@pytest.mark.asyncio()
async def test_get_seller_not_found(async_client):
    response = await async_client.get("/api/v1/seller/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

#Тест обновления книги с несуществующим id
@pytest.mark.asyncio()
async def test_update_book_not_found(async_client):
    data = {
        "title": "Test",
        "author": "Author",
        "pages": 100,
        "year": 2024,
        "id": 9999,
        "seller_id": 1
    }
    response = await async_client.put("/api/v1/books/9999", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

#Тест создания книги с несуществующим seller_id
@pytest.mark.asyncio()
async def test_create_book_with_invalid_seller(async_client):
    data = {
        "title": "Test",
        "author": "Author",
        "count_pages": 100,
        "year": 2024,
        "seller_id": 9999
    }
    response = await async_client.post("/api/v1/books/", json=data)
    assert response.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_CONTENT)

#Тест получения пустого списка книг
@pytest.mark.asyncio()
async def test_get_books_empty(async_client):
    response = await async_client.get("/api/v1/books/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["books"] == []

#Тест получения пустого списка книг
@pytest.mark.asyncio()
async def test_seller_with_no_books(db_session, async_client):
    seller1 = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan@test.com",
        password="1234"
    )
    seller2 = Seller(
        first_name="Petr",
        last_name="Petrov",
        e_mail="petr@test.com",
        password="1234"
    )

    db_session.add_all([seller1, seller2])
    await db_session.flush()

    book = Book(
        title="Test Book",
        author="Pushkin",
        pages=100,
        year=2024,
        seller_id=seller1.id
    )

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller2.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == seller2.id
    assert data["books"] == []

# Тест, что нельзя создать двух продавцов с одинаковым email
@pytest.mark.asyncio()
async def test_create_seller_duplicate_email(async_client):
    data1 = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "test@test.com",
        "password": "1234"
    }
    response1 = await async_client.post("/api/v1/seller/", json=data1)
    assert response1.status_code == status.HTTP_201_CREATED
    data2 = {
        "first_name": "Ivanchik",
        "last_name": "Ivanovchik",
        "e_mail": "test@test.com",
        "password": "1234"
    }
    response2 = await async_client.post("/api/v1/seller/", json=data2)

    assert response2.status_code == status.HTTP_409_CONFLICT