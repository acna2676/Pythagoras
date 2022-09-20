
import json

from crawler import Crawler


def lambda_main():

    crawler = Crawler()
    status_code = crawler.run()

    return status_code


def lambda_handler(_, __):
    status_code = 200
    message = 'Success'

    status_code = lambda_main()

    body = {
        'message': message,
    }

    return {'statusCode': status_code,
            'body': json.dumps(body),
            'headers': {'Content-Type': 'application/json'}}
