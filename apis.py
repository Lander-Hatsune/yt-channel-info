import re
import json
import urllib
import requests

# Youtube Data API
import googleapiclient.discovery
youtube = None
def setupYoutubeDataAPI(api_key: str):
    global youtube
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

def searchVids(prompt:str, num:int, kwargs: dict) -> list:
    '''
    Use YouTube Data API https://developers.google.com/youtube/v3
    to search videos, return result video list.
    '''
    pageToken = None
    ret = []
    while num > len(ret):
        data = youtube.search().list(
            part='snippet',
            type='video',
            maxResults=min(num - len(ret), 50), # 50 is the maximum
            q=prompt,
            pageToken=pageToken,
            **kwargs,
        ).execute()

        assert(data['kind'] == 'youtube#searchListResponse')
        num = min(num, data['pageInfo']['totalResults'])

        pageToken = data['nextPageToken']
        
        ret += [{
            **vid['snippet'],
            'videoId': vid['id']['videoId'],
        } for vid in data['items']]

    assert(len(ret) == num)
    return ret

def filterChannels(vids:list) -> list:
    ret = {}
    for vid in vids:
        if vid['channelId'] in ret:
            ret[vid['channelId']].append(vid['videoId'])
        else:
            ret[vid['channelId']] = [vid['videoId']]
    return ret

def getChannelAbout(channel_id:str) -> dict:
    '''
    Use requests to get 'About' page of a channel,
    return a dict of channel information.
    '''
    headers = {'Accept-Language': 'en-US'}
    cookies = {'CONSENT': 'YES+'}

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
    try_redirect = \
        lambda x: urllib.parse.unquote(link_pattern.search(x).group(1)) if \
        link_pattern.search(x) else x
    try_get_text = \
        lambda k: about[k]['simpleText'] if k in about else None
    
    ret = {
        'title': try_get_text('title'),
        'description': try_get_text('description'),
        'avatar': about['avatar']['thumbnails'],
        'country': try_get_text('country'),
        'viewCount': try_get_text('viewCountText'),
        'joinedDate': about['joinedDateText']['runs'][1]['text'],
        'links': [{
            'title': link['title']['simpleText'],
            'link': try_redirect(link['navigationEndpoint']['urlEndpoint']['url']),
        } for link in about['primaryLinks']] if 'primaryLinks' in about else None,
        'channelId': about['channelId'],
    }
    assert(ret['channelId'] == channel_id)
    return ret
        
