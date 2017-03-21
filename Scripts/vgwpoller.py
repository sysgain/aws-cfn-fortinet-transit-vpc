import boto3
import json
vpngatewayids1 = []
vpngatewayids2 = []
vpnconnections = []
vgwtag = []
newvpcconnection = []
EIP1 = '52.221.136.205'
BGP = 65008
client = boto3.client('ec2')
regions = client.describe_regions()
for r in regions['Regions']:
 srcregion = r['RegionName']
 regionclient = boto3.client('ec2', region_name=srcregion)
 vpgw1=regionclient.describe_vpn_gateways(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']}])
 for i in vpgw1['VpnGateways']:
  vpngid1 = i['VpnGatewayId']
  a = srcregion, i['VpnGatewayId']
  vpngatewayids1.append(a)
#-----------------------------------------------------------------------------------------------
 vpgw2=regionclient.describe_vpn_gateways(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:''transitvpc:spoke','Values':['false']}])
 for k in vpgw2['VpnGateways']:
  vpngid2 = i['VpnGatewayId']
  b = srcregion, k['VpnGatewayId']
  vpngatewayids2.append(b)
  
for y in vpngatewayids2:
  for z in vpngatewayids1:
    if y == z:
     vgwtag.append(y)
     break

#-----------------------------------------------------------------------------------------------
for r in regions['Regions']:
 srcregion = r['RegionName']
 regionclient = boto3.client('ec2', region_name=srcregion)
 vpns=regionclient.describe_vpn_connections(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:''transitvpc:spoke','Values':['false']}])
 for l in vpns['VpnConnections']:
  c = srcregion, l['VpnGatewayId']
  vpnconnections.append(c)
#----------------------------------------------------------------------------------------------
for v1 in vgwtag:
 for v2 in vpnconnections:
  if v1 != v2:
   newvpcconnection.append(v1)
   break

print (vgwtag)
print (vpnconnections)
print (newvpcconnection)
for n in newvpcconnection:
 print n[0], n[1]
 nr = boto3.client('ec2', region_name=n[0])
 cg1=nr.create_customer_gateway(Type='ipsec.1',PublicIp=EIP1,BgpAsn=BGP)
 print (cg1)
