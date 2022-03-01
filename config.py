from typing import Union
from os import PathLike

# JWT Secret used to generate authorization tokens
JWT_SECRET: str = r"DKm%`Uq/.,Z@rL?,y/mypy,*tmME,n*veWh8LsK*Eq{VtG;\_4%F[U/`^,>v4z[("

# Database connection string relative to the messenger.core module
DB_CONNECTION_STRING: str = "sqlite+aiosqlite:///../databases/main.db"

# SSL key and certificate file paths relative to the messenger.main module
SSL_KEYFILE_PATH: Union[str, PathLike] = "..\\certs\\key.pem"
SSL_CERTFILE_PATH: Union[str, PathLike] = "..\\certs\\cert.pem"

# Host and port for the Uvicorn ASGI server
HOST: str = "0.0.0.0"
PORT: int = 8080
