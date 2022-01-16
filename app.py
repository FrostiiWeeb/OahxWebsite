from aiohttp import client
from aiohttp.client import request
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse, HTMLResponse
import uvicorn, asyncpg
import asyncio, aiohttp
import string
from datetime import datetime, timedelta
from typing import Optional
import random
import aioredis
import uvicorn
from discord.ext import ipc
import asyncrd, json
from fastapi import Depends, FastAPI

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import FastAPI
import uvloop
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi_asyncpg import configure_asyncpg
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from fastapi.staticfiles import StaticFiles
from fastapi_contrib.auth.backends import AuthBackend
from fastapi_contrib.auth.middlewares import AuthenticationMiddleware

from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse
from fastapi import Depends, FastAPI

from fastapi.templating import Jinja2Templates

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)

API_KEY_NAME = "Authorization"
COOKIE_DOMAIN = "repi.openrobot.xyz"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

app = FastAPI(
    title="Oahx",
    swagger_static={"favicon": "favicon.ico"},
    description="A multipurpose bot with alot of new coming features.",
    version="beta",
    docs_url="/try",
    redoc_url=None,
)

app.mount("/website/assets", StaticFiles(directory="./website/assets"), name="assets")
app.mount("/website/js", StaticFiles(directory="./website/js"), name="js")
app.mount("/website/css", StaticFiles(directory="./website/css"), name="css")
ipc_client = ipc.Client(secret_key="my_secret_key", port=7870, multicast_port=28900)  # secret_key must be the same as your server


templates = Jinja2Templates(directory="website")


async def request_logger(request: Request):
    WEBHOOK_URL = "https://discord.com/api/webhooks/932214312620159066/l4A0q7GdovXW7kXhY1C3y8DlsBK699D_oOgg4f_txGu6jXy3GJw9jHmPOZvAAYqdHcqo"
    client_host = request.client.host
    content = "%s %s" % (request.method, request.url.path)
    data = {"content": f"NEW REQUEST: {content} {client_host}"}
    session = aiohttp.ClientSession()
    await session.post(WEBHOOK_URL, json=data)
    await session.close()


@app.on_event("startup")
async def startup():
    app.db = await asyncpg.create_pool(
        dsn="postgres://xxhhlapgszttrj:10096a300ff61f58f7b6d85c32d7de075be761a5380731c15dedfae788fc9bd5@ec2-108-128-104-50.eu-west-1.compute.amazonaws.com:5432/dr9vebh5nv6tp"
    )
    app.redis = await asyncrd.connect("redis://localhost:7000")


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/docs", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title,
        redoc_js_url="/static/redoc.standalone.js",
    )

@app.get("/")
async def home(request: Request):
	guild_count = await ipc_client.request(
        "get_guild_count"
    )  # get the guild count
	guild_count = str(guild_count)
	user_count = await ipc_client.request(
        "get_user_count"
    )  # get the guild count
	user_count = str(user_count)	
	channel_count = await ipc_client.request(
        "get_channel_count"
    )  # get the guild count
	channel_count = str(channel_count)
	return templates.TemplateResponse("index.html", {"request": request, "guild_count": guild_count, "user_count": user_count, "channel_count": channel_count})


if __name__ == "__main__":
    uvicorn.run(host="localhost", port=9000, app="app:app", loop="uvloop", reload=True)
