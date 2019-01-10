from __future__ import print_function
import boto3
from botocore.exceptions import ClientError

dynamo_table = "maths_mountain_db"


def db_write_settings(response, *subset):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamo_table)

    def resolve(s0):
        l=[]
        for s1 in s0:
            if isinstance(s1, tuple) or isinstance(s1, list):
                for s2 in s1:
                    l=l+resolve([s2])
            else:
                l.append(s1)
        return l
    sub = resolve([subset])
    if sub == []:
        item={k:v for k,v in response.att.items()}
    else:
        item={k:v for k,v in response.att.items() if k in sub}

    db = table.put_item(Item=item)

    return item

def db_read_settings(response):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamo_table)

    db = table.get_item(Key={'uid': response.uid})

    item = db['Item']
    response.att.update(item)
    
    return item
