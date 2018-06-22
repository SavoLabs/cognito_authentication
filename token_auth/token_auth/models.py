from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    pswd = models.CharField(max_length=100)
    tenant_id = models.CharField(max_length=10)
    user_id = models.CharField(max_length=20)
    lib_view = models.CharField(max_length=20)
