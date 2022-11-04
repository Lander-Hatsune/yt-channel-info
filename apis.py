import re
import json
import urllib
import requests

headers = {'Accept-Language': 'en-US'}
cookies = {'CONSENT': 'YES+'}

def getChannelAbout(channel_id: str):
    url = f'https://www.youtube.com/channel/{channel_id}/about'
    pattern = re.compile(r'var ytInitialData = (.*?);</script>')
    resp = requests.get(url, headers=headers, cookies=cookies)
    json_text = pattern.search(resp.text).group(1)
    data = json.loads(json_text)

    about = next(
        tab['tabRenderer']['content'] for tab in \
        data['contents']['twoColumnBrowseResultsRenderer']['tabs'] \
        if tab['tabRenderer'].get('selected'))

    about = about['sectionListRenderer']['contents'][0] \
        ['itemSectionRenderer']['contents'][0] \
        ['channelAboutFullMetadataRenderer']

    link_pattern = re.compile(r'&q=(.*)')
    ret = {
        'title': about['title']['simpleText'],
        'description': about['description']['simpleText'],
        'avatar': about['avatar']['thumbnails'][-1]['url'],
        'country': about['country']['simpleText'],
        'viewCount': about['viewCountText']['simpleText'],
        'joinedDate': about['joinedDateText']['runs'][1]['text'],
        'links': [{
            'title': link['title']['simpleText'],
            'link': urllib.parse.unquote(link_pattern.search(
                link['navigationEndpoint']['urlEndpoint']['url']).group(1)),
        } for link in about['primaryLinks']],
        'channelId': about['channelId'],
    }
    assert(ret['channelId'] == channel_id)
    return ret
        
session = requests.session() # for https://www.googleapis.com/youtube/v3/

if __name__ == '__main__':
    channelAbout = getChannelAbout('UCf5CA0OsvhhU-6AcSjT1oKQ')
    print(channelAbout)
