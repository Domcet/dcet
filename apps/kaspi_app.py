from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from sql_db.db_queries import get_apartment_by_account, get_kaspi_pay_request_by_txn_id
from services.kaspi_service.response import KaspiResponse
from celery_service.tasks import execute_kaspi_request
from dcet_tools.dcet_exceptions import BadKaspiPayRequestParams, ApartmentNotFound, ApartmentNotCreated
from dcet_tools.dcet_logging import BaseLogging

logger = BaseLogging("kaspi.log")
router = APIRouter(prefix="/kaspi", tags=["kaspi"])

def validate_params(request: Request):
    """Извлекает и проверяет параметры запроса."""
    command = request.query_params.get("command")
    account = request.query_params.get("account")
    txn_id = request.query_params.get("txn_id")
    summ = request.query_params.get("summ")
    txn_date = request.query_params.get("txn_date")
    
    if None in (command, account, txn_id, summ, txn_date):
        logger.error(BadKaspiPayRequestParams, message=str(BadKaspiPayRequestParams))
        return None
    
    return command, account, txn_id, summ, txn_date


@router.get("/")
async def kaspi_handler(request: Request):
    """Главный эндпоинт для обработки запросов КАСПИ."""
    params = validate_params(request)
    if params is None:
        logger.error(BadKaspiPayRequestParams, message=str(BadKaspiPayRequestParams))
        return JSONResponse(content=KaspiResponse(0).make_error_response())
    
    command, account, txn_id, summ, txn_date = params

    kr = KaspiResponse(txn_id)
    try:
        result = await get_apartment_by_account(personal_account=account)
        if not result:
            logger.error(ApartmentNotFound, message=str(ApartmentNotFound))
            return JSONResponse(content=kr.make_error_response(txn_id=txn_id))
        
        apartment_id, address, balance = result.apartment_id, result.title, float(result.apartment_balance)
        debt = -balance if balance else 0.0

        if command == "check":
            return JSONResponse(content=kr.make_response(txn_id=txn_id, result=0, address=address, debt=debt))

        elif command == "pay":
            existing_request = await get_kaspi_pay_request_by_txn_id(txn_id=txn_id)
            if existing_request:
                return JSONResponse(content=kr.make_response(txn_id=txn_id, result=0, address=address, debt=debt, summ=float(existing_request.summ), prv_id=existing_request.id))
            
            prv_txn_id = await execute_kaspi_request(txn_id=txn_id, account=account, date=txn_date, summ=summ, apartment_id=apartment_id, balance=balance)
            if not prv_txn_id:
                logger.error(ApartmentNotCreated, str(ApartmentNotCreated))
                return JSONResponse(content=kr.make_error_response(txn_id=txn_id))
            
            return JSONResponse(content=kr.make_response(txn_id=txn_id, result=0, address=address, debt=debt, summ=float(summ), prv_id=prv_txn_id.id))
        
        else:
            logger.error(BadKaspiPayRequestParams, str(BadKaspiPayRequestParams))
            return JSONResponse(content=kr.make_error_response(txn_id=txn_id))
    
    except Exception as ex:
        logger.error(exception=ex, message=str(ex))
        return JSONResponse(content=kr.make_error_response(txn_id=txn_id))


app = FastAPI()
app.include_router(router)
