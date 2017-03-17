import boto3
import json
vpngatewayids1 = []
vpngatewayids2 = []
vpnconnections = []
vgwtag = []
client = boto3.client('ec2')
regions = client.describe_regions()
for r in regions['Regions']:
 srcregion = r['RegionName']
 regionclient = boto3.client('ec2', region_name=srcregion)
#print (srcregion)
 vpgw1=regionclient.describe_vpn_gateways(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']}])
 for i in vpgw1['VpnGateways']:
  vpngid1 = i['VpnGatewayId']
  a = srcregion, i['VpnGatewayId']
  vpngatewayids1.append(a)
#-----------------------------------------------------------------------------------------------
 vpgw2=regionclient.describe_vpn_gateways(Filters=[{'Name':'state','Values':['available', 'attached', 'detached']},{'Name':'tag:''transitvpc:spoke','Values':['false']}])
 for k in vpgw2['VpnGateways']:
  vpngid2 = i['VpnGatewayId']
  c = srcregion, k['VpnGatewayId']
  vpngatewayids2.append(c)

#print (vpngatewayids2)
for y in vpngatewayids2:
  for z in vpngatewayids1:
    if y == z:
     vgwtag.append(y)
     break
print (vgwtag)
