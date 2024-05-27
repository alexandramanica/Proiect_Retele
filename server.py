import asyncio
import math
import random
import networkx as nx
import matplotlib.pyplot as plt

class Node:
    def __init__(self, key, info):
        self.key = key
        self.info = info
        self.connections = {}
        self.services = info.get('services', [])  # Lista de servicii ale nodului
        self.running_services = set()  # Set pentru a ține evidența serviciilor pornite

    def calculate_distance(self, coord1, coord2):
        x1, y1 = coord1
        x2, y2 = coord2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Connected to {addr}")
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode()
            print(f"Received data from {addr}: {message}")
            parts = message.strip().split()
            if not parts:
                writer.write("Invalid command. Please enter a command.".encode())
                await writer.drain()
                continue

            command = parts[0].lower()
            if command == "query":
                if len(parts) != 2:
                    writer.write("Invalid command. Please enter in the format 'query <node>'.".encode())
                else:
                    node_name = parts[1]
                    status = node_manager.query_node(node_name)
                    writer.write(status.encode())

            elif command == "start":
                if len(parts) != 3:
                    writer.write("Invalid command. Please enter in the format 'start <node> <service>'.".encode())
                else:
                    node_name = parts[1]
                    service_name = parts[2]
                    response = await node_manager.start_service(node_name, service_name)
                    writer.write(response.encode())

            elif command == "stop":
                if len(parts) != 3:
                    writer.write("Invalid command. Please enter in the format 'stop <node> <service>'.".encode())
                else:
                    node_name = parts[1]
                    service_name = parts[2]
                    response = await node_manager.stop_service(node_name, service_name)
                    writer.write(response.encode())

            else:
                writer.write("Invalid command.".encode())

            await writer.drain()

        print(f"Connection with {addr} closed")

    async def start_server(self):
        server = await asyncio.start_server(
            self.handle_client, self.info['ip'], self.info['port']
        )
        print(f"Node {self.key} is listening for connections on port {self.info['port']}...")
        async with server:
            await server.serve_forever()

    def connect_to_nearest_nodes(self, nodes):
        connected_to = []
        distances = [(node_key, self.calculate_distance(self.info['coordinates'], node_info['coordinates'])) for node_key, node_info in nodes.items() if node_key != self.key]
        distances.sort(key=lambda x: x[1])  # Sortăm nodurile în funcție de distanță
        for i in range(min(2, len(distances))):  # Conectăm la cel mult 2 noduri vecine
            node_key, _ = distances[i]
            self.connections[node_key] = nodes[node_key]['coordinates']  # Adaugă conexiunile nodului în obiectul Node
            connected_to.append(node_key)
            print(f"Connected to node: {node_key}")
        return connected_to

    async def start_service(self, service_name):
        # Simulare pornire serviciu
        print(f"Service {service_name} started on node {self.key}")
        self.running_services.add(service_name)

    async def stop_service(self, service_name):
        # Simulare oprire serviciu
        print(f"Service {service_name} stopped on node {self.key}")
        self.running_services.remove(service_name)

    def get_service_status(self):
        status = f"Service status on node {self.key}:\n"
        for service in self.services:
            if service in self.running_services:
                status += f"{service}: Running\n"
            else:
                status += f"{service}: Stopped\n"
        return status


class NodeManager:
    def __init__(self, nodes):
        self.nodes = {key: Node(key, info) for key, info in nodes.items()}

    def query_node(self, node_name):
        if node_name in self.nodes:
            return self.nodes[node_name].get_service_status()
        else:
            return f"Node {node_name} not found."

    async def start_service(self, node_name, service_name):
        if node_name in self.nodes:
            await self.nodes[node_name].start_service(service_name)
            return f"Service {service_name} started on node {node_name}."
        else:
            return f"Node {node_name} not found."

    async def stop_service(self, node_name, service_name):
        if node_name in self.nodes:
            await self.nodes[node_name].stop_service(service_name)
            return f"Service {service_name} stopped on node {node_name}."
        else:
            return f"Node {node_name} not found."

    async def start_all_nodes(self):
        tasks = []
        G = nx.Graph()  # Creează un graf gol
        for key, node in self.nodes.items():
            task = asyncio.create_task(node.start_server())  # Folosește asyncio.create_task() pentru a porni serverul în mod asincron
            connected_to = node.connect_to_nearest_nodes({k: v.info for k, v in self.nodes.items()})  # Connect to all other nodes
            G.add_node(key)  # Adaugă nodul în graf
            for connected_node in connected_to:
                G.add_edge(key, connected_node)  # Adaugă legături bazate pe conexiuni
                print(f"Node {key} connected to node {connected_node}")
            tasks.append(task)

        # Desenează graficul
        nx.draw(G, with_labels=True)
        plt.show()

        await asyncio.gather(*tasks)


nodes = {
    'A': {"ip": "127.0.0.1", "port": 12345, "coordinates": (0.0, 0.0), "services": ["service1", "service2"]},
    'B': {"ip": "127.0.0.1", "port": 12346, "coordinates": (3.0, 4.0), "services": ["service3", "service4"]},
    'C': {"ip": "127.0.0.1", "port": 12347, "coordinates": (5.0, 6.0), "services": ["service5"]},
    'D': {"ip": "127.0.0.1", "port": 12348, "coordinates": (-2.0, -2.0), "services": ["service6", "service7"]},
    'E': {"ip": "127.0.0.1", "port": 12349, "coordinates": (-4.0, 4.0), "services": ["service8"]}
}

node_manager = NodeManager(nodes)

if __name__ == "__main__":
    asyncio.run(node_manager.start_all_nodes())  # Rulează bucla de evenimente asincronă folosind asyncio.run()
