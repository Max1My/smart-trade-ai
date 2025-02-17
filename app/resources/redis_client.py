import asyncio
import logging

import json
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self, redis_url="redis://localhost:6379", password=None):
        self.redis_url = redis_url
        self.password = password
        self.pool = None
        self.redis = None

    async def connect(self):
        """Подключение к Redis с пулом подключений"""
        self.pool = aioredis.ConnectionPool.from_url(
            self.redis_url,
            password=self.password,
            max_connections=100
        )
        self.redis = aioredis.Redis(connection_pool=self.pool)
        logger.info("✅ Подключено к Redis с пулом подключений")

    async def close(self):
        """Закрытие Redis-соединения и пула."""
        if self.redis:
            await self.redis.close()
        if self.pool:
            await self.pool.disconnect()

    async def _reconnect(self):
        """Переинициализировать подключение, если оно потеряно."""
        logger.warning("Попытка переподключения к Redis...")
        await self.close()
        await asyncio.sleep(1)  # небольшая пауза перед повтором
        await self.connect()

    async def set(self, key: str, value: dict, expire: int = 60):
        try:
            await self.redis.set(key, json.dumps(value), ex=expire)
        except (aioredis.ConnectionError, OSError) as e:
            logger.error(f"Ошибка записи в Redis (set): {e}")
            await self._reconnect()
            # Повторная попытка (опционально)
            await self.redis.set(key, json.dumps(value), ex=expire)

    async def add_to_queue(self, queue_name: str, message: dict):
        """Добавление одного сообщения в очередь Redis"""
        try:
            await self.redis.lpush(queue_name, json.dumps(message))
        except (aioredis.ConnectionError, OSError) as e:
            logger.error(f"Ошибка записи в Redis (add_to_queue): {e}")
            await self._reconnect()
            # Повторная попытка (опционально)
            await self.redis.lpush(queue_name, json.dumps(message))

    async def add_to_queue_batch(self, queue_name: str, message_buffer: list, batch_size: int = 100):
        """Добавление нескольких сообщений в очередь пакетами"""
        try:
            for i in range(0, len(message_buffer), batch_size):
                batch = message_buffer[i:i + batch_size]
                await self.redis.lpush(queue_name, *[json.dumps(msg) for msg in batch])
        except (aioredis.ConnectionError, OSError) as e:
            logger.error(f"Ошибка записи в Redis (add_to_queue_batch): {e}")
            await self._reconnect()
            # Повторная попытка (зависит от того, как хотите обрабатывать —
            # можно снова пройтись циклом, который неудавшиеся batch'и зальёт)

    async def pop_from_queue(self, queue_name: str):
        """Извлекает одно сообщение (dict) из очереди (FIFO)"""
        try:
            data = await self.redis.rpop(queue_name)
            if data:
                return json.loads(data)
            return None
        except (aioredis.ConnectionError, OSError) as e:
            logger.error(f"Ошибка чтения из Redis (pop_from_queue): {e}")
            await self._reconnect()
            return None
