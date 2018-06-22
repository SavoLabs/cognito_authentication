from django.conf.urls import url

from . import views

urlpatterns= [
    url(r'^home/$', views.home),
    url(r'^meta/$', views.display_meta),
    url(r'^sign-up-form/$', views.sign_up_form),
    url(r'^signup/$', views.signup),
    url(r'^getToken/$', views.getToken),
    url(r'^returnToken/$',views.returnToken),
]
