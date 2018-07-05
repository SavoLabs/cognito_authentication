import json
import boto3
from warrant import Cognito

IDENTITY_POOL_ID = 'us-east-2:e2a5786c-5dc2-4025-84c8-e629568a0f32'
USER_POOL_ID = 'us-east-2_a7vE0OvG5'
CLIENT_ID = '6e1qos6n7r927dsob5mm23opdp'
DEFAULT_PASSWORD = 'Testing123!'

def lambda_handler(event, context):
        print ("Got event \n" + json.dumps(event,indent=2))

        cognito = boto3.client('cognito-idp',region_name='us-east-2')
        if event['user'] != None:
            user = event['user']
            email_add = event['email']
            t_id = event['tenant']
            u_id = event['user_id']

            u = Cognito(USER_POOL_ID, CLIENT_ID)
            u.add_base_attributes(email = email_add)
            u.add_custom_attributes(tenantId=t_id, userId=u_id, lib_view = '*')
            u.register(user,DEFAULT_PASSWORD)

            response = cognito.admin_confirm_sign_up(UserPoolId = USER_POOL_ID,Username = user)
            u = Cognito(USER_POOL_ID,CLIENT_ID,username = user)

            u.admin_authenticate(password=DEFAULT_PASSWORD)
            print "getting refresh token"

            return u.refresh_token
