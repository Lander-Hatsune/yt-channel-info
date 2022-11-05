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

def searchVids(prompt:str) -> list:
    '''
    Use YouTube Data API https://developers.google.com/youtube/v3
    to search videos, return result video list.
    '''
    data = youtube.search().list(
        part="snippet", maxResults=3, q=prompt).execute() # 50 is the maximum
    assert(data['kind'] == 'youtube#searchListResponse')
    ret = [{
        **vid['snippet'],
        'videoId': vid['id']['videoId'],
    } for vid in data['items']]
    return ret

def filterChannels(vids:list) -> list:
    ret = {vid['channelId']: vid['videoId'] for vid in vids}
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
    
    ret = {
        'title': about['title']['simpleText'],
        'description': about['description']['simpleText'],
        'avatar': about['avatar']['thumbnails'],
        'country': about['country']['simpleText'] if 'country' in about else None,
        'viewCount': about['viewCountText']['simpleText'],
        'joinedDate': about['joinedDateText']['runs'][1]['text'],
        'links': [{
            'title': link['title']['simpleText'],
            'link': try_redirect(link['navigationEndpoint']['urlEndpoint']['url']),
        } for link in about['primaryLinks']] if 'primaryLinks' in about else None,
        'channelId': about['channelId'],
    }
    assert(ret['channelId'] == channel_id)
    return ret
        
