import re
import json
import requests

cookies = {'CONSENT': 'YES+'}

def getChannelAbout(channel_id: str):
    url = f'https://www.youtube.com/channel/{channel_id}/about'
    pattern = re.compile(r'var ytInitialData = (.*?);</script>')
    resp = requests.get(url, cookies=cookies)
    json_text = pattern.search(resp.text).group(1)
    data = json.loads(json_text)
    about = next(tab for tab in data['contents']['tabs'] if tab.get('selected')) \
        ['content']['channelAboutFullMetadataRenderer']
        
        
session = requests.session() # for https://www.googleapis.com/youtube/v3/

if __name__ == '__main__':
    getChannelAbout('UCf5CA0OsvhhU-6AcSjT1oKQ')
