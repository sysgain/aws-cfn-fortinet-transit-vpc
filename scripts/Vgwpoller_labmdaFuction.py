import boto3
import json
def lambda_handler(event, context):
    sns = boto3.resource('sns')
    sns_endpoint = sns.PlatformEndpoint('arn:aws:sns:ap-southeast-1:650549925864:Vivek_SNS_LAMBDA')
    vpngatewayids1 = []
    vpnconnections = []
    vgwtag = []
    newvpcconnection = []
    EIP1 = '52.221.136.205'
    BGP = 65008
    NameTag = 'transitvpc:spoke'
    KeyTag = 'false'
    client = boto3.client('ec2')
    regions = client.describe_regions()
    for r in regions['Regions']:
        srcregion = r['RegionName']
        regionclient = boto3.client('ec2', region_name=srcregion)
        vpgw1=regionclient.describe_vpn_gateways(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:''transitvpc:spoke','Values':['false']}])
        for k in vpgw1['VpnGateways']:
                a = srcregion, k['VpnGatewayId']
                vpngatewayids1.append(a)
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    for r in regions['Regions']:
        srcregion = r['RegionName']
        regionclient = boto3.client('ec2', region_name=srcregion)
        vpns=regionclient.describe_vpn_connections(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:''transitvpc:spoke','Values':['false']}])
        for l in vpns['VpnConnections']:
                b = srcregion, l['VpnGatewayId']
                vpnconnections.append(b)
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    newvpnconnection = list(set(vpngatewayids1) - set(vpnconnections))
    print (newvpcconnection)
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
        cg1=nr.create_customer_gateway(Type='ipsec.1',PublicIp=EIP1,BgpAsn=BGP)
        nr.create_tags(Resources=[cg1['CustomerGateway']['CustomerGatewayId']], Tags=[{'Key': 'Name','Value': 'Transit VPC Endpoint1' }])
        #cg2=nr.create_customer_gateway(Type='ipsec.1',PublicIp=EIP2,BgpAsn=BGP)
        #ec2.create_tags(Resources=[cg1['CustomerGateway']['CustomerGatewayId']], Tags=[{'Key': 'Name','Value': 'Transit VPC Endpoint1' }])
        vpn1=nr.create_vpn_connection(Type='ipsec.1',CustomerGatewayId=cg1['CustomerGateway']['CustomerGatewayId'],VpnGatewayId=n[1],Options={'StaticRoutesOnly':False})
        nr.create_tags(Resources=[vpn1['VpnConnection']['VpnConnectionId']],
            Tags=[{'Key': NameTag,'Value': KeyTag }])
        #vpn2=nr.create_vpn_connection(Type='ipsec.1',CustomerGatewayId=cg1['CustomerGateway']['CustomerGatewayId'],VpnGatewayId=n[1],Options={'StaticRoutesOnly':False})

    response = sns_endpoint.publish(
        Message=MSG,
        Subject=' Fortinet Gateway VGWPoller Lamabda Fuction ' ,
        MessageStructure='string',)
    print (MSG)
if __name__ == '__main__':
    lambda_handler('event', 'handler')