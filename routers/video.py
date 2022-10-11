import asyncio
import os
from pprint import pprint

from dotenv import load_dotenv
from fastapi import Response, APIRouter
from httpx import AsyncClient
from starlette import status

from utils import humanbytes

load_dotenv()
API_KEY = os.getenv('API_KEY')

video_api = APIRouter(prefix='/video', tags=['video'])


async def get_video_data(video_id):
    try:
        async with AsyncClient() as client:
            url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics'
            data = {'id': video_id, 'key': API_KEY}
            r = await client.get(url, params=data)
            dl = f'https://onlinevideoconverter.pro/api/convert?url=https://www.youtube.com/watch?v={video_id}'
            payload = {'url': 'https://www.youtube.com/watch?v=' + video_id, 'extension': 'mp3'}
            dl_data = await client.post(dl, data=payload)

            if r.status_code != 200 or dl_data.status_code != 200:
                return False
            # d.json()['url'][9]
            video = r.json()['items'][0]
            if dl_data.status_code == 200:
                downloads = {'video': [], 'audio': []}
                for item in dl_data.json()['url']:
                    if not item['audio']:
                        downloads['video'].append(
                            {
                                'type': item.get('attr').get('title'),
                                'format': item.get('quality'),
                                'filesize': humanbytes(item.get('filesize')),
                                'url': item.get('url')
                            })
                    else:
                        downloads['audio'].append(
                            {
                                'type': item.get('attr').get('title'),
                                'format': item.get('quality'),
                                'filesize': humanbytes(item.get('filesize')),
                                'url': item.get('url')
                            })
        return {
            'title': video['snippet'].get('title'),
            'channelId': video['snippet'].get('channelId'),
            'description': video['snippet'].get('description'),
            'keywords': video['snippet'].get('keywords'),
            'publishedAt': video['snippet'].get('publishedAt').replace('T', ' ').replace('Z', ' '),
            'duration': video['contentDetails'].get('duration').replace('M', 'M ').replace('PT', ''),
            'thumbnails': video['snippet']['thumbnails']['default']['url'],
            'tags': video['snippet'].get('tags'),
            'categoryId': video['snippet'].get('categoryId'),
            'viewCount': video['statistics'].get('viewCount'),
            'likeCount': video['statistics'].get('likeCount'),
            'commentCount': video['statistics'].get('commentCount'),
            'downloads': downloads
        }
    except KeyError:
        return False


# asyncio.run(get_video_data('qAh5dDODJ5k'))


@video_api.get('/{video_api}', status_code=status.HTTP_200_OK)
async def get_video(video_api: str, response: Response):
    result = await get_video_data(video_api)
    if result:
        return result

    response.status_code = status.HTTP_404_NOT_FOUND
    return {'message': f'video which belongs to this id {video_api} is not Found !'}
