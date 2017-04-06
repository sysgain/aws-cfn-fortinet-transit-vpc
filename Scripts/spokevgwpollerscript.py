import boto3
import os
import json
def lambda_handler(event, context):
    vpngatewayids1 = []
    vpnconnections = []
    vgwtag = []
    newvpcconnection = []
    #-----------------------------------------------------------------------------------------------------------------------------------
    TransitS3Bucket = os.environ['TransitS3Bucket']
    S3Bucket = []
    S3Prefix = []
    FortinetEIP1 = []
    FortinetEIP2 = []
    FortinetPIP1 = []
    FortinetPIP2 = []
    FortinetPass1 = []
    FortinetPass2 = []
    FortinetUser  = []
    AutomateUser  = []
    AutomateUserPwd = []
    BGP = []
    NameTag = []
    NameValue = []
    #-----------------------------------------------------------------------------------------------------------------------------------
    boto3.client('s3').download_file( TransitS3Bucket, 'transitvpc.txt', '/tmp/transitvpc.txt' )
    for line in open ('/tmp/transitvpc.txt', 'r'):
        value = line.split('|')
        S3Bucket = value[0]
        S3Prefix = value[1]
        FortinetEIP1 = value[2]
        FortinetEIP2 = value[3]
        FortinetPIP1 = value[4]
        FortinetPIP2 = value[5]
        FortinetPass1 = value[6]
        FortinetPass2 = value[7]
        FortinetUser = value[8]
        AutomateUser = value[9]
        AutomateUserPwd = value[10]
        BGP = value[11]
        NameTag = value[12]
        NameValue = value[13]
    #-------------------------------------------------------------------------------------------------------------------------------------
    client = boto3.client('ec2')
    regions = client.describe_regions()
    for r in regions['Regions']:
        srcregion = r['RegionName']
        regionclient = boto3.client('ec2', region_name=srcregion)
        vpgw1=regionclient.describe_vpn_gateways(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:'+NameTag+'','Values':[''+NameValue+'']}])
        for k in vpgw1['VpnGateways']:
                a = srcregion, k['VpnGatewayId']
                vpngatewayids1.append(a)
    #---------------------------------------------------------------------------------------------------------------------------------------
    for r in regions['Regions']:
        srcregion = r['RegionName']
        regionclient = boto3.client('ec2', region_name=srcregion)
        vpns=regionclient.describe_vpn_connections(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:'+NameTag+'','Values':[''+NameValue+'']}])
        for l in vpns['VpnConnections']:
                b = srcregion, l['VpnGatewayId']
                vpnconnections.append(b)
    #-------------------------------------------------------------------------------------------------------------------------------------
    if (len(vpnconnections)) == 0:
        newvpcconnection = vpngatewayids1
    else:
        newvpnconnection = set(vpnconnections).intersection(set(vpngatewayids1))
        print (newvpnconnection)
    #-------------------------------------------------------------------------------------------------------------------------------------
    MSG = "Listing all the Vitual Priavte Gatways with  Spoke tags: [('Region', 'VirtualPriavteGatwayID')] \n"
    MSG + "---------------------------------------------------------------------------------------------------- \n"
    MSG = MSG + str(vpngatewayids1)
    MSG = MSG + " \n"
    MSG + "---------------------------------------------------------------------------------------------------- \n"
    MSG = MSG + "Listing all the Vitual Priavte Gatways with  VPN Connections: [('Region', 'VirtualPriavteGatwayID')] \n"
    MSG + "---------------------------------------------------------------------------------------------------- \n"
    MSG = MSG + str(vpnconnections)
    MSG = MSG + " \n"
    MSG + "---------------------------------------------------------------------------------------------------- \n"
    MSG = MSG + "The New VPN Connection will be create for this Virtual Private Gateway: [('Region', 'VirtualPriavteGatwayID')])] \n"
    MSG + "---------------------------------------------------------------------------------------------------- \n"
    MSG = MSG + str(newvpcconnection)

    for n in newvpcconnection:
        nr = boto3.client('ec2', region_name=n[0])
        cg1=nr.create_customer_gateway(Type='ipsec.1',PublicIp=FortinetEIP1,BgpAsn=int(BGP))
        nr.create_tags(Resources=[cg1['CustomerGateway']['CustomerGatewayId']],Tags=[{'Key': 'Name','Value': 'Transit VPC Endpoint1' }])
        cg2=nr.create_customer_gateway(Type='ipsec.1',PublicIp=FortinetEIP2,BgpAsn=int(BGP))
        nr.create_tags(Resources=[cg2['CustomerGateway']['CustomerGatewayId']],Tags=[{'Key': 'Name','Value': 'Transit VPC Endpoint2' }])
        vpn1=nr.create_vpn_connection(Type='ipsec.1',CustomerGatewayId=cg1['CustomerGateway']['CustomerGatewayId'],VpnGatewayId=n[1],Options={'StaticRoutesOnly':False})
        nr.create_tags(Resources=[vpn1['VpnConnection']['VpnConnectionId']],Tags=[{'Key': NameTag,'Value': NameValue }])
        vpn_config1=nr.describe_vpn_connections(VpnConnectionIds=[vpn1['VpnConnection']['VpnConnectionId']])
        vpn_config1=vpn_config1['VpnConnections'][0]['CustomerGatewayConfiguration']
        s3_client = boto3.client('s3')
        s3_client.put_object(
              Body=str.encode(vpn_config1),
              Bucket=S3Bucket,
              Key=''+S3Prefix+''+n[0]+'-'+vpn1['VpnConnection']['VpnConnectionId']+'.conf',
              #ACL='bucket-owner-full-control',
              #ServerSideEncryption='aws:kms',
              #SSEKMSKeyId=config['KMS_KEY']
              )
        vpn2=nr.create_vpn_connection(Type='ipsec.1',CustomerGatewayId=cg2['CustomerGateway']['CustomerGatewayId'],VpnGatewayId=n[1],Options={'StaticRoutesOnly':False})
        nr.create_tags(Resources=[vpn2['VpnConnection']['VpnConnectionId']],Tags=[{'Key': NameTag,'Value': NameValue }])
        vpn_config2=nr.describe_vpn_connections(VpnConnectionIds=[vpn2['VpnConnection']['VpnConnectionId']])
        vpn_config2=vpn_config2['VpnConnections'][0]['CustomerGatewayConfiguration']
        s3_client = boto3.client('s3')
        s3_client.put_object(
              Body=str.encode(vpn_config2),
              Bucket=S3Bucket,
              Key=''+S3Prefix+''+n[0]+'-'+vpn2['VpnConnection']['VpnConnectionId']+'.conf',
              #ACL='bucket-owner-full-control',
              #ServerSideEncryption='aws:kms',
              #SSEKMSKeyId=config['KMS_KEY']
              )
    print (MSG)
if __name__ == '__main__':
    lambda_handler('event', 'handler')
