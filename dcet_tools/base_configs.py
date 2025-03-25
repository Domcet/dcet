from decouple import config
from dotenv import load_dotenv


load_dotenv()

WEBHOOK_BITRIX_URL = config('WEBHOOK_BITRIX_URL')
PIN_CODE = config('PIN_CODE')
SECRET_KEY = config('SECRET_KEY')
