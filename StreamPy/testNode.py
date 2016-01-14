import sys
import os

from Node import Node
host = sys.argv[1]
port = int(sys.argv[2])
n = Node(host, port, debug=False)
