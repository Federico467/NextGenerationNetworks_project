from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
import networkx as nx
from mininet.net import Mininet
from Network import TOPO
import subprocess



SLICES = []
nameToIP = {
        "h1": "10.0.0.1",
        "h2": "10.0.0.2",
        "h3": "10.0.0.3",
        "h4": "10.0.0.4",
        "h5": "10.0.0.5",
        "h6": "10.0.0.6",
        "h7": "10.0.0.7"
    }

def calculate_path(topology, src, dst, link_capacities):

    #create an algorith, Sort the edges by capacity. Remove the edge with lowest capacity,
    # and check if there is still a path from s to t. If there is, move on the edge with the second lowest capacity,
    # and so on. At some point, we will disconnect s from t by removing an edge of capacity c.
    # Now, we know that c is the maximum capacity of a single path from sto t.

    #create a graph from the topology
    G = nx.Graph()
     # Add nodes
    for switch in topology.switches():
        G.add_node(switch)

    for host in topology.hosts():
        G.add_node(host)

    # Add edges
    for src_, dst_ in topology.links():
        link_attrs = topology.linkInfo(src_, dst_)
        # Check if 'bw' or other possible keys exist
        capacity = link_attrs.get('bw', 0)  # Default to 0 if bw attribute doesn't exist
        G.add_edge(src_, dst_, bw=capacity)

    print("Nodes:", G.nodes())
    print("Edges:", G.edges())

    #create a dictionary to store the capacity of each link
    link_capacity = {}
    print("link capacities: ", link_capacities)
    if link_capacities:
        print("second time running the function.--------------------------------------------------------------------------------------------")
        link_capacity = link_capacities.copy()
    else:
        for edge in G.edges():
            link_capacity[edge] = G[edge[0]][edge[1]]['bw']

    link_capacities_backup = link_capacity.copy()
    print("Link capacity:", link_capacity)
    
    #create a dictionary to store the path from src to dst
    path = nx.shortest_path(G, source=src, target=dst, weight='bw')


    if not nx.has_path(G, src, dst):
        print("No path exists between source and destination.")
        return None    


    #if there is path from src to dst, remove the edge with the lowest capacity
    current_path = path
    while nx.has_path(G, src, dst):
        # check if there is still a path from src to dst
        path = current_path
        current_path = nx.shortest_path(G, source=src, target=dst, weight='bw')
        if not current_path:
            break
        # remove edge with lowest capacity
        min_capacity = min(link_capacity.values())
        for edge in link_capacity:
            if link_capacity[edge] == min_capacity:
                G.remove_edge(edge[0], edge[1])
                #remove the edge from the dictionary
                del link_capacity[edge]
                break

        print("Path:", path)

    print("\nPath:", path)  # Debug print to check the structure of path
    print("link capa", link_capacities_backup)

    if path:
        max_bandwidth = float('inf')  # Initialize with positive infinity
        
        for u, v in zip(path[:-1], path[1:]):
            #print("u,v=", u,v)
            edge_bandwidth_uv = link_capacities_backup.get((u, v), float('inf'))  # Get bandwidth of edge (u, v)
            edge_bandwidth_vu = link_capacities_backup.get((v, u), float('inf'))  # Get bandwidth of edge (v, u)
            edge_bandwidth = min(edge_bandwidth_uv, edge_bandwidth_vu)  # Choose the minimum bandwidth
            #print("edge ", edge_bandwidth, "\n")
            max_bandwidth = min(max_bandwidth, edge_bandwidth)
            #print("max ",max_bandwidth, "\n")
        
        print("Maximum bandwidth of the path:", max_bandwidth)
    else:
        print("No valid path found.")
    
    print("Final path:", path)

    if not link_capacities:
        print("first time, returning also link capacities.--------------------------------------------------------------------------------------------")
        return path,max_bandwidth, link_capacities_backup
    else:
        print("second time, returning only path and max bandwidth.--------------------------------------------------------------------------------------------")
        return path,max_bandwidth






