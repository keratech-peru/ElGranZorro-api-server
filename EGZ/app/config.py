from starlette.config import Config

config = Config(".env")

SECRETE_KEY = config("SECRETE_KEY")
TOKEN_SCONDS_EXP = config("TOKEN_SCONDS_EXP")
POSTGRES_DB = config("POSTGRES_DB")
POSTGRES_USER = config("POSTGRES_USER")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
POSTGRES_SERVER = config("POSTGRES_SERVER")
USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")
SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

class ApiKey:
    USERS = config("API_KEY_USERS")

class Email:
    REMITENTE = config("EMAIL_REMITENTE")
    PASSWORD = config("EMAIL_PASSWORD")

class Whatsapp:
    URL_SEND = config("URL_SEND_WHATSAPP")

API_FOOTBALL_DATA = config("API_FOOTBALL_DATA")
KEY_FOOTBALL_DATA = config("KEY_FOOTBALL_DATA")

class MercadoPago:
    URL_GENERATE_TOKEN = config("MERCADO_PAGO_URL") + "platforms/pci/yape/v1/payment"
    URL_PAYMENT = config("MERCADO_PAGO_URL") + "v1/payments"
    ACCESS_TOKEN = config("MERCADO_PAGO_ACCESS_TOKEN")
    PUBLIC_KEY = config("MERCADO_PAGO_PUBLIC_KEY")

ADMINISTRATOR_NUMBER = config("ADMINISTRATOR_NUMBER")
URL_FRONTEND  = config("URL_FRONTEND")