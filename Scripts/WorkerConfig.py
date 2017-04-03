import paramiko
import os
import sys
import time
import boto3
from xml.dom import minidom
def worker_handler(event, context):
        #server, username, password = ('52.221.207.51', 'admin', 'i-0c48f0ff4f4a40366')
        S3Bucket = os.environ['S3Bucket']
        S3Prefix = os.environ['S3Prefix']
        FortinetEIP1 = os.environ['FortinetEIP1']
        FortinetEIP2 = os.environ['FortinetEIP2']
        FortinetPIP1 = os.environ['FortinetPIP1']
        FortinetPIP2 = os.environ['FortinetPIP2']
        FortinetUser = os.environ['FortinetUser']
        FortinetPass1 = os.environ['FortinetPass1']
        FortinetPass2 = os.environ['FortinetPass2']
        AutomateUserPwd = os.environ['AutomateUserPwd']
        AutomateUser = os.environ['AutomateUser']
        #------------------------------------------------------------------------------------------
        for i in [''+FortinetEIP1+':'+FortinetPass1+'', ''+FortinetEIP2+':'+FortinetPass2+'']:
              i  = (i.split(':',1))
              print "Creating user on Fortigate: " + i[0]
              #print (i[1])
              c = paramiko.SSHClient()
              c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
              c.connect(i[0], username=FortinetUser, password=i[1])
              ssh = c.invoke_shell()
              print "Connected to " + i[0]
              commands = [
                      'config system admin \n',
                      'edit '+AutomateUser+' \n',
                      'set accprofile super_admin \n',
                      'set password '+AutomateUserPwd+' \n'
                      'end \n'
                      ]
              for command in commands:
                      #print (command)
                      #print "Executing {}".format(command)
                      ssh.send(command)
              while not ssh.recv_ready():
                time.sleep(3)
              out = ssh.recv(9999)
              print(out.decode("ascii"))
        #------------------------------------------------------------------------------------------
        def tunnel0(VPNID, vpn_gateway_tunnel_outside_address_info, ipsec_dead_peer_detection_interval_info, ike_lifetime_info, customer_gateway_tunnel_outside_address_info, ipsec_lifetime_info, customer_gateway_bgp_asn_info, vpn_gateway_tunnel_inside_address_ip_address_info, vpn_gateway_bgp_asn_info):
                config1 = []
                config2 = []
                config3 = []
                config4 = []
                config5 = []
                config = []
                PIP = []
                print "Config for Tunnel0: "
                if customer_gateway_tunnel_outside_address_info[0] == FortinetEIP1:
                    pip1 = FortinetPIP1
                    PIP.append(pip1)
                    EIP  = FortinetEIP1
                    PASS = FortinetPass1
                else:
                    pip2 = FortinetPIP2
                    PIP.append(pip2)
                    EIP  = FortinetEIP2
                    PASS = FortinetPass2
                config1.append('config vpn ipsec phase1-interface \n')
                config1.append('edit  "'+VPNID+'-0" \n')
                config1.append('set interface "port1" \n')
                config1.append('set dpd enable \n')
                config1.append('set local-gw '+PIP[0]+'  \n')
                config1.append('set dhgrp 2  \n')
                config1.append('set proposal aes128-sha1 \n')
                config1.append('set keylife '+ike_lifetime_info[0]+' \n')
                config1.append('set remote-gw '+vpn_gateway_tunnel_outside_address_info[0]+'\n')
                config1.append('set psksecret '+ike_pre_shared_key_info[0]+' \n')
                config1.append('set dpd-retryinterval '+ipsec_dead_peer_detection_interval_info[0]+' \n')
                config1.append('next \n')
                config1.append('end \n')
                config2.append('config vpn ipsec phase2-interface \n')
                config2.append('edit '+VPNID+'-0 \n')
                config2.append('set phase1name "'+VPNID+'-0" \n')
                config2.append('set proposal aes128-sha1 \n')
                config2.append('set dhgrp 2 \n')
                config2.append('set pfs enable \n')
                config2.append('set keylifeseconds '+ipsec_lifetime_info[0]+' \n')
                config2.append('next \n')
                config2.append('end \n')
                config3.append('config system interface \n')
                config3.append('edit '+VPNID+'-0 \n')
                config3.append('set vdom "root" \n')
                config3.append('set ip '+customer_gateway_tunnel_inside_address_ip_address_info[0]+' 255.255.255.255 \n')
                config3.append('set allow ping \n')
                config3.append('set type tunnel \n')
                config3.append('set remote-ip '+vpn_gateway_tunnel_inside_address_ip_address_info[0]+' \n')
                config3.append('set interface "port1" \n')
                config3.append('next \n')
                config3.append('end \n')
                config4.append('config router bgp \n')
                config4.append('set as '+customer_gateway_bgp_asn_info[0]+' \n')
                config4.append('config neighbor \n')
                config4.append('edit '+vpn_gateway_tunnel_inside_address_ip_address_info[0]+' \n')
                config4.append('set remote-as '+vpn_gateway_bgp_asn_info[0]+' \n')
                config4.append('end \n')
                config4.append('end \n')
                config4.append('config route bgp \n')
                config4.append('config neighbor \n')
                config4.append('edit '+vpn_gateway_tunnel_inside_address_ip_address_info[0]+' \n')
                config4.append('set capability-default-originate enable \n')
                config4.append('end \n')
                config4.append('end \n')
                config4.append('config router bgp \n')
                config4.append('config network \n')
                config4.append('edit 1 \n')
                config4.append('set prefix 192.168.0.0 255.255.0.0 \n')
                config4.append('next \n')
                config4.append('end \n')
                config4.append('set router '+PIP[0]+' \n')
                config4.append('end \n')
                config5.append('config firewall policy \n')
                config5.append('edit 0 \n')
                config5.append('set srcintf "'+VPNID+'-0" \n')
                config5.append('set dstintf port1 \n')
                config5.append('set srcaddr all \n')
                config5.append('set dstaddr all \n')
                config5.append('set action accept \n')
                config5.append('set schedule always \n')
                config5.append('set service ALL \n')
                config5.append('next \n')
                config5.append('end \n')
                config5.append('config firewall policy \n')
                config5.append('edit 0 \n')
                config5.append('set srcintf port1 \n')
                config5.append('set dstintf "'+VPNID+'-0" \n')
                config5.append('set srcaddr all \n')
                config5.append('set dstaddr all \n')
                config5.append('set action accept \n')
                config5.append('set schedule always \n')
                config5.append('set service ALL \n')
                config5.append('next \n')
                config5.append('end \n')
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config1:
                        #print (command)
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config2:
                        #print (command)
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config3:
                        #print (command)
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config4:
                        #print (command)
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config5:
                        #print (command)
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                return;
        #------------------------------------------------------------------------------------------
        def tunnel1(VPNID, vpn_gateway_tunnel_outside_address_info, ipsec_dead_peer_detection_interval_info, ike_lifetime_info, customer_gateway_tunnel_outside_address_info, ipsec_lifetime_info, customer_gateway_bgp_asn_info, vpn_gateway_tunnel_inside_address_ip_address_info, vpn_gateway_bgp_asn_info):
                config1 = []
                config2 = []
                config3 = []
                config4 = []
                config5 = []
                config = []
                PIP = []
                print "Config for Tunnel1: "
                if customer_gateway_tunnel_outside_address_info[0] == FortinetEIP1:
                    pip1 = FortinetPIP1
                    EIP  = FortinetEIP1
                    PASS = FortinetPass1
                    PIP.append(pip1)
                else:
                    pip2 = FortinetPIP2
                    EIP = FortinetEIP2
                    PASS = FortinetPass2
                    PIP.append(pip2)
                config1.append('config vpn ipsec phase1-interface \n')
                config1.append('edit '+VPNID+'-1 \n')
                config1.append('set interface "port1" \n')
                config1.append('set dpd enable \n')
                config1.append('set local-gw '+PIP[0]+'  \n')
                config1.append('set dhgrp 2  \n')
                config1.append('set proposal aes128-sha1 \n')
                config1.append('set keylife '+ike_lifetime_info[0]+' \n')
                config1.append('set remote-gw '+vpn_gateway_tunnel_outside_address_info[1]+'\n')
                config1.append('set psksecret '+ike_pre_shared_key_info[1]+' \n')
                config1.append('set dpd-retryinterval '+ipsec_dead_peer_detection_interval_info[0]+' \n')
                config1.append('next \n')
                config1.append('end \n')
                config2.append('config vpn ipsec phase2-interface \n')
                config2.append('edit  '+VPNID+'-1 \n')
                config2.append('set phase1name "'+VPNID+'-1" \n')
                config2.append('set proposal aes128-sha1 \n')
                config2.append('set dhgrp 2 \n')
                config2.append('set pfs enable \n')
                config2.append('set keylifeseconds '+ipsec_lifetime_info[0]+' \n')
                config2.append('next \n')
                config2.append('end \n')
                config3.append('config system interface \n')
                config3.append('edit '+VPNID+'-1 \n')
                config3.append('set vdom "root" \n')
                config3.append('set ip '+customer_gateway_tunnel_inside_address_ip_address_info[1]+' 255.255.255.255 \n')
                config3.append('set allow ping \n')
                config3.append('set type tunnel \n')
                config3.append('set remote-ip '+vpn_gateway_tunnel_inside_address_ip_address_info[1]+' \n')
                config3.append('set interface "port1" \n')
                config3.append('next \n')
                config3.append('end \n')
                config4.append('config router bgp \n')
                config4.append('set as '+customer_gateway_bgp_asn_info[0]+' \n')
                config4.append('config neighbor \n')
                config4.append('edit '+vpn_gateway_tunnel_inside_address_ip_address_info[1]+' \n')
                config4.append('set remote-as '+vpn_gateway_bgp_asn_info[0]+' \n')
                config4.append('end \n')
                config4.append('end \n')
                config4.append('config route bgp \n')
                config4.append('config neighbor \n')
                config4.append('edit '+vpn_gateway_tunnel_inside_address_ip_address_info[1]+' \n')
                config4.append('set capability-default-originate enable \n')
                config4.append('end \n')
                config4.append('end \n')
                config4.append('config router bgp \n')
                config4.append('config network \n')
                config4.append('edit 1 \n')
                config4.append('set prefix 192.168.0.0 255.255.0.0 \n')
                config4.append('next \n')
                config4.append('end \n')
                config4.append('set router '+PIP[0]+' \n')
                config4.append('end \n')
                config5.append('config firewall policy \n')
                config5.append('edit 0 \n')
                config5.append('set srcintf "'+VPNID+'-1" \n')
                config5.append('set dstintf port1 \n')
                config5.append('set srcaddr all \n')
                config5.append('set dstaddr all \n')
                config5.append('set action accept \n')
                config5.append('set schedule always \n')
                config5.append('set service ALL \n')
                config5.append('next \n')
                config5.append('end \n')
                config5.append('config firewall policy \n')
                config5.append('edit 0 \n')
                config5.append('set srcintf port1 \n')
                config5.append('set dstintf "'+VPNID+'-1" \n')
                config5.append('set srcaddr all \n')
                config5.append('set dstaddr all \n')
                config5.append('set action accept \n')
                config5.append('set schedule always \n')
                config5.append('set service ALL \n')
                config5.append('next \n')
                config5.append('end \n')
                config = config1
                config = config2
                config = config3
                config = config4
                config = config5
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config1:
                        print (command)
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config2:
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config3:
                        print (command)
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config4:
                        print (command)
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                print "----------------------------------------" +EIP+"--------------"+PASS
                c = paramiko.SSHClient()
                c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                       c.connect(EIP, username=FortinetUser, password=PASS)
                except paramiko.SSHException:
                        print "Connection Failed"
                        quit()
                ssh = c.invoke_shell()
                for command in config5:
                        print (command)
                        ssh.send(command)
                while not ssh.recv_ready():
                        time.sleep(5)
                out = ssh.recv(9999)
                print(out.decode("ascii"))
                return;
        #------------------------------------------------------------------------------------------
        Processfile = []
        s3_client = boto3.client('s3')
        response = s3_client.list_objects(
                Bucket = S3Bucket,
                Prefix = S3Prefix
        )
        #-----------------------------------------------------------------------------------------------
        for file in response['Contents']:
                name = file['Key'].rsplit('/', 1)
                if name[1] != u'':
                        path = ''+S3Prefix+''+name[1]+''
                        s3_client.download_file(S3Bucket, path, '/tmp/'+name[1]+'')
                        Processfile.append('/tmp/'+name[1]+'')
        #-----------------------------------------------------------------------------------------------

        for i in Processfile:
                customer_gateway_tunnel_outside_address_info = []
                customer_gateway_tunnel_inside_address_ip_address_info = []
                customer_gateway_tunnel_inside_address_network_mask_info = []
                customer_gateway_tunnel_inside_address_network_cidr_info = []
                customer_gateway_bgp_asn_info = []
                customer_gateway_bgp_hold_time_info = []
                vpn_gateway_tunnel_outside_address_info = []
                vpn_gateway_tunnel_inside_address_ip_address_info = []
                vpn_gateway_tunnel_inside_address_network_mask_info = []
                vpn_gateway_tunnel_inside_address_network_cidr_info = []
                vpn_gateway_bgp_asn_info = []
                vpn_gateway_bgp_hold_time_info = []
                ike_authentication_protocol_info = []
                ike_encryption_protocol_info = []
                ike_lifetime_info = []
                ike_perfect_forward_secrecy_info = []
                ike_mode_info = []
                ike_pre_shared_key_info = []
                ipsec_protocol_info = []
                ipsec_authentication_protocol_info = []
                ipsec_encryption_protocol_info = []
                ipsec_lifetime_info = []
                ipsec_perfect_forward_secrecy_info = []
                ipsec_mode_info = []
                ipsec_clear_df_bit_info = []
                ipsec_fragmentation_before_encryption_info = []
                ipsec_tcp_mss_adjustment_info = []
                ipsec_dead_peer_detection_interval_info = []
                ipsec_dead_peer_detection_retries_info =  []
                xmldoc=minidom.parse(i)
                #print (xmldoc)
                vpn_connection=xmldoc.getElementsByTagName('vpn_connection')[0]
                vpn_connection_id=vpn_connection.attributes['id'].value
                customer_gateway_id=vpn_connection.getElementsByTagName("customer_gateway_id")[0].firstChild.data
                vpn_gateway_id=vpn_connection.getElementsByTagName("vpn_gateway_id")[0].firstChild.data
                vpn_connection_type=vpn_connection.getElementsByTagName("vpn_connection_type")[0].firstChild.data
                VPNID, CGWID, VGWID, VPNTYPE = (vpn_connection_id, customer_gateway_id, vpn_gateway_id, vpn_connection_type)
                print "############################################################################"
                print "Processing conf file:" +i
                print "############################################################################"
                print (VPNID, CGWID, VGWID, VPNTYPE)
                print "############################################################################"
        #-------------------------------------------------------------------------------------------
                for ipsec_tunnel in vpn_connection.getElementsByTagName("ipsec_tunnel"):
                        customer_gateway=ipsec_tunnel.getElementsByTagName("customer_gateway")[0]
                        customer_gateway_tunnel_outside_address=customer_gateway.getElementsByTagName("tunnel_outside_address")[0].getElementsByTagName("ip_address")[0].firstChild.data
                        customer_gateway_tunnel_inside_address_ip_address=customer_gateway.getElementsByTagName("tunnel_inside_address")[0].getElementsByTagName("ip_address")[0].firstChild.data
                        customer_gateway_tunnel_inside_address_network_mask=customer_gateway.getElementsByTagName("tunnel_inside_address")[0].getElementsByTagName("network_mask")[0].firstChild.data
                        customer_gateway_tunnel_inside_address_network_cidr=customer_gateway.getElementsByTagName("tunnel_inside_address")[0].getElementsByTagName("network_cidr")[0].firstChild.data
                        customer_gateway_bgp_asn=customer_gateway.getElementsByTagName("bgp")[0].getElementsByTagName("asn")[0].firstChild.data
                        customer_gateway_bgp_hold_time=customer_gateway.getElementsByTagName("bgp")[0].getElementsByTagName("hold_time")[0].firstChild.data
                        #--------------Appending the Customer Gateway Values------------------------------------
                        customer_gateway_tunnel_outside_address_info.append(customer_gateway_tunnel_outside_address)
                        customer_gateway_tunnel_inside_address_ip_address_info.append(customer_gateway_tunnel_inside_address_ip_address)
                        customer_gateway_tunnel_inside_address_network_mask_info.append(customer_gateway_tunnel_inside_address_network_mask)
                        customer_gateway_tunnel_inside_address_network_cidr_info.append(customer_gateway_tunnel_inside_address_network_cidr)
                        customer_gateway_bgp_asn_info.append(customer_gateway_bgp_asn)
                        customer_gateway_bgp_hold_time_info.append(customer_gateway_bgp_hold_time)
        #------------------------------------------------------------------------------------------
                        vpn_gateway=ipsec_tunnel.getElementsByTagName("vpn_gateway")[0]
                        vpn_gateway_tunnel_outside_address=vpn_gateway.getElementsByTagName("tunnel_outside_address")[0].getElementsByTagName("ip_address")[0].firstChild.data
                        vpn_gateway_tunnel_inside_address_ip_address=vpn_gateway.getElementsByTagName("tunnel_inside_address")[0].getElementsByTagName("ip_address")[0].firstChild.data
                        vpn_gateway_tunnel_inside_address_network_mask=vpn_gateway.getElementsByTagName("tunnel_inside_address")[0].getElementsByTagName("network_mask")[0].firstChild.data
                        vpn_gateway_tunnel_inside_address_network_cidr=vpn_gateway.getElementsByTagName("tunnel_inside_address")[0].getElementsByTagName("network_cidr")[0].firstChild.data
                        vpn_gateway_bgp_asn=vpn_gateway.getElementsByTagName("bgp")[0].getElementsByTagName("asn")[0].firstChild.data
                        vpn_gateway_bgp_hold_time=vpn_gateway.getElementsByTagName("bgp")[0].getElementsByTagName("hold_time")[0].firstChild.data
                        #--------------Appending the VPN Values------------------------------------
                        vpn_gateway_tunnel_outside_address_info.append(vpn_gateway_tunnel_outside_address)
                        vpn_gateway_tunnel_inside_address_ip_address_info.append(vpn_gateway_tunnel_inside_address_ip_address)
                        vpn_gateway_tunnel_inside_address_network_mask_info.append(vpn_gateway_tunnel_inside_address_network_mask)
                        vpn_gateway_tunnel_inside_address_network_cidr_info.append(vpn_gateway_tunnel_inside_address_network_cidr)
                        vpn_gateway_bgp_asn_info.append(vpn_gateway_bgp_asn)
                        vpn_gateway_bgp_hold_time_info.append(vpn_gateway_bgp_hold_time)
        #------------------------------------------------------------------------------------------
                        ike=ipsec_tunnel.getElementsByTagName("ike")[0]
                        ike_authentication_protocol=ike.getElementsByTagName("authentication_protocol")[0].firstChild.data
                        ike_encryption_protocol=ike.getElementsByTagName("encryption_protocol")[0].firstChild.data
                        ike_lifetime=ike.getElementsByTagName("lifetime")[0].firstChild.data
                        ike_perfect_forward_secrecy=ike.getElementsByTagName("perfect_forward_secrecy")[0].firstChild.data
                        ike_mode=ike.getElementsByTagName("mode")[0].firstChild.data
                        ike_pre_shared_key=ike.getElementsByTagName("pre_shared_key")[0].firstChild.data
                        #--------------Appending the IKE Values------------------------------------
                        ike_authentication_protocol_info.append(ike_authentication_protocol)
                        ike_encryption_protocol_info.append(ike_encryption_protocol)
                        ike_lifetime_info.append(ike_lifetime)
                        ike_perfect_forward_secrecy_info.append(ike_perfect_forward_secrecy)
                        ike_mode_info.append(ike_mode)
                        ike_pre_shared_key_info.append(ike_pre_shared_key)
        #------------------------------------------------------------------------------------------
                        ipsec=ipsec_tunnel.getElementsByTagName("ipsec")[0]
                        ipsec_protocol=ipsec.getElementsByTagName("protocol")[0].firstChild.data
                        ipsec_authentication_protocol=ipsec.getElementsByTagName("authentication_protocol")[0].firstChild.data
                        ipsec_encryption_protocol=ipsec.getElementsByTagName("encryption_protocol")[0].firstChild.data
                        ipsec_lifetime=ipsec.getElementsByTagName("lifetime")[0].firstChild.data
                        ipsec_perfect_forward_secrecy=ipsec.getElementsByTagName("perfect_forward_secrecy")[0].firstChild.data
                        ipsec_mode=ipsec.getElementsByTagName("mode")[0].firstChild.data
                        ipsec_clear_df_bit=ipsec.getElementsByTagName("clear_df_bit")[0].firstChild.data
                        ipsec_fragmentation_before_encryption=ipsec.getElementsByTagName("fragmentation_before_encryption")[0].firstChild.data
                        ipsec_tcp_mss_adjustment=ipsec.getElementsByTagName("tcp_mss_adjustment")[0].firstChild.data
                        ipsec_dead_peer_detection_interval=ipsec.getElementsByTagName("dead_peer_detection")[0].getElementsByTagName("interval")[0].firstChild.data
                        ipsec_dead_peer_detection_retries=ipsec.getElementsByTagName("dead_peer_detection")[0].getElementsByTagName("retries")[0].firstChild.data
                        #--------------Appending the IPSEC Values------------------------------------
                        ipsec_protocol_info.append(ipsec_protocol)
                        ipsec_authentication_protocol_info.append(ipsec_authentication_protocol)
                        ipsec_encryption_protocol_info.append(ipsec_authentication_protocol)
                        ipsec_lifetime_info.append(ipsec_lifetime)
                        ipsec_perfect_forward_secrecy_info.append(ipsec_mode)
                        ipsec_mode_info.append(ipsec_mode)
                        ipsec_clear_df_bit_info.append(ipsec_clear_df_bit)
                        ipsec_fragmentation_before_encryption_info.append(ipsec_fragmentation_before_encryption)
                        ipsec_tcp_mss_adjustment_info.append(ipsec_tcp_mss_adjustment)
                        ipsec_dead_peer_detection_interval_info.append(ipsec_dead_peer_detection_interval)
                        ipsec_dead_peer_detection_retries_info.append(ipsec_dead_peer_detection_retries)
        #------------------------------------------------------------------------------------------
        #               tunnel0 (VPNID, vpn_gateway_tunnel_outside_address_info, ipsec_dead_peer_detection_interval_info, ike_lifetime_info, customer_gateway_tunnel_outside_address_info, ipsec_lifetime_info, customer_gateway_bgp_asn_info, vpn_gateway_tunnel_inside_address_ip_address_info, vpn_gateway_bgp_asn_info)
                tunnel1 (VPNID, vpn_gateway_tunnel_outside_address_info, ipsec_dead_peer_detection_interval_info, ike_lifetime_info, customer_gateway_tunnel_outside_address_info, ipsec_lifetime_info, customer_gateway_bgp_asn_info, vpn_gateway_tunnel_inside_address_ip_address_info, vpn_gateway_bgp_asn_info)
                #for Tunnel in [0,1]:
                        #Config1 (VPNID, Tunnel, vpn_gateway_tunnel_outside_address_info, ipsec_dead_peer_detection_interval_info, ike_lifetime_info, customer_gateway_tunnel_outside_address_info)
                        #Config2 (VPNID, Tunnel, ipsec_lifetime_info, customer_gateway_tunnel_outside_address_info)
                        #Config3 (VPNID, Tunnel, customer_gateway_tunnel_inside_address_ip_address_info, vpn_gateway_tunnel_inside_address_ip_address_info)
                        #Config4 (customer_gateway_bgp_asn_info, vpn_gateway_tunnel_inside_address_ip_address_info, vpn_gateway_bgp_asn_info )
                        #Config5 (VPNID, Tunnel)
                #print "######################CUSTOMER_GATEWAY_INFO#################################"
                #print (customer_gateway_tunnel_outside_address_info)
                #print (customer_gateway_tunnel_inside_address_ip_address_info)
                #print (customer_gateway_tunnel_inside_address_network_mask_info)
                #print (customer_gateway_tunnel_inside_address_network_cidr_info)
                #print (customer_gateway_bgp_asn_info)
                #print (customer_gateway_bgp_hold_time_info)
                ##print "######################VPN_GATEWAY_INFO#####################################"
                ##print (vpn_gateway_tunnel_outside_address_info)
                ##print (vpn_gateway_tunnel_inside_address_ip_address_info)
                ##print (vpn_gateway_tunnel_inside_address_network_mask_info)
                ##print (vpn_gateway_tunnel_inside_address_network_cidr_info)
                ##print (vpn_gateway_bgp_asn_info)
                ##print (vpn_gateway_bgp_hold_time_info)
                ##print "######################IKE_GATEWAY_INFO####################################"
                ##print (ike_authentication_protocol_info)
                ##print (ike_encryption_protocol_info)
                ##print (ike_lifetime_info)
                ##print (ike_perfect_forward_secrecy_info)
                ##print (ike_mode_info)
                ##print (ike_pre_shared_key_info)
                ##print "######################IPSEC_INFO##########################################"
                ##print (ipsec_protocol_info)
                ##print (ipsec_authentication_protocol_info)
                ##print (ipsec_encryption_protocol_info)
                ##print (ipsec_lifetime_info)
                ##print (ipsec_perfect_forward_secrecy_info)
                ##print (ipsec_mode_info)
                ##print (ipsec_clear_df_bit_info)
                ##print (ipsec_fragmentation_before_encryption_info)
                ##print (ipsec_tcp_mss_adjustment_info)
                ##print (ipsec_dead_peer_detection_interval_info)
                ##print (ipsec_dead_peer_detection_retries_info)
        #-----------------------------------------------------------------------------------------------
        #-----------------------------------------------------------------------------------------------
        MSG = "The Configuration files to be processed: \n"
        MSG = MSG + "---------------------------------------------------------------------------------------------------- \n"
        MSG = MSG + str(Processfile)
        print (MSG)
if __name__ == '__main__':
        worker_handler('event', 'handler')