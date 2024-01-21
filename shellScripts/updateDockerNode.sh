#!/run/current-system/sw/bin/bash

HOST=$(hostname)

if [ "$HOST" == "canopus" ] || [ "$HOST" == "procyon" ] || [ "$HOST" == "spica" ]; then
	echo "This computer is a recognized Docker Swarm node"
else
	echo "This is NOT a recognized Docker Swarm node"
	exit
fi

NODES=$(sudo docker node ls)
STATUS=$(echo "$NODES"| grep $HOST | awk '{print $4}')
ACTNODES=$(echo "$NODES" | awk '{print $4}' | grep -c Active)

if [ "$ACTNODES" -ge 2 ]; then
	echo "There are enough active nodes to take on additional services"
else
	echo "There aren't enough active nodes to perform this action"
	exit
fi

if [ "$STATUS" == "Ready" ]; then
	echo "This node is in the expected state. Testing the /etc/nixos/configuration.nix file."
else
	echo "This node is not in the expected state"
	exit
fi

if sudo nixos-rebuild dry-activate 2>&1 | grep -q "would activate the configuration..."; then
	echo "Nix configuration is good, draining node"
	sudo docker node update --availability drain $HOST >/dev/null
	echo "Sleeping for one minute to allow for all services to replicate to other nodes"
	sleep 60
	echo "Updating node"
	sudo nixos-rebuild switch >/dev/null 2>&1
	echo "Setting the node as active"
	sudo docker node update --availability active $HOST | >/dev/null
else
	echo "The Nix configuration test failed"
	exit
fi

echo "Update completed"
