import os
from fastapi import FastAPI
from dotenv import load_dotenv
from starlette.responses import RedirectResponse

from routers import channel_api, video_api

load_dotenv()
API_KEY = os.getenv('API_KEY')

app = FastAPI(title='YouTube API', version='v1.0')

app.include_router(channel_api)
app.include_router(video_api)


@app.get('/')
async def root():
    return RedirectResponse('/docs')
