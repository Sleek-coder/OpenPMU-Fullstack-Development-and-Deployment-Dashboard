from django.db import models

# Create your models here.
class PmuData(models.Model):
    date = models.CharField(max_length=200,blank=True, null=True)
    time = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    frame = models.CharField(max_length=200,null=True, blank=True)
    mag = models.FloatField(max_length=200, null=True, blank=True)
    angle = models.FloatField(max_length=200, null=True, blank=True)
    freq = models.FloatField(max_length = 500, null=True, blank=True)
    rocof = models.FloatField(max_length = 500, null=True, blank=True)
    channel = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        db_table = 'synchrophasor_data'
    
    def __str__(self):
        return f"{str(self.time)}--{self.date}--{self.frame}"
    
  