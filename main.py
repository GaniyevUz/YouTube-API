import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from starlette.responses import RedirectResponse

from database import engine
from models import Base
from routers import channel_api, video_api, users

load_dotenv()
API_KEY = os.getenv('API_KEY')

app = FastAPI(title='YouTube API', version='v1.0')

app.include_router(channel_api)
app.include_router(users)
app.include_router(video_api)


@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.get('/')
async def root():
    return RedirectResponse('/docs')


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=-5000)
