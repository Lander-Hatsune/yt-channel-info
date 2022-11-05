import sys
import json
from apis import *
import pandas as pd

if __name__ == '__main__':
    setupYoutubeDataAPI(sys.argv[1])

    vids = searchVids(sys.argv[2])
    print(json.dumps(vids))

    channels = filterChannels(vids)
    print(json.dumps(channels))

    channel_about = []
    for channel_id in channels.keys():
        channel_about.append(getChannelAbout(channel_id))

    data = pd.DataFrame(channel_about)
    print(data)
    data.to_csv('data.csv')
