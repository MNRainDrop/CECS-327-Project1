import docker

# Initialize the Docker client
client = docker.from_env()

# Define the node names and ports
nodes = [
    {"name": "node1", "port": 3001},
    {"name": "node2", "port": 3002},
    {"name": "node3", "port": 3003},
    {"name": "node4", "port": 3004},
    {"name": "node5", "port": 3005},
]

# Create and run Docker containers for each node
for node in nodes:
    container = client.containers.run(
        "ubuntu:latest",  # Use an appropriate base image
        detach=True,
        name=node["name"],
        ports={f"{node['port']}/tcp": node["port"]},
        command="tail -f /dev/null",  # Keep the container running
    )

# Print container information
for container in client.containers.list():
    print(f"Container Name: {container.name}, Port Mapping: {container.ports}")