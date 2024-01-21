#!/run/current-system/sw/bin/bash

HOST=$(hostname)

if [ "$HOST" == "canopus" ] || [ "$HOST" == "procyon" ] || [ "$HOST" == "spica" ]; then
	echo "This computer is a recognized Docker Swarm node"
else
	echo "This is NOT a recognized Docker Swarm node"
	exit
fi

NODES=$(sudo docker node ls)
STATUS=$(echo "$NODES"| grep $HOST | awk '{print $5}')
ACTNODES=$(echo "$NODES" | awk '{print $4}' | grep -c Active)

if [ "$ACTNODES" -ge 2 ]; then
	echo "There are enough active nodes to take on additional services"
else
	echo "There aren't enough active nodes to perform this action"
	exit
fi

if [ "$STATUS" == "Active" ]; then
	echo "This node is in the expected state, draining node"
else
	echo "This node is not in the expected state"
	exit
fi

sudo docker node update --availability drain $HOST >/dev/null

echo "Drain completed, please wait for services to be picked up by the other nodes"
