from django.shortcuts import render
from rest_framework.response import Response
from .serializers import *
from .models import *
from rest_framework.views import APIView

class PmuDataView1(APIView):
    def get(self,request):
        pmudata = PmuData.objects.filter(channel="Channel_1").values().order_by('created_at')
       
        serializer1 =PmuDataSerializer1(pmudata,many=True) 
        return  Response(serializer1.data)

    
class PmuDataView2(APIView):
    def get(self,request):
        pmudata = PmuData.objects.filter(channel="Channel_1").values().order_by('created_at')
       
        serializer2 =PmuDataSerializer2(pmudata,many=True) 
        return  Response(serializer2.data)