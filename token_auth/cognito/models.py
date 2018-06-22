from django.db import models

class CognitoUser(models.Model):
    name = models.CharField(max_length=100)
    pswd = models.CharField(max_length=100)
    tenant_id = models.CharField(max_length=10)
    user_id = models.CharField(max_length=20)
    lib_view = models.CharField(max_length=20)

    @classmethod
    def create(cls, name, pswd, tenant_id, user_id, lib_view):
        cognito_user=cls(name=name,pswd=pswd,tenant_id=tenant_id,
                         user_id=user_id, lib_view=lib_view)
        return cognito_user
