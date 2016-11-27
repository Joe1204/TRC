import socket
import struct
import sys
import optparse
from datetime import datetime


class flushfile(file):
    def __init__(self, f):
        self.f = f
    def write(self, x):
        self.f.write(x)
        self.f.flush()

sys.stdout = flushfile(sys.stdout)

def main(dest_name,t_port,hops):
    dest_addr = socket.gethostbyname(dest_name)#Get IP Address of target domain
    port = t_port
    max_hops = hops
    icmp = socket.getprotobyname('icmp')#Create ICMP Sockets
    udp = socket.getprotobyname('udp')#Create UDP Sockets
    ttl = 1
    sys.stdout.write('\ntraceroute to %s (%s)\n'%(dest_name,dest_addr))
    sys.stdout.write('\nTTL\tIP Address\tHost Name\tRTT\n')
    sys.stdout.write('-------------------------------------------\n\n')
    while True:
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)#Use icmp socket to receive packets
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)#Use udp socket to send packets
        sender_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        
        # Create a timeout struct(seconds, microseconds)
        timeout = struct.pack("ll", 5, 0)
        
        #Set a timeout interval on receiver socket
        receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)
        
        receiver_socket.bind(("", port))
        sys.stdout.write(" %d  " % ttl)
	t1=datetime.now()
        sender_socket.sendto("", (dest_name, port))
        curr_addr = None
        curr_name = None
        finished = False
        attempts = 3
        while not finished and attempts > 0:
            try:
                data, curr_addr = receiver_socket.recvfrom(512)
                finished = True
                curr_addr = curr_addr[0]
                try:
                    curr_name = socket.gethostbyaddr(curr_addr)[0]
                except socket.error:
                    curr_name = curr_addr
            except socket.error as (errno, errmsg):
                attempts = attempts - 1
                sys.stdout.write("* ")
        
        sender_socket.close()
        receiver_socket.close()
        t2=datetime.now()
	t=str(((t2-t1).microseconds)/1000)#Calculate RTT in milliseconds
        if not finished:
            pass
        
        if curr_addr is not None:
	    sys.stdout.write("\t%s\t%s\t%s\n" % (curr_addr,curr_name,t))
        else:
	    sys.stdout.write("\t\t\t\t%s\n"%(t))

        ttl += 1
        if curr_addr == dest_addr or ttl > max_hops:
            break

if __name__ == "__main__":
	sys.stdout.write('Enter the address:')
	addr=raw_input()
	(sys.stdout.write('Enter the Port:'))
	port=int(raw_input())
	(sys.stdout.write('Enter the no of hops:'))
	ttl=int(raw_input())
	main(addr,port,ttl)
