#!/usr/bin/sh

list=(`cat input`)
mpeipvs=${list[0]}
mceipvs=${list[1]}
mpe=${list[2]}
mce=${list[3]}
am=${list[4]}

# Update ntp.conf on ALL hosts (AM, MCE, MCE IPVS, MPE, MPE IPVS)
for i in $mpeipvs $mceipvs $mpe $mce $am
do
salt $i cmd.run 'echo server 10.249.53.32 >> /etc/ntp.conf'
done

# Update GATEWAY variable in eth0/eth1 in MCE, MPE, MPE IPVS)
# MCE FIRST
for i in $mce
do
salt $i cmd.run "sed -i.bak 's/GATEWAY/#GATEWAY/' /etc/sysconfig/network-scripts/ifcfg-eth1"
salt $i cmd.run "sed -i.bak2 '/^DNS1/i GATEWAY=10.165.6.1' /etc/sysconfig/network-scripts/ifcfg-eth0"
done

# Update GATEWAY variable in eth0/eth1 in MCE, MPE, MPE IPVS)
# MPE, MPE IPVS SECOND
for i in $mpeipvs $mpe
do
salt $i cmd.run "sed -i.bak 's/GATEWAY/#GATEWAY/' /etc/sysconfig/network-scripts/ifcfg-eth1"
salt $i cmd.run "sed -i.bak2 '/^DNS1/i GATEWAY=10.165.4.1' /etc/sysconfig/network-scripts/ifcfg-eth0"
done

# Copy route file to MCE, MPE, MPE IPVS
for i in $mpeipvs $mpe $mce
do
salt-cp $i route-eth1 /etc/sysconfig/network-scripts/
done

# restart network on MCE, MPE, MPE IPVS

for i in $mpeipvs $mpe $mce
do
salt $i cmd.run 'service network restart'
done

# restart ntpd on all new nodes
for i in $mpeipvs $mceipvs $mpe $mce $am
do
salt $i cmd.run 'service ntpd restart'
done

# Update rp_filter on MCE
salt $mce cmd.run 'echo 2 > /proc/sys/net/ipv4/conf/all/rp_filter'

echo **VERIFICATION**

# Verify default route on MCE, MPE, MPE IPVS
for i in $mpeipvs $mpe $mce
do
salt $i cmd.run 'netstat -nvr|grep ^0.0.0.0' --output=json|sort -u |grep v2pc
done

# Verify ntp on all new nodes
for i in $mpeipvs $mceipvs $mpe $mce $am
do
salt $i cmd.run 'ntpq -p' --output=json | grep v2pc
done

# Verify rp_filter on MCE
salt $mce cmd.run 'cat /proc/sys/net/ipv4/conf/all/rp_filter' --output=json|grep v2pc | sort -u

# Ping test all nodes
for i in $mpeipvs $mceipvs $mpe $mce $am
do
salt $i test.ping --output=json|grep v2pc
done
