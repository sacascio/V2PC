#!/usr/bin/sh
for i in `cat mcelist`
do
salt "*$i*" cmd.run "cp /etc/td-agent/td-agent.conf /etc/td-agent/td-agent.conf.08262019"
salt "*$i*" cmd.run "cp /etc/td-agent/td-agent.conf.v2pc /etc/td-agent/td-agent.conf.v2pc.08262019"
salt-cp "*$i*" td-agent.conf.mce /etc/td-agent/td-agent.conf
salt-cp "*$i*" td-agent.conf.mce /etc/td-agent/td-agent.conf.v2pc
salt "*$i*" cmd.run "service td-agent restart"
done
