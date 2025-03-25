from services.bx_service.executor import ApartmentDataExecutor
from dcet_tools.dcet_exceptions import NoApartmentItem, NoApartmentDeleteId, NoPersonalAccount, NoTxnId, BadKaspiPayRequestParams
from sql_db.context_manager import AsyncDatabaseManager
from sql_db.tables import BitrixApartment, KaspiPayRequest
from sqlalchemy.exc import NoResultFound
from services.kaspi_service.date_time import make_normal_datetime

async def bitrix_delete_apartment_handler(delete_id: str = None):
    if delete_id:
        try:
            await AsyncDatabaseManager().delete(BitrixApartment, BitrixApartment.apartment_id == delete_id)
        except Exception as ex:
            raise ex
    else:
        raise NoApartmentDeleteId


async def bitrix_create_apartment_handler(item: dict = None):
    if item:
        apartment_id, apartment_fields = ApartmentDataExecutor(item=item).execute_data()
        try:
            await AsyncDatabaseManager().create(BitrixApartment, **apartment_fields)
        except Exception as ex:
            raise ex   
    else:
        NoApartmentItem


async def bitrix_update_apartment_handler(item: dict = None):
    if item:
        apartment_id, apartment_fields = ApartmentDataExecutor(item=item).execute_data()
        try:
            await AsyncDatabaseManager().update(BitrixApartment, BitrixApartment.apartment_id == apartment_id, **apartment_fields)
        except NoResultFound:
            await bitrix_create_apartment_handler(item=item)
        except Exception as ex:
            raise ex

    else:
        raise NoApartmentItem


async def get_apartment_by_account(personal_account: str):
    if personal_account:
        try:
            data = await AsyncDatabaseManager().fetch_one(BitrixApartment, filter_by=(BitrixApartment.personal_account == str(personal_account)))
            return data
        
        except Exception as ex:
            raise ex

    else:
        raise NoPersonalAccount


async def get_kaspi_pay_request_by_txn_id(txn_id: str):
    if txn_id:
        try:
            data = await AsyncDatabaseManager().fetch_one(KaspiPayRequest, filter_by=(KaspiPayRequest.txn_id == str(txn_id)))
            return data if data else None
        
        except Exception as ex:
            raise ex

    else:
        raise NoTxnId
    

async def create_kaspi_pay_request(txn_id: str, account: str, date, summ, apartment_id, balance):
    normal_date = make_normal_datetime(date)

    params={
        'txn_id': txn_id,
        'account': account,
        'date': normal_date,
        'summ': summ
    }
    for param in params.values():
        if not param:
            raise BadKaspiPayRequestParams
    try:
        result = await AsyncDatabaseManager().create(KaspiPayRequest, **params)
        return result
    except Exception as ex:
        raise ex
    