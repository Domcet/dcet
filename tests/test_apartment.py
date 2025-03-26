import asyncio
from services.accrual_service.apartment import Apartment

sample_apartment = {
    "id": 49833,
    "title": "1000-1000-1000 кв",
    "ufCrm9_1684774043": -5560,  # Баланс
    "ufCrm9_1684821535720": 303,  # Тариф
    "ufCrm9_1696004188251": 327,  # Льгота
}

class MockLogger:
    def info(self, msg): print(f"[INFO] {msg}")
    def error(self, msg, exception=None): print(f"[ERROR] {msg}")

async def test_apartment_init():
    apartment = Apartment(sample_apartment, "Начисление за Февраль 2025")
    assert apartment.apartment_data == sample_apartment, "Ошибка: данные квартиры неправильные"
    assert apartment.deal_name == "Начисление за Февраль 2025", "Ошибка: название сделки неверное"

async def test_get_apartment_tariff_name():
    apartment = Apartment(sample_apartment, "Начисление за Февраль 2025")
    result = await apartment._get_apartment_tariff_name(303)
    assert result == "Базовый", f"Ошибка: неверный тариф {result}"

async def test_has_apartment_exemption():
    apartment = Apartment(sample_apartment, "Начисление за Февраль 2025")
    result = await apartment._has_apartment_exemption(sample_apartment["ufCrm9_1696004188251"])
    assert result is True, "Ошибка: неверно определена льгота"

async def test_do_sync_accrual():
    apartment = Apartment(sample_apartment, "Начисление за Февраль 2025")
    logger = MockLogger()
    new_balance = await apartment.do_sync_accrual(logger)
    assert new_balance < sample_apartment["ufCrm9_1684774043"], "Ошибка: баланс не уменьшился"

async def run_tests():
    await test_apartment_init()

    await test_get_apartment_tariff_name()

    await test_has_apartment_exemption()

    await test_do_sync_accrual()

if __name__ == "__main__":
    asyncio.run(run_tests())
