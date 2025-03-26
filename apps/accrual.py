from fastapi import FastAPI, Request, Form, Body, APIRouter, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dcet_tools.base_configs import SECRET_KEY, PIN_CODE
from celery_service.tasks import do_accrual_task
import uvicorn, os
from services.accrual_service.accrual import Accrual

router = APIRouter(prefix="", tags=["accrual"])
templates = Jinja2Templates(directory="templates")
LOGS_DIR = "."
FILES_DIR = "."
task_results = {}

@router.get("/pin_code_form", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("pin_code_form.html", {"request": request})

@router.post("/pin_code_form")
async def login(request: Request, pin: str = Form(...)):
    if pin == PIN_CODE:
        request.session["authenticated"] = True
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("pin_code_form.html", {"request": request, "error": "Неверный пин-код!"})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/pin_code_form")
    
    accrual = Accrual()
    default_title = accrual.deal_name_static

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "default_title": default_title,
        "task_results": task_results
    })

@router.post("/start_task")
async def start_task(deal_name: str = Body(..., embed=True)):
    """Запускает Celery-задачу начисления"""
    accrual = Accrual()
    deal_title = deal_name if deal_name else accrual.deal_name_static

    task = do_accrual_task.delay(deal_title)
    task_results[task.id] = "В процессе..."
    return {"task_id": task.id}

@router.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request, log: str = Query(None)):
    """Просмотр логов начислений"""
    log_files = [f for f in os.listdir(LOGS_DIR) if f.endswith(".log")]
    
    log_name = None
    log_content = None
    
    if log and log in log_files:
        log_path = os.path.join(LOGS_DIR, log)
        with open(log_path, "r", encoding="utf-8") as file:
            log_name = log
            log_content = "\n".join(reversed(file.readlines()))

    return templates.TemplateResponse("logs.html", {
        "request": request, 
        "log_files": log_files,
        "log_name": log_name,
        "log_content": log_content
    })

@router.get("/view_log/{log_name}", response_class=HTMLResponse)
async def view_log(log_name: str, request: Request):
    """Просмотр содержимого .log файла"""
    log_path = os.path.join(LOGS_DIR, log_name)
    if not os.path.exists(log_path) or not log_name.endswith(".log"):
        return RedirectResponse(url="/logs")
    
    with open(log_path, "r", encoding="utf-8") as file:
        log_content = file.read()
    
    return templates.TemplateResponse("log_view.html", {"request": request, "log_name": log_name, "log_content": log_content})

@router.get("/files", response_class=HTMLResponse)
async def view_files(request: Request):
    """Просмотр файлов начислений (Excel)"""
    excel_files = [f for f in os.listdir(FILES_DIR) if f.endswith(".xlsx")]
    return templates.TemplateResponse("files.html", {"request": request, "excel_files": excel_files})

@router.get("/download/{file_name}")
async def download_file(file_name: str):
    """Скачивание Excel-файла"""
    file_path = os.path.join(FILES_DIR, file_name)
    if not os.path.exists(file_path) or not file_name.endswith(".xlsx"):
        return RedirectResponse(url="/files")
    return FileResponse(file_path, filename=file_name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

app = FastAPI()
app.include_router(router)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

if __name__ == "__main__":
    uvicorn.run("accrual:app", host="0.0.0.0", port=8000, reload=True)
