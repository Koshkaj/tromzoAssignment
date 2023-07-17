import pytest

import pytest_asyncio
from httpx import AsyncClient
from main import serve_graphql


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=serve_graphql, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_get_status(client):
    response = await client.post("/graphql", json={"query": "{ getStatus { active, idle, capacity } }"})
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "getStatus" in data["data"]
    status = data["data"]["getStatus"]
    assert "active" in status
    assert "idle" in status
    assert "capacity" in status


@pytest.mark.asyncio
async def test_get_object(client):
    response = await client.post("/graphql", json={"query": "{ getObject }"})
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "getObject" in data["data"]
    obj = data["data"]["getObject"]
    assert isinstance(obj, int)


@pytest.mark.asyncio
async def test_create_object(client):
    response = await client.post("/graphql",
                                 json={"query": 'mutation { createObject(obj: 5) { active, idle, capacity } }'})
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "createObject" in data["data"]
    status = data["data"]["createObject"]
    assert "active" in status
    assert "idle" in status
    assert "capacity" in status


@pytest.mark.asyncio
async def test_free_object(client):
    response_get = await client.post("/graphql", json={"query": "{ getObject }"})
    assert response_get.status_code == 200

    data_get = response_get.json()
    assert "data" in data_get
    assert "getObject" in data_get["data"]
    obj = data_get["data"]["getObject"]

    response_free = await client.post(
        "/graphql", json={"query": 'mutation { freeObject(obj: %d) { active, idle, capacity } }' % obj}
    )
    assert response_free.status_code == 200

    data_free = response_free.json()
    assert "data" in data_free
    assert "freeObject" in data_free["data"]
    status = data_free["data"]["freeObject"]
    assert "active" in status
    assert "idle" in status
    assert "capacity" in status


@pytest.mark.asyncio
async def test_create_object_existing(client):
    # Create an object
    response_create = await client.post(
        "/graphql", json={"query": 'mutation { createObject(obj: 0) { active, idle, capacity } }'}
    )
    assert response_create.status_code == 200

    # Try to create an object with the same number
    response_duplicate = await client.post(
        "/graphql", json={"query": 'mutation { createObject(obj: 0) { active, idle, capacity } }'}
    )
    assert response_duplicate.status_code == 200

    data_duplicate = response_duplicate.json()
    assert "errors" in data_duplicate
    assert len(data_duplicate["errors"]) == 1
    assert "message" in data_duplicate["errors"][0]
    assert data_duplicate["errors"][0]["message"] == "number already exists, input other number"


@pytest.mark.asyncio
async def test_free_object_invalid(client):
    # Try to free an object that doesn't exist
    response_invalid = await client.post(
        "/graphql", json={"query": 'mutation { freeObject(obj: 100) { active, idle, capacity } }'}
    )
    assert response_invalid.status_code == 200

    data_invalid = response_invalid.json()
    assert "errors" in data_invalid
    assert len(data_invalid["errors"]) == 1
    assert "message" in data_invalid["errors"][0]
    assert data_invalid["errors"][0]["message"] == "100 cant be freed"


@pytest.mark.asyncio
async def test_create_object_capacity_reached(client):
    for i in range(3, 10):
        response_fill = await client.post(
            "/graphql", json={"query": 'mutation { createObject(obj: %d) { active, idle, capacity } }' % i}
        )
        assert response_fill.status_code == 200

    response_create = await client.post(
        "/graphql", json={"query": 'mutation { createObject(obj: 11) { active, idle, capacity } }'}
    )
    assert response_create.status_code == 200

    data_create = response_create.json()
    assert "errors" in data_create
    assert len(data_create["errors"]) == 1
    assert "message" in data_create["errors"][0]
    assert data_create["errors"][0]["message"] == "capacity is reached, number cant be added"


@pytest.mark.asyncio
async def test_invalid_query(client):
    response_invalid = await client.post("/graphql", json={"query": "{ invalidQuery }"})

    data_invalid = response_invalid.json()
    assert "errors" in data_invalid
    assert len(data_invalid["errors"]) == 1
    assert "message" in data_invalid["errors"][0]
    assert data_invalid["errors"][0]["message"] == "Cannot query field 'invalidQuery' on type 'Query'."


@pytest.mark.asyncio
async def test_invalid_mutation(client):
    response_invalid = await client.post("/graphql", json={"query": 'mutation { invalidMutation }'})

    data_invalid = response_invalid.json()
    assert "errors" in data_invalid
    assert len(data_invalid["errors"]) == 1
    assert "message" in data_invalid["errors"][0]
    assert (
            data_invalid["errors"][0]["message"] == "Cannot query field 'invalidMutation' on type 'Mutation'."
    )
