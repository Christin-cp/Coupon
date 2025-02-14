

from django.urls import path
from.import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.forms,name='forms'),
    # path('share-coupon/<str:code>/', views.share_coupon, name='share_coupon'),
    path('apply-coupon/<str:coupon_code>/', views.apply_coupon, name='apply_coupon'),
    path('generate-coupon-pdf/<str:coupon_code>/', views.generate_coupon_pdf, name='generate_coupon_pdf'),

] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

