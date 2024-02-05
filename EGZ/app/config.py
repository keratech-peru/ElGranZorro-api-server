from starlette.config import Config

config = Config(".env")

POSTGRES_DB = config("POSTGRES_DB")
POSTGRES_USER = config("POSTGRES_USER")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
POSTGRES_SERVER = config("POSTGRES_SERVER")
POSTGRES_PORT = config("POSTGRES_PORT")
#SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
SQLALCHEMY_DATABASE_URI = f"postgresql://nick:ucVhKOTkHOzeDPYa3AlOcnK1VM3QasAK@dpg-cn02l6md3nmc73899tpg-a.oregon-postgres.render.com/egzdb"
