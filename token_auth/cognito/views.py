from django.shortcuts import render
from django.http import HttpResponse
from warrant import Cognito
from .models import CongnitoUser
import boto3
import datetime

#cognito = boto3.client('cognito-idp',region_name='us-east-2')

IDENTITY_POOL_ID = 'us-east-2:e2a5786c-5dc2-4025-84c8-e629568a0f32'
USER_POOL_ID = 'us-east-2_a7vE0OvG5'
CLIENT_ID = '6e1qos6n7r927dsob5mm23opdp'
DEFAULT_PASSWORD = 'Testing123!'


def import_users(request):
    cognito = boto3.client('cognito-idp',region_name='us-east-2')
    response = cognito.list_users(UserPoolId=USER_POOL_ID,AttributesToGet=[],)

def home(request):
        return render(request, 'home.html')
def display_meta(request):
        values = request.META
        html = []
        for k in sorted(values):
            html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, values[k]))
        return HttpResponse('<table>%s</table>' % '\n'.join(html))

def login_form(request):
    return render(request, 'login_form.html')

def login(request):
    error = False
    if 'user' in request.GET:
        user = request.GET['user']
        passwd = request.GET['password']

        print user
        print passwd
        u = Cognito(USER_POOL_ID,CLIENT_ID,username = user)

        try:
            u.admin_authenticate(password=passwd)
        except:
            error = True

        return render(request, 'login.html', {'error': error,
                                              'logged_in': logged_in})

def getToken(request):
    cognito = boto3.client('cognito-idp',region_name='us-east-2')
    response = cognito.list_users(UserPoolId=USER_POOL_ID,
                                     AttributesToGet=[],)
    users = []

    for Users in response['Users']:
        users.append(Users['Username'])

    return render(request, 'getToken.html',
                  {'users': users, 'idp_id': IDENTITY_POOL_ID,
                   'pool_id': USER_POOL_ID, 'client_id': CLIENT_ID,
                   'logged_in': logged_in})

def returnToken(request):
    error = False
    if 'user' in request.GET:
        user = request.GET['user']
        u = Cognito(USER_POOL_ID,CLIENT_ID,username = user)

        try:
            u.admin_authenticate(password=DEFAULT_PASSWORD)
        except:
            error = True
        return render(request, 'returnToken.html',
                      {'user': user, 'r_token': u.refresh_token,
                       'error': error, 'logged_in':logged_in})

def sign_up_form(request):
    return render(request, 'sign_up_form.html',{'logged_in': logged_in})

def signup(request):
    cognito = boto3.client('cognito-idp',region_name='us-east-2')
    if 'user' in request.GET:
        user = request.GET['user']
        email_add = request.GET['email_addr']
        t_id = request.GET['tenant_id']
        u_id = request.GET['user_id']

        u = Cognito(USER_POOL_ID, CLIENT_ID)
        u.add_base_attributes(email = email_add)
        u.add_custom_attributes(tenantId=t_id, userId=u_id, lib_view = '*')
        u.register(user,DEFAULT_PASSWORD)

        response = cognito.admin_confirm_sign_up(UserPoolId = USER_POOL_ID,
                                                 Username = user)
        u = Cognito(USER_POOL_ID,CLIENT_ID,username = user)

        u.admin_authenticate(password=DEFAULT_PASSWORD)

        new_user = CognitoUser(name=user,pswd=DEFAULT_PASSWORD,
                                               tenant_id=t_id,user_id=u_id,
                                               lib_view = '*')

        new_user.save()
        return render(request, 'signup.html',{'user':user,
                                              'email': email_add,
                                              'r_token': u.refresh_token,
                                              'logged_in': logged_in})



