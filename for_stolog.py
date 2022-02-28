from flask import Flask, render_template
import requests
import json
import calendar

access_token = '{access_token}'
headers = {'Authorization': 'Bearer '+access_token}

selected_articles = []

target_year = '2021'

for month in ['1']:  # , '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:

    _, lastday = calendar.monthrange(int(target_year), int(month))
    for page in range(1, 2):
        url = 'https://qiita.com/api/v2/items?page='+str(page)+'&per_page=100&query=created%3A%3E'+target_year+'-'+month.zfill(2)+'-01+created%3A%3C'+target_year+'-' + \
            month.zfill(2)+'-'+str(lastday)+'+stocks%3A%3E500'
        response = requests.get(url, headers=headers)
        selected_articles.append(json.loads(response.text))

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='qiita legend', selected_articles=selected_articles)


if __name__ == "__main__":
    app.run(debug=True, port=8888, threaded=True)
