from django.core.management.base import BaseCommand
# from twisted.internet import reactor
# from livedata.consumers import EchoUDP
# import pandas as pd 
import socket
from lxml import etree
import json


class Command(BaseCommand):
    help = 'import booms'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        xmlTypeConvert = lambda tag: {'Frame': int,
                              'Channels': int,
                              'Freq': float,
                              'Angle': float,
                              'ROCOF': float,
                              'Mag': float,
                              }.get(tag, lambda x: x)
        
        localIP     = "127.0.0.1"
        bufferSize  = 10240

        localPort   = 48011
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((localIP, localPort))
        while(True):
            mesg,addr = UDPServerSocket.recvfrom(bufferSize)
            mesg = mesg.decode('utf-8')
            # print("msg is",mesg )
            phasorDict = dict()
            from livedata.models import PmuData
            # parse the received data and store it in a dict
            data = etree.fromstring(mesg)

            db_data = {
                "date": data.find("Date").text,
                "time": data.find("Time").text,
                "frame": data.find("Frame").text,
            }   
            # print(list(data), '=dta')
            for i in range(int(data.find("Channels").text)):
                channel_data = {
                    "mag": data.find(f"Channel_{i}/Mag").text,
                    "angle": data.find(f"Channel_{i}/Angle").text,
                    "freq": data.find(f"Channel_{i}/Freq").text,
                    "rocof": data.find(f"Channel_{i}/ROCOF").text,
                    "channel":  f"Channel_{i}",
                     }
                PmuData.objects.create(**{**db_data, **channel_data})
           