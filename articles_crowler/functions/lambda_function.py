
import json

from crowler import Crowler


def lambda_main():

    crowler = Crowler()
    status_code = crowler.run()

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


if __name__ == '__main__':
    lambda_handler(None, None)
