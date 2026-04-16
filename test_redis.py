import asyncio

from app.core.redis import set_value, get_value, delete_value


async def main():
    print("=== Записываем значение в Redis ===")
    await set_value("test_key", "hello_redis", expire_seconds=60)

    print("=== Читаем значение из Redis ===")
    value = await get_value("test_key")
    print("Получили:", value)

    print("=== Удаляем значение ===")
    await delete_value("test_key")

    print("=== Проверяем после удаления ===")
    value_after_delete = await get_value("test_key")
    print("После удаления:", value_after_delete)


if __name__ == "__main__":
    asyncio.run(main())