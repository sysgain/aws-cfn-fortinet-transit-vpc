import boto3
import botocore
import paramiko
import sys
import time
import os
def main_handler(event, context):
    vpngatewayids1 = []
    vpnconnections = []
    vgwtag = []
    newvpcconnection = []
    processfilenames = []
    #-----------------------------------------------------------------------------------------------------------------------------------
    S3Bucket = os.environ['S3Bucket']
    S3Prefix = os.environ['S3Prefix']
    FortinetEIP1 = os.environ['FortinetEIP1']
    FortinetEIP2 = os.environ['FortinetEIP2']
    FortinetPIP1 = os.environ['FortinetPIP1']
    FortinetPIP2 = os.environ['FortinetPIP2']
    FortinetPass1 = os.environ['FortinetPass1']
    FortinetPass2 = os.environ['FortinetPass2']
    FortinetUser  = os.environ['FortinetUser']
    AutomateUser  = os.environ['AutomateUser']
    AutomateUserPwd = os.environ['AutomateUserPwd']
    BGP = os.environ['BGP']
    NameTag = os.environ['NameTag']
    NameValue = os.environ['NameValue']
    LambdaFunctionArn = os.environ['LambdaFunctionArn']
    #-----------------------------------------------------------------------------------------------------------------------------------
    s3 = boto3.resource('s3')
    exists = False
    try:
        s3.Object(S3Bucket, 'transitvpc.txt').load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
                exists = False
                print "-----------------------------------------------------------------------------------------------------------------------------------"
                print ("1. 'transitvpc.txt' file Doesn't Exists")
                print "-----------------------------------------------------------------------------------------------------------------------------------"
                print "1.2 Updating the 'transitvpc.txt' file in " +S3Bucket
                File = S3Bucket+'|'+S3Prefix+'|'+FortinetEIP1+'|'+FortinetEIP2+'|'+FortinetPIP1+'|'+FortinetPIP2+'|'+FortinetPass1+'|'+FortinetPass2+'|'+FortinetUser+'|'+AutomateUser+'|'+AutomateUserPwd+'|'+BGP+'|'+NameTag+'|'+NameValue+'|'+LambdaFunctionArn
                with open ('/tmp/transitvpc.txt', 'w') as f:
                        f.write(File)
                boto3.client('s3').upload_file('/tmp/transitvpc.txt', S3Bucket, 'transitvpc.txt')
                print "-----------------------------------------------------------------------------------------------------------------------------------"
                print "1.3 Updating the S3 Bucket Events to " +S3Bucket+ " & " +LambdaFunctionArn
                client = boto3.client('s3')
                response = client.put_bucket_notification_configuration(
                Bucket = S3Bucket,
                NotificationConfiguration={'LambdaFunctionConfigurations': [{'LambdaFunctionArn': LambdaFunctionArn,'Events': [ 's3:ObjectCreated:Put' ], 'Filter':{'Key':{'FilterRules':[{'Name': 'prefix', 'Value': 'Processfiles/'},{'Name': 'suffix', 'Value': '.txt'}]}}}]}
                )
                print "-----------------------------------------------------------------------------------------------------------------------------------"
                print "1.4 Creating the Automate user on FortiGate EC2 Instances"
                for i in [''+FortinetEIP1+':'+FortinetPass1+'', ''+FortinetEIP2+':'+FortinetPass2+'']:
                        i  = (i.split(':',1))
                        print "-----------------------------------------------------------------------------------------------------------------------------------"
                        print "         1.4.1 Creating user on Fortigate: " + i[0]
                        print "-----------------------------------------------------------------------------------------------------------------------------------"
                        c = paramiko.SSHClient()
                        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        c.connect(i[0], username=FortinetUser, password=i[1])
                        ssh = c.invoke_shell()
                        print "         1.4.2 Connected to " + i[0]
                        print "----------------------------------------------------------------------------------------------------------------------------------"
                        commands = [
                                'config system admin \n',
                                'edit '+AutomateUser+' \n',
                                'set accprofile super_admin \n',
                                'set password '+AutomateUserPwd+' \n'
                                'end \n'
                        ]
                        for command in commands:
                                ssh.send(command)
                        while not ssh.recv_ready():
                                time.sleep(3)
                        out = ssh.recv(9999)
                        print(out.decode("ascii"))
                print "-----------------------------------------------------------------------------------------------------------------------------------"
        else:
                raise
    else:
        exists = True
        print "----------------------------------------------------------------------------------------------------------------------------------"
        print "1. 'transitvpc.txt' files exists, process of Virtual Private Connection starts ......"
    #-----------------------------------------------------------------------------------------------------------------------------------
    client = boto3.client('ec2')
    regions = client.describe_regions()
    for r in regions['Regions']:
        srcregion = r['RegionName']
        regionclient = boto3.client('ec2', region_name=srcregion)
        vpgw1=regionclient.describe_vpn_gateways(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:'+NameTag+'','Values':[''+NameValue+'']}])
        for k in vpgw1['VpnGateways']:
                a = srcregion, k['VpnGatewayId']
                vpngatewayids1.append(a)
    #-----------------------------------------------------------------------------------------------------------------------------------
    for r in regions['Regions']:
        srcregion = r['RegionName']
        regionclient = boto3.client('ec2', region_name=srcregion)
        vpns=regionclient.describe_vpn_connections(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:'+NameTag+'','Values':[''+NameValue+'']}])
        for l in vpns['VpnConnections']:
                b = srcregion, l['VpnGatewayId']
                vpnconnections.append(b)
    #-----------------------------------------------------------------------------------------------------------------------------------
    if (len(vpnconnections)) == 0:
        newvpcconnection = vpngatewayids1
        #print (newvpcconnection)
    else:
        newvpcconnection = list(set(vpngatewayids1) - set(vpnconnections))
        print (newvpcconnection)
    #-----------------------------------------------------------------------------------------------------------------------------------
    print "-----------------------------------------------------------------------------------------------------------------------------------"
    print "2. Listing all the Vitual Priavte Gatways with  Spoke tags: [('Region', 'VirtualPriavteGatwayID')] \n" +str(vpngatewayids1)
    print "-----------------------------------------------------------------------------------------------------------------------------------"
    print "3. Listing all the Vitual Priavte Gatways with  VPN Connections: [('Region', 'VirtualPriavteGatwayID')] \n" +str(vpnconnections)
    print "-----------------------------------------------------------------------------------------------------------------------------------"
    print "4. New VPN Connection that will be created for this Virtual Private Gateway: [('Region', 'VirtualPriavteGatwayID')])] \n" +str(newvpcconnection)
    print "-----------------------------------------------------------------------------------------------------------------------------------"
    #-----------------------------------------------------------------------------------------------------------------------------------
    for n in newvpcconnection:
        nr = boto3.client('ec2', region_name=n[0])
        cg1=nr.create_customer_gateway(Type='ipsec.1',PublicIp=FortinetEIP1,BgpAsn=int(BGP))
        nr.create_tags(Resources=[cg1['CustomerGateway']['CustomerGatewayId']], Tags=[{'Key': 'Name','Value': 'Transit VPC Endpoint1' }])
        cg2=nr.create_customer_gateway(Type='ipsec.1',PublicIp=FortinetEIP2,BgpAsn=int(BGP))
        nr.create_tags(Resources=[cg2['CustomerGateway']['CustomerGatewayId']], Tags=[{'Key': 'Name','Value': 'Transit VPC Endpoint2' }])
        vpn1=nr.create_vpn_connection(Type='ipsec.1',CustomerGatewayId=cg1['CustomerGateway']['CustomerGatewayId'],VpnGatewayId=n[1],Options={'StaticRoutesOnly':False})
        nr.create_tags(Resources=[vpn1['VpnConnection']['VpnConnectionId']], Tags=[{'Key': NameTag,'Value': NameValue }])
        vpn_config1=nr.describe_vpn_connections(VpnConnectionIds=[vpn1['VpnConnection']['VpnConnectionId']])
        vpn_config1=vpn_config1['VpnConnections'][0]['CustomerGatewayConfiguration']
        s3_client = boto3.client('s3')
        s3_client.put_object(
                Body=str.encode(vpn_config1),
                Bucket=S3Bucket,
                Key=''+S3Prefix+''+n[0]+'-'+vpn1['VpnConnection']['VpnConnectionId']+'.conf',
                ACL='bucket-owner-full-control',
                #ServerSideEncryption='aws:kms',
                #SSEKMSKeyId=config['KMS_KEY']
                )
        processfilenames.append(n[0]+'-'+vpn1['VpnConnection']['VpnConnectionId']+'.conf')
        vpn2=nr.create_vpn_connection(Type='ipsec.1',CustomerGatewayId=cg2['CustomerGateway']['CustomerGatewayId'],VpnGatewayId=n[1],Options={'StaticRoutesOnly':False})
        nr.create_tags(Resources=[vpn1['VpnConnection']['VpnConnectionId']], Tags=[{'Key': NameTag,'Value': NameValue }])
        vpn_config2=nr.describe_vpn_connections(VpnConnectionIds=[vpn2['VpnConnection']['VpnConnectionId']])
        vpn_config2=vpn_config2['VpnConnections'][0]['CustomerGatewayConfiguration']
        s3_client = boto3.client('s3')
        s3_client.put_object(
                Body=str.encode(vpn_config2),
                Bucket=S3Bucket,
                Key=''+S3Prefix+''+n[0]+'-'+vpn2['VpnConnection']['VpnConnectionId']+'.conf',
                ACL='bucket-owner-full-control',
                #ServerSideEncryption='aws:kms',
                #SSEKMSKeyId=config['KMS_KEY']
                )
        processfilenames.append(n[0]+'-'+vpn2['VpnConnection']['VpnConnectionId']+'.conf')
    if len(processfilenames)==0:
        print "5. No process files available for Processing"
        print "-----------------------------------------------------------------------------------------------------------------------------------"
    else:
        print "5. Uploading the 'Fortigateconfig.txt' file to S3bucket ......"
        print "-----------------------------------------------------------------------------------------------------------------------------------"
        boto3.client('s3').put_object(
                        Body=str.encode("|".join(processfilenames)),
                        Bucket=S3Bucket,
                        Key='Processfiles/Fortigateconfig.txt',
                        ACL='bucket-owner-full-control',
                        #ServerSideEncryption='aws:kms',
                        #SSEKMSKeyId=config['KMS_KEY']
                        )
if __name__ == '__main__':
    main_handler('event', 'handler')
