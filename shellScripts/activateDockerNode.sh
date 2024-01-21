#!/run/current-system/sw/bin/bash

HOST=$(hostname)

if [ "$HOST" == "canopus" ] || [ "$HOST" == "procyon" ] || [ "$HOST" == "spica" ]; then
	echo "This computer is a recognized Docker Swarm node"
else
	echo "This is NOT a recognized Docker Swarm node"
	exit
fi

STATUS=$(sudo docker node ls | grep $HOST | awk '{print $5}')

if [ "$STATUS" == "Drain" ]; then
	echo "This node is in the expected state, activating node"
else
	echo "This node is not in the expected state"
	exit
fi

sudo docker node update --availability active $HOST >/dev/null

echo "Activation completed, please wait for services to be moved on to this node"
