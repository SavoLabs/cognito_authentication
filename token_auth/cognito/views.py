from django.shortcuts import *
from django.http import *
from django.db import models
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import *
from warrant import Cognito
from .models import CognitoUser
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

    for Users in response['Users']:
        response2 = cognito.admin_get_user(UserPoolId=USER_POOL_ID,
                                           Username=Users['Username'])

        name = Users['Username']

        for attribute in response2['UserAttributes']:
            if attribute['Name']=='email':
                e_mail = attribute['Value']

        user = User.objects.create_user(name,e_mail, DEFAULT_PASSWORD)
        user.save()

    return render(request, 'import_users.html')

def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        print "got to post"
        uname=request.POST['username']
        password=request.POST['password']

        print username
        print password
        user = authenticate(username=uname, password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/cognito/home/')
    return render(request, 'login.html')



@login_required
def home(request):
        return render(request, 'home.html')

@login_required
def display_meta(request):
        values = request.META
        html = []
        for k in sorted(values):
            html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, values[k]))
        return HttpResponse('<table>%s</table>' % '\n'.join(html))

@login_required
def getToken(request):
    cognito = boto3.client('cognito-idp',region_name='us-east-2')
    response = cognito.list_users(UserPoolId=USER_POOL_ID,
                                     AttributesToGet=[],)
    users = []

    for Users in response['Users']:
        users.append(Users['Username'])

    return render(request, 'getToken.html',
                  {'users': users, 'idp_id': IDENTITY_POOL_ID,
                   'pool_id': USER_POOL_ID, 'client_id': CLIENT_ID})
@login_required
def returnToken(request):
    error = False
    if 'user' in request.POST:
        user = request.POST['user']
        u = Cognito(USER_POOL_ID,CLIENT_ID,username = user)

        try:
            u.admin_authenticate(password=DEFAULT_PASSWORD)
        except:
            error = True
        return render(request, 'returnToken.html',
                      {'user': user, 'r_token': u.refresh_token,
                       'error': error})

@login_required
def sign_up_form(request):
    return render(request, 'sign_up_form.html')

@login_required
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

        new_user = User.objects.create_user(user, email_add, DEFAULT_PASSWORD)


        new_user.save()
        return render(request, 'signup.html',{'user':user,
                                              'email': email_add,
                                              'r_token': u.refresh_token})



