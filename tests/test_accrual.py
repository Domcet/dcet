import asyncio
from services.accrual_service.accrual import Accrual

async def test_get_all_apartments():
    accrual = Accrual()
    apartments = await accrual._get_all_apartments()

    assert isinstance(apartments, list), "Ошибка: должен быть список квартир"
    assert len(apartments) > 0, "Ошибка: список квартир пуст"
    assert "id" in apartments[0], "Ошибка: в данных квартиры нет ID"
    assert "title" in apartments[0], "Ошибка: в данных квартиры нет названия"

async def test_run_accrual_process():
    accrual = Accrual()
    await accrual.run("Начисление за Февраль 2025")

async def run_tests():
    print("🔹 Тестируем получение квартир...")
    await test_get_all_apartments()

    print("\n🔹 Тестируем процесс начисления...")
    await test_run_accrual_process()

if __name__ == "__main__":
    asyncio.run(run_tests())
