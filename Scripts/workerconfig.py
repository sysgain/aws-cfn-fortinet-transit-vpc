import boto3
import paramiko
from xml.dom import minidom
import ast
import time
import os
import string
import logging
import select
#S3Bucket = os.environ['S3Bucket']
S3Bucket='testing-s3bucket-1jujo9af55rm7'
#S3Prefix = os.environ['S3Prefix']
S3Prefix='vpnconfigurations/'
#FortinetEIP1 = os.environ['FortinetEIP1']
#FortinetEIP2 = os.environ['FortinetEIP2']
#FortinetPIP1 = os.environ['FortinetPIP1']
#FortinetPIP2 = os.environ['FortinetPIP2']
#BGP = os.environ['BGP']
processfile = []
s3_client = boto3.client('s3')
bucket = 'testing-s3bucket-1jujo9af55rm7'
prefix = 'vpnconfigrations/'
response = s3_client.list_objects(
    Bucket = bucket,
    Prefix = prefix
)
print (response)
for file in response['Contents']:
        name = file['Key'].rsplit('/', 1)
        if name[1] != u'':
                path = ''+prefix+''+name[1]+''
                #print(path)
                s3_client.download_file(bucket, path, '/tmp/'+name[1]+'')
                processfile.append('/tmp/'+name[1]+'')
#-----------------------------------------------------------------------------
BucketName = 'fortinetlambda'
PrivateKey = 'SysgainVivek.pem'
s3 = boto3.client('s3')
#for bucket in s3.buckets.all():
#       print(bucket.name)
s3.download_file( BucketName, PrivateKey, '/tmp/SysgainVivek.pem')
k = paramiko.RSAKey.from_private_key_file("/tmp/SysgainVivek.pem")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.load_system_host_keys()
c.connect( hostname = "52.74.216.91", username = "admin", pkey = k )
ssh = c.invoke_shell()
out = ssh.recv(9999)
ssh.send('config vpn ipsec phase1-interface \n')
ssh.send('edit vpn-f16fe8d8-0 \n')
ssh.send('set interface "port1" \n')
ssh.send('set local-gw 10.80.2.40 \n')
ssh.send('set dhgrp 2 \n')
ssh.send('set proposal aes128-sha1 \n')
ssh.send('set keylife 28800 \n')
ssh.send('set remote-gw 52.221.4.164 \n')
ssh.send('set psksecret HuYWVK.tmOCOh_sGAvruBu_tMsUV2Ofx \n')
ssh.send('set dpd-retryinterval 10 \n')
ssh.send('next \n')
ssh.send('end \n')
ssh.send('config vpn ipsec phase2-interface \n')
ssh.send('edit "vpn-f16fe8d8-0" \n')
ssh.send('set phase1name "vpn-f16fe8d8-0" \n ')
ssh.send('set proposal aes128-sha1 \n')
ssh.send('set dhgrp 2 \n')
ssh.send('set pfs enable \n')
ssh.send('set keylifeseconds 3600 \n')
ssh.send('next \n')
ssh.send('end \n')
ssh.send('config system interface \n')
ssh.send('edit "vpn-f16fe8d8-0" \n')
ssh.send('set vdom "root" \n')
ssh.send('set ip 169.254.30.30 255.255.255.255 \n')
ssh.send('set allowaccess ping \n')
ssh.send('set type tunnel \n')
ssh.send('set remote-ip 169.254.30.29 \n')
ssh.send('set interface "port1" \n')
ssh.send('next \n')
ssh.send('end \n')
ssh.send('config router bgp \n')
ssh.send('set as 65010 \n')
ssh.send('config neighbor \n')
ssh.send('edit 169.254.30.29 \n')
ssh.send('set remote-as 17493 \n')
ssh.send('end \n')
ssh.send('end \n')
ssh.send('config router bgp \n')
ssh.send('config neighbor \n')
ssh.send('edit 169.254.30.29 \n')
ssh.send('set capability-default-originate enable \n')
ssh.send('end \n')
ssh.send('end \n')
ssh.send('config router bgp \n')
ssh.send('config network \n')
ssh.send('edit 1 \n')
ssh.send('set prefix 192.168.0.0 255.255.0.0 \n')
ssh.send('next \n')
ssh.send('end \n')
ssh.send('set router-id 10.80.2.40 \n')
ssh.send('end \n')
ssh.send('config firewall policy \n')
ssh.send('edit 0 \n')
ssh.send('set srcintf "vpn-f16fe8d8-0" \n')
ssh.send('set dstintf port1 \n')
ssh.send('set srcaddr all \n')
ssh.send('set dstaddr all \n')
ssh.send('set action accept \n')
ssh.send('set schedule always \n')
ssh.send('set service ALL \n')
ssh.send('next \n')
ssh.send('end \n')
ssh.send('end \n')
while not ssh.recv_ready():
        time.sleep(30)
out = ssh.recv(9999)
print(out.decode("ascii"))
