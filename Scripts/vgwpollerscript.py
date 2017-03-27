import boto3
import os
import json
def lambda_handler(event, context):
    sns = boto3.resource('sns')
    sns_endpoint = sns.PlatformEndpoint('arn:aws:sns:ap-southeast-1:650549925864:Vivek_SNS_LAMBDA')
    vpngatewayids1 = []
    vpnconnections = []
    vgwtag = []
    newvpcconnection = []
    S3Bucket = os.environ['S3Bucket']
    S3Prefix = os.environ['S3Prefix']
    FortinetEIP1 = os.environ['FortinetEIP1']
    FortinetEIP2 = os.environ['FortinetEIP2']
    FortinetPIP1 = os.environ['FortinetPIP1']
    FortinetPIP2 = os.environ['FortinetPIP2']
    BGP = int(os.environ['BGP'])
    NameTag = os.environ['NameTag']
    NameValue = os.environ['NameValue']
    client = boto3.client('ec2')
    regions = client.describe_regions()
    for r in regions['Regions']:
        srcregion = r['RegionName']
        regionclient = boto3.client('ec2', region_name=srcregion)
        vpgw1=regionclient.describe_vpn_gateways(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:'+NameTag+'','Values':[''+NameValue+'']}])
        for k in vpgw1['VpnGateways']:
                a = srcregion, k['VpnGatewayId']
                vpngatewayids1.append(a)
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    for r in regions['Regions']:
        srcregion = r['RegionName']
        regionclient = boto3.client('ec2', region_name=srcregion)
        vpns=regionclient.describe_vpn_connections(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:'+NameTag+'','Values':[''+NameValue+'']}])
        for l in vpns['VpnConnections']:
                b = srcregion, l['VpnGatewayId']
                vpnconnections.append(b)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    for v1 in vpngatewayids1:
        for v2 in vpnconnections:
                if v1 != v2:
                        newvpcconnection.append(v1)
                break

    #newvpnconnection = list(set(vpngatewayids1) - set(vpnconnections))
    #print (newvpcconnection)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
        cg1=nr.create_customer_gateway(Type='ipsec.1',PublicIp=FortinetEIP1,BgpAsn=BGP)
        nr.create_tags(Resources=[cg1['CustomerGateway']['CustomerGatewayId']], Tags=[{'Key': 'Name','Value': 'Transit VPC Endpoint1' }])
        cg2=nr.create_customer_gateway(Type='ipsec.1',PublicIp=FortinetEIP2,BgpAsn=BGP)
        nr.create_tags(Resources=[cg1['CustomerGateway']['CustomerGatewayId']], Tags=[{'Key': 'Name','Value': 'Transit VPC Endpoint1' }])
        vpn1=nr.create_vpn_connection(Type='ipsec.1',CustomerGatewayId=cg1['CustomerGateway']['CustomerGatewayId'],VpnGatewayId=n[1],Options={'StaticRoutesOnly':False})
        nr.create_tags(Resources=[vpn1['VpnConnection']['VpnConnectionId']],
            Tags=[{'Key': NameTag,'Value': NameValue }])
        vpn_config1=nr.describe_vpn_connections(VpnConnectionIds=[vpn1['VpnConnection']['VpnConnectionId']])
        vpn_config1=vpn_config1['VpnConnections'][0]['CustomerGatewayConfiguration']
        with open ('/tmp/'+vpn1['VpnConnection']['VpnConnectionId']+'.conf', 'w') as f:
             f.write(vpn_config1)
        s3_client = boto3.client('s3')
        s3_client.upload_file('/tmp/'+vpn1['VpnConnection']['VpnConnectionId']+'.conf', S3Bucket, ''+vpn1['VpnConnection']['VpnConnectionId']+'.conf')
        vpn2=nr.create_vpn_connection(Type='ipsec.1',CustomerGatewayId=cg2['CustomerGateway']['CustomerGatewayId'],VpnGatewayId=n[1],Options={'StaticRoutesOnly':False})
        nr.create_tags(Resources=[vpn1['VpnConnection']['VpnConnectionId']],
            Tags=[{'Key': NameTag,'Value': NameValue }])
        vpn_config2=nr.describe_vpn_connections(VpnConnectionIds=[vpn2['VpnConnection']['VpnConnectionId']])
        vpn_config2=vpn_config2['VpnConnections'][0]['CustomerGatewayConfiguration']
        with open ('/tmp/'+vpn2['VpnConnection']['VpnConnectionId']+'.conf', 'w') as f:
             f.write(vpn_config1)
        s3_client = boto3.client('s3')
        s3_client.upload_file('/tmp/'+vpn2['VpnConnection']['VpnConnectionId']+'.conf', S3Bucket, ''+vpn2['VpnConnection']['VpnConnectionId']+'.conf')

    response = sns_endpoint.publish(
        Message=MSG,
        Subject=' Fortinet Gateway VGWPoller Lamabda Fuction ' ,
        MessageStructure='string',)
    print (MSG)
    print (S3Bucket)
    print (S3Prefix)
    print (FortinetEIP1)
    print (FortinetEIP2)
    print (FortinetPIP1)
    print (FortinetPIP2)
    print (BGP)
    print (NameTag)
    print (NameValue)
if __name__ == '__main__':
    lambda_handler('event', 'handler')
