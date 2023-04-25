from rest_framework import serializers
from .models import *

class PmuDataSerializer1(serializers.ModelSerializer):
   created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")


   class Meta:
      model = PmuData
      fields = ["created_at","mag","date", "time"]


class PmuDataSerializer2(serializers.ModelSerializer):
   created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")


   class Meta:
      model = PmuData
      fields = ["created_at","freq","date", "time","mag"]
     


