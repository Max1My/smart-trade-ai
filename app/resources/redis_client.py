import asyncio
import logging

import json
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self, redis_url="redis://localhost:6379", password=None, max_connections: int = 100):
        self.redis_url = redis_url
        self.password = password
        self.pool = None
        self.redis = None
        self.max_connections = max_connections

    async def connect(self):
        """
        Устанавливает подключение к Redis, если оно еще не установлено или не активно.
        Если уже существует активное соединение, метод просто возвращает управление.
        """
        # Если соединение уже установлено, проверяем его работоспособность.
        if self.redis is not None:
            try:
                if await self.redis.ping():
                    return
            except Exception as e:
                logger.warning(f"Существующее соединение Redis неактивно: {e}")
                # Закрываем старый пул, чтобы создать новый.
                await self.close()

        # Если есть уже созданный пул, но соединение не активно, закрываем его.
        if self.pool is not None:
            await self.pool.disconnect()

        # Создаем новый пул соединений.
        self.pool = aioredis.ConnectionPool.from_url(
            self.redis_url,
            password=self.password,
            max_connections=self.max_connections
        )
        self.redis = aioredis.Redis(connection_pool=self.pool)
        logger.info("✅ Подключено к Redis с пулом подключений")

    async def close(self):
        """Закрывает соединение и пул Redis, затем зануляет ссылки."""
        if self.redis:
            try:
                await self.redis.close()
            except Exception as e:
                logger.error(f"Ошибка закрытия Redis клиента: {e}")
        if self.pool:
            try:
                await self.pool.disconnect()
            except Exception as e:
                logger.error(f"Ошибка отключения пула Redis: {e}")
        self.redis = None
        self.pool = None

    async def _reconnect(self):
        """
        Попытка переподключения: закрывает старое соединение и создает новое.
        """
        logger.warning("Попытка переподключения к Redis...")
        await self.close()
        await asyncio.sleep(1)
        await self.connect()

    async def set(self, key: str, value: dict, expire: int = 60):
        """Сохранение данных в кэш Redis с использованием пула подключений."""
        try:
            await self.redis.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logger.error(f"Ошибка записи в Redis (set): {e}")
            await self._reconnect()
            await self.redis.set(key, json.dumps(value), ex=expire)

    async def add_to_queue(self, queue_name: str, message: dict):
        """Добавление одного сообщения в очередь Redis."""
        try:
            await self.redis.lpush(queue_name, json.dumps(message))
        except Exception as e:
            logger.error(f"Ошибка записи в Redis (add_to_queue): {e}")
            await self._reconnect()
            await self.redis.lpush(queue_name, json.dumps(message))

    async def add_to_queue_batch(self, queue_name: str, message_buffer: list, batch_size: int = 100):
        """Добавление нескольких сообщений в очередь пакетами."""
        try:
            for i in range(0, len(message_buffer), batch_size):
                batch = message_buffer[i:i + batch_size]
                await self.redis.lpush(queue_name, *[json.dumps(msg) for msg in batch])
        except Exception as e:
            logger.error(f"Ошибка записи в Redis (add_to_queue_batch): {e}")
            await self._reconnect()
            # Опционально можно повторить попытку:
            for i in range(0, len(message_buffer), batch_size):
                batch = message_buffer[i:i + batch_size]
                await self.redis.lpush(queue_name, *[json.dumps(msg) for msg in batch])

    async def pop_from_queue(self, queue_name: str):
        """Извлекает одно сообщение (dict) из очереди."""
        try:
            data = await self.redis.rpop(queue_name)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Ошибка чтения из Redis (pop_from_queue): {e}")
            await self._reconnect()
            return None
