
import paramiko
from xml.dom import minidom
import ast
import time
import os
import string
import logging
processfile=[]
#--------------------------------------------------------------------------------
#BucketName = 'fortinetlambda'
#PrivateKey = 'SysgainVivek.pem'
#s3 = boto3.client('s3')
#for bucket in s3.buckets.all():
#       print(bucket.name)
#s3.download_file( BucketName, PrivateKey, '/tmp/SysgainVivek.pem')
#k = paramiko.RSAKey.from_private_key_file("/tmp/SysgainVivek.pem")
#c = paramiko.SSHClient()
#c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#host=['54.254.151.128']
#print "Connecting to "
#c.connect( hostname = 'ec2-54-254-151-128.ap-southeast-1.compute.amazonaws.com', username = "ec2-user", pkey = k )
#print "Connected to "
#commands = [
#        "touch example1.txt",
#        "chmod 700 /home/ec2-user/example1.txt",
#        ]
#for command in commands:
#       stdin , stdout, stderr = c.exec_command(command)
#        print stdout.read()
#        print stderr.read()
#--------------------------------------------------------------------------------------
s3_client = boto3.client('s3')
bucket = 'vivekdemo2-s3bucket-fdc6tkp702kw'
prefix = 'VpnConfigurations/'
response = s3_client.list_objects(
    Bucket = bucket,
    Prefix = prefix
)
for file in response['Contents']:
        name = file['Key'].rsplit('/', 1)
        if name[1] != u'':
                path = ''+prefix+''+name[1]+''
                #print(path)
                s3_client.download_file(bucket, path, '/tmp/'+name[1]+'')
                processfile.append('/tmp/'+name[1]+'')
#---------------------------------------------------------------------------------------
for i in processfile:
        print (i)
        xmldoc=minidom.parseString(i.read())
        print (xmldoc)
        #vpn_connection=xmldoc.getElementsByTagName('vpn_connection')[0]
        #print (vpn_connection)
