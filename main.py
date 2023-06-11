from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import add_pagination

from Docs.documentation import tags_metadata
from database import database
from api import route

app = FastAPI(
    title='Notes Taking App',
    description="This is a project to carry on all the CRUD operations required for the our main application.",
    version="0.1b",
    openapi_tags=tags_metadata,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.on_event('startup')
async def startup():
    # if not database.is_connected:
    #     await database.connect()
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    # if database.is_connected:
    #     await database.disconnect()
    await database.disconnect()


app.include_router(route.router)

add_pagination(app)
