from django.db import models

# Create your models here.
class Mymodel(models.Model):
	studnet_file=models.FileField()
	gotomeeting_file=models.FileField()
class Final_attendance(models.Model):
	sno=models.CharField(max_length=20)
	name=models.CharField(max_length=50)
	attendance=models.CharField(max_length=10)