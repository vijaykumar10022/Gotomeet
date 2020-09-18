from django.shortcuts import render
from Student_attendance.models import Mymodel,Final_attendance
from django.http import HttpResponse
from Student_attendance.attendance import *
import pandas as pd
import csv
import os
# Create your views here.
def uploadfile(request):
	if request.method=="POST":
		file1=request.FILES['file1']
		file2=request.FILES['file2']
		Mymodel.objects.create(studnet_file=file1,gotomeeting_file=file2)
		studentsData = "Student_attendance/static/files/StudentsData.csv"
		master = csv_data(studentsData)
		master['Roll Number'] = rollNumber_upper(master['Roll Number'])
		goToMeetingAttendanceFile = "Student_attendance/static/files/GotoMeetingData.xls"
		today = excel(goToMeetingAttendanceFile)
		today['Name'] = rollNumber_upper(today['Name'])
		today = today.groupby('Name').sum().reset_index()
		req_time = filterdf(today, 90)
		result = split_name(req_time['Name'], '-')
		result = split_name(result, ' ')
		result = split_name(result, '_')
		FinalRollNumbers = split_name(result, ',')
		FinalRollNumbers = remove_trainers(FinalRollNumbers)
		FinalRollNumbers = list(set(FinalRollNumbers))
		req = []
		for num in FinalRollNumbers:
			if num.isalnum():
				req.append(num)
			else:
				print(num)
		outputfile = "result"
		FinalRollNumbers = req.copy()
		FinalStudentAttendees = pd.DataFrame(FinalRollNumbers, columns=['Roll Number'])
		FinalStudentAttendees[outputfile] = ['P' for i in range(len(FinalRollNumbers))]
		FinalStudentAttendees = pd.merge(master, FinalStudentAttendees, how = 'left', on = 'Roll Number')
		FinalStudentAttendees[outputfile].value_counts()
		Unknown = pd.merge(master, FinalStudentAttendees, how = 'right', on = 'Roll Number').tail(10)
		FinalStudentAttendees.fillna('A', inplace=True)
		print(FinalStudentAttendees)
		# FinalStudentAttendees.to_excel(outputfile +'.xlsx', sheet_name=outputfile)
		for i in FinalStudentAttendees.values:
			Final_attendance.objects.create(sno=i[0],name=i[1],attendance=i[2])
		f_d=Final_attendance.objects.all()
		p=0
		a=0
		for i in f_d:
			if i.attendance=="P":
				p+=1
			elif i.attendance=="A":
				a+=1
			else:
				print("Nothing")
		print(p,a)
		mydata=[]
		for i in f_d:
			l=[]
			l.append(i.sno)
			l.append(i.name)
			l.append(i.attendance)
			mydata.append(tuple(l))
		with open('Student_attendance/static/files/myfile.csv', 'w') as csvfile:
			csvwriter = csv.writer(csvfile)
			csvwriter.writerow(['RollNumber', 'Name', 'attendance'])
			csvwriter.writerows(mydata)
		return render(request,'app1/result.html',{'data':f_d,"P":p,"A":a,"Total":a+p})
	try:
		data=Mymodel.objects.all()[:2]
		for i in data:
			filepath="Student_attendance/static/files/{}".format(i.studnet_file)
			os.remove(filepath)
			filepath="Student_attendance/static/files/{}".format(i.gotomeeting_file)
			os.remove(filepath)
		Mymodel.objects.last().delete()
		Final_attendance.objects.all().delete()
		return render(request,'app1/uploadfile.html')
	except:
		Final_attendance.objects.all().delete()
		return render(request,'app1/uploadfile.html')
def myref(request):
	data=pd.read_excel('./result.xlsx', index_col=None, header=None) 
	print(data)
	return HttpResponse(data)