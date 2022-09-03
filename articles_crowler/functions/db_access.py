import os

import boto3
from boto3.dynamodb.conditions import Key

DEBUG = False
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

# DBアクセスの抽象化


class DBAccessor:
    # NOTE ファクトリにできそう

    TABLE_NAME = os.environ.get('DB_TABLE_NAME')
    print("TABLE_NAME = ", TABLE_NAME)

    def __init__(self):
        # pk = pk
        print(DBAccessor.TABLE_NAME)
        dynamodb = DBAccessor.create_db_instance()
        self.__table = dynamodb.Table(DBAccessor.TABLE_NAME)

    @staticmethod
    def create_db_instance():
        endpoint = os.environ.get('DB_ENDPOINT')
        if endpoint:
            return boto3.resource('dynamodb', endpoint_url=endpoint)
        else:
            return boto3.resource('dynamodb')

    def get_items(self, pk):

        try:
            response = self.__table.query(
                KeyConditionExpression=Key('pk').eq(pk) & Key('sk').begins_with("id_")
            )
        except Exception as e:
            print("e = ", e)
            return 500

        items = response['Items']  # [0]

        return items

    def put_item(self, items):
        try:
            self.__table.put_item(
                Item=items
            )
        except Exception as e:
            print(e)
            return 500

        return 200

    def delete_items(self, pk):
        delete_targets = self.get_items(pk)
        print("delete pk = ", pk)

        for target in delete_targets:
            keys = {
                "pk": target.get('pk'),
                "sk": target.get('sk'),
            }

            try:
                self.__table.delete_item(
                    Key=keys
                )
            except Exception as e:
                print(e)
                return 500

        return 200


# if __name__ == '__main__':
