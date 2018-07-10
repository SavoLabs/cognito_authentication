import os
import json
import boto3
import random
import re
import string
from warrant import Cognito
from six.moves.urllib.parse import parse_qs

IDENTITY_POOL_ID = os.environ['IDENTITY_POOL_ID']
USER_POOL_ID = os.environ['USER_POOL_ID']
CLIENT_ID = os.environ['CLIENT_ID']

def gen_random_string(n):
    # Use underlying /dev/urandom as a source of randomness
    s = os.urandom(n).encode('base64')
    # Filter-out some unwanted characters
    s = re.sub('[\n\r=]+', '', s)
    # Truncate to requested length (yes, some
    # cheracters are wasted ..)
    return s[:n]

def lambda_handler(event, context):
        print ("Got event \n" + json.dumps(event,indent=2))

        p_body = parse_qs(event['body'])

        #print str(p_body['user'][0])
        #print str(p_body['tenant_id'][0])
        #print str(p_body['user_id'][0])
        #print p_body['email_addr'][0]

        print event

        cognito = boto3.client('cognito-idp',region_name='us-east-2')
        if p_body['user'] != None:
            user = p_body['user'][0]
            email_add = p_body['email_addr'][0]
            t_id = p_body['tenant_id'][0]
            u_id = p_body['user_id'][0]

            passwd = gen_random_string(8)
            passwd = passwd + "!!" + str(random.randint(0,100))

            print passwd

            u = Cognito(USER_POOL_ID, CLIENT_ID)
            u.add_base_attributes(email = email_add)
            u.add_custom_attributes(tenantId=t_id, userId=u_id, lib_view = '*')
            u.register(user,passwd)

            response = cognito.admin_confirm_sign_up(UserPoolId = USER_POOL_ID,Username = user)
            u = Cognito(USER_POOL_ID,CLIENT_ID,username = user)

            u.admin_authenticate(password=passwd)
            print "getting refresh token"

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'refresh_token' : u.refresh_token})
            }
        else:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'invalid user input'})
            }
