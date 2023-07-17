import pytest
import asyncio
from store import Pool


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def pool():
    return Pool(10)


@pytest.mark.asyncio
async def test_get_object(pool):
    obj = await pool.get_object()
    assert obj in pool.active


@pytest.mark.asyncio
async def test_get_object_no_objects_available(pool):
    with pytest.raises(ValueError) as exc_info:
        for _ in range(11):
            await pool.get_object()

    assert "cant be given" in str(exc_info.value)


@pytest.mark.asyncio
async def test_free_object(pool):
    obj = await pool.get_object()
    await pool.free_object(obj)
    assert obj not in pool.active
    assert obj in pool.idle


@pytest.mark.asyncio
async def test_free_object_invalid_object(pool):
    with pytest.raises(ValueError) as exc_info:
        await pool.free_object(100)

    assert "cant be freed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_object(pool):
    await pool.create(5)
    assert 5 in pool.idle


@pytest.mark.asyncio
async def test_create_object_number_exists(pool):
    with pytest.raises(ValueError) as exc_info:
        await pool.create(1)

    assert "number already exists" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_object_capacity_reached(pool):
    for i in range(3, 10):
        await pool.create(i)

    with pytest.raises(ValueError) as exc_info:
        await pool.create(11)

    assert "capacity is reached" in str(exc_info.value)

