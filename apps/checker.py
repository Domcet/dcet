from fastapi import FastAPI, Form, Request, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi_pagination import paginate, add_pagination, Params
from typing import Optional
from sql_db.tables import BitrixApartment, UserCheckRequest, PageVisit
from sql_db.context_manager import AsyncDatabaseManager
from fastapi.templating import Jinja2Templates
import uvicorn
from datetime import timedelta
from dcet_tools.base_configs import PIN_CODE, SECRET_KEY


router = APIRouter(prefix="", tags=["checker"])


@router.post("/check/", response_class=HTMLResponse)
@router.get("/check/", response_class=HTMLResponse)
async def apartment_details_form(request: Request,
                                 microdistrict: Optional[str] = Form(None),
                                 house: Optional[str] = Form(None),
                                 apartment: Optional[str] = Form(None)):
    context = {"request": request}

    try:
        db = AsyncDatabaseManager()
        client_ip = request.client.host  

        existing_visit = await db.fetch_one(PageVisit, PageVisit.ip_address == client_ip)

        if not existing_visit:
            await db.create(PageVisit, path="/check/", ip_address=client_ip)

        if request.method == "POST":
            if not (microdistrict and house and apartment):
                context["error"] = "Все поля обязательны для заполнения."
                return templates.TemplateResponse("apartment_details_form.html", context)

            apartment_instance = await db.fetch_one(
                BitrixApartment,
                (BitrixApartment.microdistrict == microdistrict) &
                (BitrixApartment.house == house) &
                (BitrixApartment.apartment == apartment)
            )

            if apartment_instance:
                context["apartment_balance"] = apartment_instance.apartment_balance
                context["personal_account"] = apartment_instance.personal_account
                context["title"] = apartment_instance.title

                existing_request = await db.fetch_one(
                    UserCheckRequest,
                    UserCheckRequest.ip_address == client_ip
                )

                if not existing_request:
                    await db.create(UserCheckRequest, **{
                        "address": str(apartment_instance.title),
                        "ip_address": client_ip
                    })
            else:
                context["error"] = "Квартира с такими данными не найдена."

    except Exception as e:
        context["error"] = f"Ошибка: {str(e)}"

    return templates.TemplateResponse("apartment_details_form.html", context)


@router.get("/statistics/")
async def get_statistics():
    db = AsyncDatabaseManager()
    count = len(await db.fetch_all(PageVisit, PageVisit.path == "/check/"))
    return {"Количество запросов": count}


@router.get("/requests/", response_class=HTMLResponse)
@router.post("/requests/", response_class=HTMLResponse)
async def get_requests(request: Request, pin: Optional[str] = Form(None), params: Params = Depends()):
    context = {"request": request, "params": params} 

    if not request.session.get("pin_verified"):
        if request.method == "POST":
            if pin == PIN_CODE:
                request.session["pin_verified"] = True
                return RedirectResponse(url="/requests/", status_code=302)
            else:
                context["error"] = "Неверный пин-код!"
                return templates.TemplateResponse("pin_code_form.html", context)
        return templates.TemplateResponse("pin_code_form.html", context)

    db = AsyncDatabaseManager()
    requests_list = await db.fetch_all(UserCheckRequest, filter_by=True)

    for req in requests_list:
        if req.timestamp:
            local_time = req.timestamp + timedelta(hours=5)
            req.timestamp = local_time.strftime("%d.%m.%Y %H:%M:%S")
        else:
            req.timestamp = "Неизвестно"

    page_obj = paginate(requests_list, params)
    return templates.TemplateResponse("requests_list.html", {
        "request": request,
        "page_obj": page_obj,
        "params": params  
    })

app = FastAPI()
app.include_router(router)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

add_pagination(app)

if __name__ == "__main__":
    uvicorn.run("checker:app", host="0.0.0.0", port=8000, reload=True)
