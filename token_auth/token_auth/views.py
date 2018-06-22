from django.shortcuts import render
from django.http import HttpResponse
from warrant import Cognito
import boto3
import datetime

cognito = boto3.client('cognito-idp',region_name='us-east-2')

IDENTITY_POOL_ID = 'us-east-2:e2a5786c-5dc2-4025-84c8-e629568a0f32'
USER_POOL_ID = 'us-east-2_a7vE0OvG5'
CLIENT_ID = '6e1qos6n7r927dsob5mm23opdp'
DEFAULT_PASSWORD = 'Testing123!'



def home(request):
    return render(request, 'home.html')

def display_meta(request):
        values = request.META
        html = []
        for k in sorted(values):
            html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, values[k]))
        return HttpResponse('<table>%s</table>' % '\n'.join(html))

def getToken(request):
    response = cognito.list_users(UserPoolId=USER_POOL_ID,
                                     AttributesToGet=[],)
    users = []

    for Users in response['Users']:
        users.append(Users['Username'])

    return render(request, 'getToken.html',
                  {'users': users, 'idp_id': IDENTITY_POOL_ID,
                   'pool_id': USER_POOL_ID, 'client_id': CLIENT_ID})

def returnToken(request):
    if 'user' in request.GET:
        user = request.GET['user']
        u = Cognito(USER_POOL_ID,CLIENT_ID,username = user)

        u.admin_authenticate(password=DEFAULT_PASSWORD)

        return render(request, 'returnToken.html',
                      {'user': user, 'r_token': u.refresh_token})

def sign_up_form(request):
    return render(request, 'sign_up_form.html')

def signup(request):
    if 'user' in request.GET:
        user = request.GET['user']
        email_add = request.GET['email_addr']

        u = Cognito(USER_POOL_ID, CLIENT_ID)
        u.add_base_attributes(email = email_add)
        u.register(user,DEFAULT_PASSWORD)

        response = cognito.admin_confirm_sign_up(UserPoolId = USER_POOL_ID,
                                                 Username = user)
        u = Cognito(USER_POOL_ID,CLIENT_ID,username = user)

        u.admin_authenticate(password=DEFAULT_PASSWORD)

        return render(request, 'signup.html',{'user':user,
                                              'email': email_add,
                                              'r_token': u.refresh_token})



