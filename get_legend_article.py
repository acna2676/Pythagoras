import calendar
import json

import requests

# url = 'https://qiita.com'+'/api/v2/authenticated_user/items'

with open('access_token.json') as f:
    df = json.load(f)

access_token = df['access_token']
headers = {'Authorization': 'Bearer '+access_token}

for month in ['1', '2', '3', '4', '5', '6', '7', '8']:
    print('['+month+'月]')  # : ', str(len(json.loads(response.text)))+'個')

    _, lastday = calendar.monthrange(2020, int(month))
    # print(lastday)
    for page in range(1, 2):
        url = 'https://qiita.com/api/v2/items?page='+str(page)+'&per_page=100&query=created%3A%3E2020-'+month.zfill(2)+'-01+created%3A%3C2020-'+month.zfill(2)+'-'+str(lastday)+'+stocks%3A%3E500'

        response = requests.get(url, headers=headers)
        # response = requests.get(url)

        for i in range(len(json.loads(response.text))):
            likes_count = json.loads(response.text)[i]["likes_count"]
            title = json.loads(response.text)[i]["title"]
            article_url = json.loads(response.text)[i]["url"]
            print(str(i+1)+'番目', likes_count, title, article_url)
    # print(json.loads(response.text)[0]["url"])
    # print(json.loads(response.text)[0]["likes_count"])
    # print(response.text[1])
