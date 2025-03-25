from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from celery_service.tasks import update_apartments_task

router = APIRouter(
    prefix="/bitrix24",
    tags=["bitrix24"]
)


@router.post("/apartments")
async def update_apartments(request: Request):
    data = await request.form()
    data_dict = {key: data[key] for key in data}
    update_apartments_task.delay(data_dict)
    return JSONResponse(content={"response": "OK"}, status_code=200)


app = FastAPI()
app.include_router(router)
