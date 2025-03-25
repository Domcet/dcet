from decouple import config
from dotenv import load_dotenv


load_dotenv()

DB_URL=config('DB_URL')
