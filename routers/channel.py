import os

from dotenv import load_dotenv
from fastapi import Response, APIRouter
from httpx import AsyncClient
from starlette import status

load_dotenv()
API_KEY = os.getenv('API_KEY')

channel_api = APIRouter(prefix='/channel', tags=['channel'])


async def get_channel_data(channel_id):
    try:
        async with AsyncClient() as client:
            url = 'https://www.googleapis.com/youtube/v3/channels'
            data = {'part': 'statistics,brandingSettings', 'id': channel_id, 'key': API_KEY}
            r = await client.get(url, params=data)
            if r.status_code != 200:
                return False
            statistics = r.json()['items'][0]['statistics']
            branding = r.json()['items'][0]['brandingSettings']
        return {
            'title': branding['channel'].get('title'),
            'description': branding['channel'].get('description'),
            'keywords': branding['channel'].get('keywords'),
            'country': branding['channel'].get('country'),
            'bannerExternalUrl': branding['image'].get('bannerExternalUrl'),
            'unsubscribedTrailer': 'https://www.youtube.com/watch?v=' + branding['channel'].get(
                'unsubscribedTrailer') if branding['channel'].get('unsubscribedTrailer') else 'None',
            'id': channel_id,
            'url': 'https://www.youtube.com/channel/' + channel_id,
            'videoCount': statistics.get('videoCount'),
            'viewCount': statistics.get('viewCount'),
            'subscriberCount': statistics.get('subscriberCount'),
            'hiddenSubscriberCount': statistics.get('hiddenSubscriberCount')
        }
    except KeyError:
        return False


@channel_api.get('/{channel_id}', status_code=status.HTTP_200_OK)
async def get_channel(channel_id: str, response: Response):
    result = await get_channel_data(channel_id)
    if result:
        return result

    response.status_code = status.HTTP_404_NOT_FOUND
    return {'message': f'channel which belongs to this id {channel_id} is not Found !'}
