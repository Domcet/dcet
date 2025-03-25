from services.kaspi_service.http_request import KaspiHttpService
from dcet_tools.exception_decorator import catch_exception
from dcet_tools.dcet_exceptions import NotValidRequest, NotValidEvent, NotBusinessProcess, NoApartmentId
from celery_service.celery_config import celery
import asyncio
from sql_db.db_queries import (
    bitrix_update_apartment_handler,
    bitrix_delete_apartment_handler,
    bitrix_create_apartment_handler,
    create_kaspi_pay_request
)
from services.bx_service.validator import BitrixRequestValidator
from services.accrual_service.accrual import Accrual


kaspi_service = KaspiHttpService()


@catch_exception("Bitrix24 Вебхук.log")
async def update_apartments(data):
    try:
        bx_value = data.get('document_id[2]', None)
        bx_request = BitrixRequestValidator().validate_bitrix_data(data)

        if bx_value:
            bx_value = str(bx_value)
            is_business_process = BitrixRequestValidator().validate_bitrix_apartment_value(bx_value)

            if is_business_process and is_business_process.get('success', None):
                apartment_id = is_business_process.get('extracted_number', None)

                if not apartment_id:
                    raise NoApartmentId("Не найден apartment_id в бизнес-процессе")

                item = await kaspi_service.get_apartment_info(entity_element_id=apartment_id)
                await bitrix_update_apartment_handler(item=item)

            else:
                raise NotBusinessProcess("Данные не относятся к бизнес-процессу")

        elif bx_request:
            event = bx_request.get('event', None)
            apartment_id = bx_request.get('id', None)

            if not apartment_id:
                raise NotValidRequest("Некорректный запрос: отсутствует apartment_id")

            if event == "ONCRMDYNAMICITEMDELETE":
                await bitrix_delete_apartment_handler(delete_id=str(apartment_id))

            elif event == "ONCRMDYNAMICITEMUPDATE":
                item = await kaspi_service.get_apartment_info(entity_element_id=apartment_id)
                await bitrix_update_apartment_handler(item=item)

            elif event == "ONCRMDYNAMICITEMADD":
                item = await kaspi_service.get_apartment_info(entity_element_id=apartment_id)
                await bitrix_create_apartment_handler(item=item)

            else:
                raise NotValidEvent(f"Неизвестное событие: {event}")

        else:
            raise NotValidRequest("Некорректный запрос: не удалось разобрать структуру")
    except Exception as ex:
        raise ex


@celery.task
def update_apartments_task(data):
    return asyncio.run(update_apartments(data))


@celery.task
def kaspi_pay_update_task(txn_id: str, account: str, date, summ, apartment_id, balance):
    return asyncio.run(
        kaspi_service.kaspi_pay_update(
            summ=summ,
            account=account,
            txn_id=txn_id,
            balance=balance,
            apartment_id=apartment_id,
            date_create=date
        )
    )


@catch_exception("kaspi.log")
async def execute_kaspi_request(txn_id: str, account: str, date, summ, apartment_id, balance):
    try:
        result = await create_kaspi_pay_request(txn_id, account, date, summ, apartment_id, balance)

        if not result:
            raise Exception("Запрос каспи не был создан в БД")

        kaspi_pay_update_task.delay(
            summ=summ,
            account=account,
            txn_id=txn_id,
            balance=balance,
            apartment_id=apartment_id,
            date=date
        )

        return result
    except Exception as ex:
        raise ex
    

@celery.task
def do_accrual_task(deal_title):
    asyncio.run(
        Accrual().run(deal_title)
    )
