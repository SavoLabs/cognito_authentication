from django import forms
from warrant import Cognito
import boto3


cognito = boto3.client('cognito-idp',region_name='us-east-2')
IDENTITY_POOL_ID = 'us-east-2:e2a5786c-5dc2-4025-84c8-e629568a0f32'
USER_POOL_ID = 'us-east-2_a7vE0OvG5'
CLIENT_ID = '6e1qos6n7r927dsob5mm23opdp'

response = cognito.list_users(UserPoolId=USER_POOL_ID, AttributesToGet=[],)

users = []

for Users in response['Users']:
    users.append(Users['Username'])

class UserListForm(forms.Form):
    user_dropdown = forms.ChoiceField(choices=users)
