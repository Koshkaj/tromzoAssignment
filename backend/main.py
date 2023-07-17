import os
from typing import List

import uvicorn

import strawberry
from strawberry.asgi import GraphQL
from strawberry.exceptions import StrawberryException

from pool.store import Pool


pool_size = os.getenv("POOL_SIZE", 10)
pool = Pool(pool_size)

@strawberry.type
class PoolStatus:
    active: List[int] = strawberry.field()
    idle: List[int] = strawberry.field()
    capacity: int = strawberry.field()


@strawberry.type
class Query:
    @strawberry.field
    async def get_status(self) -> PoolStatus:
        return PoolStatus(active=list(pool.active), idle=list(pool.idle), capacity=pool.cap)

    @strawberry.field
    async def get_object(self) -> int:
        try:
            obj = await pool.get_object()
        except ValueError as error:
            raise StrawberryException(str(error))
        return obj


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_object(self, obj: int) -> PoolStatus:
        try:
            await pool.create(obj)
        except ValueError as error:
            raise StrawberryException(str(error))
        return PoolStatus(active=list(pool.active), idle=list(pool.idle), capacity=pool.cap)

    @strawberry.mutation
    async def free_object(self, obj: int) -> PoolStatus:
        try:
            await pool.free_object(obj)
        except ValueError as error:
            raise StrawberryException(str(error))
        return PoolStatus(active=list(pool.active), idle=list(pool.idle), capacity=pool.cap)


schema = strawberry.Schema(query=Query, mutation=Mutation)


async def serve_graphql(scope, receive, send):
    app = GraphQL(schema)

    await app(scope, receive, send)


if __name__ == "__main__":
    port = os.getenv("PORT", 8080)
    uvicorn.run(serve_graphql, host="0.0.0.0", port=port, log_level="info")
