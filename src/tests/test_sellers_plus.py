import pytest
from fastapi import status
from sqlalchemy import select

from src.models.sellers import Seller
from src.models.books import Book

API_V1_URL_PREFIX = "/api/v1/seller"


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


@pytest.mark.asyncio()
async def test_get_sellers(db_session, async_client):

    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="test@test.com",
        password="1234"
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "sellers": [
            {
                "id": seller.id,
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "e_mail": "test@test.com",
            }
        ]
    }


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

    assert response.json()["id"] == seller.id


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

        book = Book(
            title="Test Book",
            author="Pushkin",
            pages=100,
            year=2024,
            seller_id=seller.id
        )

        db_session.add(book)
        await db_session.flush()

        response = await async_client.get(f"/api/v1/seller/{seller.id}")

        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert len(data["books"]) == 1
        assert data["books"][0]["title"] == "Test Book"


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

    book = Book(
        title="Test Book",
        author="Pushkin",
        pages=100,
        year=2024,
        seller_id=seller.id
    )

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller.id}")

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data["books"]) == 1
    assert data["books"][0]["title"] == "Test Book"


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


@pytest.mark.asyncio()
async def test_book_requires_seller(async_client):

    data = {
        "title": "Test Book",
        "author": "Pushkin",
        "count_pages": 100,
        "year": 2024
    }

    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio()
async def test_book_requires_seller(async_client):

    data = {
        "title": "Test Book",
        "author": "Pushkin",
        "count_pages": 100,
        "year": 2024
    }

    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY



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

    book = Book(
        title="Test Book",
        author="Pushkin",
        pages=100,
        year=2024,
        seller_id=seller.id
    )

    db_session.add(book)
    await db_session.commit()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    books = await db_session.execute(select(Book))
    res = books.scalars().all()

    assert len(res) == 0