def allocate(path,link_capacity, link_capacities):
    #remove the capacity from the links
    for u, v in zip(path[:-1], path[1:]):
        print("u,v=", u,v)
        #check if link u v exists
        
        if (u, v) in link_capacities:
            #print("link capa before:", link_capacities[(u, v)])
            link_capacities[(u, v)]-= link_capacity
            #print("link capa after:", link_capacities[(u, v)])
        elif (v, u) in link_capacities:
            #print("link capa before:", link_capacities[(v, u)])
            link_capacities[(v, u)] -= link_capacity
            #print("link capa after:", link_capacities[(v, u)])
        else:
            print("Link does not exist")
            return
        
        
    print("Link capacities after allocation: ", link_capacities)

    SLICES.append(path.copy()+[link_capacity])



    

    SwitchDestToPort = {
            "s1": {
                "h1": 1,
                "s2": 2,
                "s4": 4,
                "s5": 3
            },
            "s2": {
                "h2": 1,
                "s1": 2,
                "s3": 3,
                "s5": 4
            },
            "s3": {
                "h3": 1,
                "s2": 2,
                "s4": 3
            },
            "s4": {
                "h4": 1,
                "h5": 2,
                "s1": 3,
                "s3": 4,
                "s5": 5

            },
            "s5": {
                "h6": 1,
                "h7": 2,
                "s1": 4,
                "s2": 3,
                "s4": 5
                
            }
        }

    # Update the flow tables for each switch along the path
    src_hostIP = nameToIP[path[0]]
    dst_hostIP = nameToIP[path[-1]]
    flow_table_command1 = {}
    flow_table_command2 = {}
    #for each switch in the path except the last one and the first one
    for switch in path[1:-1]:

        
        #install the flow rule
        #sudo ovs-ofctl add-flow s5 ip,priority=65500,dl_type=0x0800,nw_src=10.0.0.7,nw_dst=10.0.0.2,actions=output:3
        #sudo ovs-ofctl del-flows s5 dl_type=0x0800,nw_src=10.0.0.7,nw_dst=10.0.0.2
        print("switch: ", switch)
        print("path: ", path)
        next_switch = path[path.index(switch)+1]
        print("next switch: ", next_switch)
        port = SwitchDestToPort[switch][next_switch]
        flow_table_command = "sudo ovs-ofctl add-flow " + switch + " ip,priority=65500,dl_type=0x0800,nw_src=" + src_hostIP + ",nw_dst=" + dst_hostIP + ",actions=output:" + str(port)
        print("command: ",switch, ": ",flow_table_command)
        subprocess.run(flow_table_command, shell=True)
        
        
        if switch == path[-2]:
            switch = path[0]
            next_switch = path[1]
            print("path[2]: ", path[1])
            print("path[1]: ", path[0])

        port = SwitchDestToPort[next_switch][switch]

        flow_table_command = "sudo ovs-ofctl add-flow " + next_switch + " ip,priority=65500,dl_type=0x0800,nw_src=" + dst_hostIP + ",nw_dst=" + src_hostIP + ",actions=output:" + str(port)
        print("command: ",switch, ": ",flow_table_command)
        subprocess.run(flow_table_command, shell=True)
        

    return link_capacities





def create_slice(src_host, dst_host, user_capacity, link_capacities):
    custom_topo = TOPO
    # Calculate path
    if not link_capacities:
        print("first time running the function create slice.--------------------------------------------------------------------------------------------")
        path, max_bandwidth, link_capacities = calculate_path(custom_topo, src_host, dst_host, link_capacities)
    else:
        print("second time running the function create slice.--------------------------------------------------------------------------------------------")
        path, max_bandwidth = calculate_path(custom_topo, src_host, dst_host, link_capacities)
    print("max band=", max_bandwidth)
    print("path =", path)
    print(user_capacity)
    #if path doesnt exist exit this function
    if not path:
        return
    if max_bandwidth >= user_capacity:
        print("allocate")
        link_capacities = allocate(path, user_capacity, link_capacities)
    else:
        print("No available bandwidth")
        allocate_bool = input("Do you want to allocate it anyway? (y/n) \nThis is only for testing ")
        
        if allocate_bool == "y":
            link_capacities = allocate(path, user_capacity, link_capacities)

    return link_capacities






    
