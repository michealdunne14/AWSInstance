#!/usr/bin/env python3
import sys
import boto3
import time
import subprocess
import os
import webbrowser

#Main Menu 
def main():
 print("1: Create Instance")
 print("2: List Instances")
 print("3: Terminate Instance")
 print("4: Create a Bucket")
 print("5: List Buckets")
 print("6: Put file into Bucket")
 print("7: Delete a Bucket")
 print("8: Delete Bucket contents")
 print("9: Check Nginx")
 print("10:Start Nginx")
 print("11:Write File")
 print("0: Exit")
 
 selection=int(input("Enter choice: "))
 print(selection)
 if(selection == 1):
  createInstance()
  main()
 elif(selection == 2):
  listInstance()
  main()
 elif(selection == 3):
  terminateInstance()
  main()
 elif(selection == 4):
  createBuckets()
  main()
 elif(selection == 5):
  listBuckets()
  main()
 elif(selection == 6):
  putFileInBucket()
  main()
 elif(selection == 7):
  deleteBucket()
  main()
 elif(selection == 8):
  deleteBucketContents()
  main()
 elif(selection == 9):
  checknginx()
  main()
 elif(selection == 10):
  startnginx()
  main()
 elif(selection == 11):
  writeFile()
  main()
 elif(selection == 0):
  exit()
 else:
  print('This is not a an Option')
  main()

#Create an Instance for including security group and user data
def createInstance():
	ec2 = boto3.resource('ec2')
	instance = ec2.create_instances(
	   #Type of Instance
	   ImageId='ami-0c21ae4a3bd190229',
	   MinCount=1,
	   MaxCount=1,
	   #Key Pair
	   KeyName='MyKeyPair',
	   #Security Group 
	   SecurityGroupIds=[
		'sg-0c59ca1e7fe77077a'
	   ], 
	   #Commands running in instance
	   UserData='''#!/bin/bash
		       yum update -y
		       yum install python3 -y
		       amazon-linux-extras install nginx1.12 -y
		       service nginx start
		       touch /home/ec2-user/testfile''',
	   InstanceType='t2.micro'
	   )
	#Printing out The created instance 
	print ("An instance with ID", instance[0].id, "has been created.")
	time.sleep(5)
	instance[0].reload()
	print ("Public IP address:", instance[0].public_ip_address)

#List every instance in AWS
def listInstance():
	ec2 = boto3.resource('ec2')
	for instance in ec2.instances.all():
	 print (instance.id, instance.state,instance.public_ip_address)
	 print ("--------------------------")

#Delete an instance
def terminateInstance():
	ec2 = boto3.resource('ec2')
	#Listing all instances
	listInstance()
	#Prompt to enter instance to delete 
	terminate_instance = input("Please enter ID to delete :")
	instance = ec2.Instance(terminate_instance)
	response = instance.terminate()
	print (response)

#Create a bucket to store Files
def createBuckets():
	 s3 = boto3.resource("s3")
	 create = input("Please enter bucket name to create => ")
	 try:
	  #Create bucket In location eu West
	  response = s3.create_bucket(Bucket=create,CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
	  print (response)
	 except Exception as error:
	  print (error)

#List all Buckets and Contents
def listBuckets():
	 s3 = boto3.resource('s3')
	 #List bucket each bucket by name
	 for bucket in s3.buckets.all():
	    print (bucket.name)
	    print ("---")
	    #List all bucket contents
	    try:
	     for item in bucket.objects.all():
	      print ("\t%s" % item.key)
	    except Exception as error:
	      print(error)

#Put a file in the bucket 
def putFileInBucket():
	 s3 = boto3.resource("s3")
	 #Prints bucket name and puts in to file
	 for bucket in s3.buckets.all():
	  print(bucket.name)
	 bucket_name = input("Please enter bucket Name => ")
	 object_name = input("Please enter object Name => ")
	 if (bucket.name == bucket_name):
	  try:
	   #Adding file to aws bucket and makes public read
	   response = s3.Object(bucket_name, object_name).put(Body=open(object_name, 'rb'),ACL = ("public-read"))
	   print (response)
	  except Exception as error:
	   print (error)

#Delete a bucket 
def deleteBucket():
	 s3 = boto3.resource('s3')
	 for bucket in s3.buckets.all():
	    print(bucket.name)
	 #Enter bucket name to delete
	 bucket_name = input("Please enter bucket Name => ")
	 if(bucket.name == bucket_name):
	  bucket = s3.Bucket(bucket_name)
	  try:
	   response = bucket.delete()
	   print (response)
	  except Exception as error:
	   print (error)

#Delete Contents of bucket
def deleteBucketContents():
	#List Buckets
	listBuckets()
	#Deleting bucket
	s3 = boto3.resource('s3')
	bucket_name = input("Please enter bucket Name => ")
	bucket = s3.Bucket(bucket_name)
	if (bucket_name == bucket.name):
	 for key in bucket.objects.all():
	  try:
	   response = key.delete()
	   print (response)
	  except Exception as error:
	   print (error)
 

#Check if nginx is running
def checknginx():
	try:
	 #nginx command
	 cmd = 'ps -A | grep nginx'
	 #list instances 
	 listInstance()
	 #Ip address commands
	 ip_address = input("Please enter Ip address => ")
	 cmd2 = 'scp -i MyKeyPair.pem index.html ec2-user@'+ip_address+':/usr/share/nginx/html/index.html'
	 cmd3 = 'ssh -i MyKeyPair.pem ec2-user@' + ip_address + ' sudo chmod 777 /usr/share/nginx/html/index.html'
	 #Running all commands using subprocess
	 subprocess.run(cmd3,shell = True)
	 subprocess.run(cmd2,shell = True)
	 subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	 print("Nginx Server IS running")
	 #Stats
	 subprocess.call('vmstat',shell = True)
	 print("------------------------------------------------------------------")
	 #CPU Usage
	 grep = """grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage "%"}'"""
	 subprocess.run(grep,shell = True,check = True)
	 #Running the Browser
	 page = input("Would you like to launch browser (Yes/No)")
	 if(page.lower() == "yes"):
	  webbrowser.open('http://'+ ip_address +'/',new=2)
   	#Error 
	except subprocess.CalledProcessError:
	 print("Nginx Server IS NOT running")

#Start Nginx
def startnginx():
	try:
	 #Starting nginx and running it 
	 cmd = 'sudo service nginx start'
	 subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	 print("Nginx started") 
	#error
	except subprocess.CalledProcessError:
	 print("--- Error starting Nginx! ---")

#Writing A file 
def writeFile():
	#Listing all buckets and there contents
	listBuckets()
	#Enter the bucket and your object you want
	bucket_name = input("Please enter bucket_name => ")
	object_name = input("Please enter object Name => ") 
	#Opens the file of index 
	f = open('index.html','w')
	#The message to put on to HTML
	message = """<html>
	<head></head>
	<body><img src="https://s3-eu-west-1.amazonaws.com/""" + bucket_name + """/""" + object_name + """"/></body>
	</html>"""
	#Writing the File in to a new File
	f.write(message)
	f.close()

#Running main Menu 
if __name__ == '__main__':
    main()


 

 

