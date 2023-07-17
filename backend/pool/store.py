import asyncio
import logging

logger = logging.getLogger("uvicorn")


class Pool:
    def __init__(self, cap: int):
        self.cap = cap
        self.idle = {0, 1, 2}
        self.active = set()
        self.lock = asyncio.Lock()

    def __str__(self):
        return f"active:  {self.active} | idle: {self.idle} | cap: {self.cap}"

    async def get_object(self) -> int:
        async with self.lock:
            if len(self.idle) == 0 or len(self.active) >= self.cap:
                raise ValueError("cant be given")

            obj = self.idle.pop()
            self.active.add(obj)
            return obj

    async def free_object(self, obj: int):
        async with self.lock:
            if obj not in self.active:
                raise ValueError(f"{obj} cant be freed")

            self.active.remove(obj)
            self.idle.add(obj)

    async def create(self, obj: int):
        async with self.lock:
            if len(self.idle) + len(self.active) + 1 > self.cap:
                raise ValueError("capacity is reached, number cant be added")
            if obj in self.idle or obj in self.active:
                raise ValueError("number already exists, input other number")

            self.idle.add(obj)