def delete_slice(link_capacities):

    print("Current slices: ")
    for i, slice_ in enumerate(SLICES):
        print(i, slice_)
    i=int(input("Enter the index of the slice you want to delete: "))
    
    user_capacity = SLICES[i][-1]
    #remove the last element in SLICES
    SLICES[i].pop()
    
    for u, v in zip(SLICES[i][:-1], SLICES[i][1:]):
        #print("u,v=", u,v)
        #check if link u v exists
        
        if (u, v) in link_capacities:
            #print("link capa before:", link_capacities[(u, v)])
            link_capacities[(u, v)]+= user_capacity
           # print("link capa after:", link_capacities[(u, v)])
        elif (v, u) in link_capacities:
            #print("link capa before:", link_capacities[(v, u)])
            link_capacities[(v, u)] += user_capacity
            #print("link capa after:", link_capacities[(v, u)])
        else:
            print("Link does not exist")
            return
        
    print("Link capacities after deallocation:", link_capacities)
    

    flow_table_command1 = {}
    flow_table_command2 = {}

    #delete the flow rules
    for switch in SLICES[i][1:-1]:
        flow_table_command1[switch]= "sudo ovs-ofctl del-flows " + switch + " dl_type=0x0800,nw_src=" + nameToIP[SLICES[i][0]]+ ",nw_dst=" + nameToIP[SLICES[i][-1]]
        flow_table_command2[switch]= "sudo ovs-ofctl del-flows " + switch + " dl_type=0x0800,nw_src=" + nameToIP[SLICES[i][-1]] + ",nw_dst=" + nameToIP[SLICES[i][0]]
        print("command: ",switch, ": ",flow_table_command1[switch], "\n", flow_table_command2[switch])
        subprocess.run(flow_table_command1[switch], shell=True)
        subprocess.run(flow_table_command2[switch], shell=True)
    
    SLICES.pop(i)

    return link_capacities

def inputs():
    link_capacities = {}
    while True:
        #ask user if they want to crete new flows or delete existing flows
        print("Do you want to add new flows or delete existing flows? (add/delete/exit)")
        action = input()
        if action == "exit":
            exit(0)
        if action != "add" and action != "delete":
            print("Invalid action")
            exit(1)

        if action == "add":
            src_host = input("Enter source host name (1 to 7): ")
            dst_host = input("Enter destination host name (1 to 7): ")
            user_capacity = int(input("Enter link capacity (in Mbps): "))
            user_capacity = user_capacity * 1 #if you want to change units

        
            #src parameter type check
            if not src_host.isdigit():
                print("Source host has to be a number")
                exit(1)
            src_host = int(src_host)
            if src_host < 1 or src_host > 7:
                print("Source host has to be between 1 and 7")
                exit(1)

            src_host = "h" + str(src_host)
            
            #dst parameter type check
            if not dst_host.isdigit():
                print("Destination host has to be a number")
                exit(1)
            dst_host = int(dst_host)
            if dst_host < 1 or dst_host > 7:
                print("Destination host has to be between 1 and 7")
                exit(1)

            dst_host = "h" + str(dst_host)
            

            #src and dst have to be different
            if src_host == dst_host:
                print("Source and destination hosts cannot be the same")
                exit(1)
            
            print("Add new flows")
            link_capacities = create_slice(src_host, dst_host, user_capacity, link_capacities)


        if action == "delete":
            print("Delete existing flows")
            link_capacities = delete_slice(link_capacities)
        
        print("\n\n\n\n")
    




if __name__ == "__main__":
    net=Mininet()
    inputs()

    




