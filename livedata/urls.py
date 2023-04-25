from django.urls import path
from  .serializers import  PmuDataSerializer1,PmuDataSerializer2
from .views import PmuDataView1, PmuDataView2
from .models import PmuData



urlpatterns=[
    path('home/',PmuDataView1.as_view(), name='home'),
    path('chart/',PmuDataView2.as_view(), name='chart'),
    # path('home/',PmuDataView1.as_view(queryset=PmuData.objects.filter(channel="Channel_1").values().order_by('created_at')
    #                                   ),serializer_class=PmuDataSerializer1, name='home'),
    # path('chart/',PmuDataView2.as_view(queryset=PmuData.objects.filter(channel="Channel_1").values().order_by('created_at')
    #                                   ),serializer_class=PmuDataSerializer2, name='chart'),


]
