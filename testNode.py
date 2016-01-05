import sys
import os

from Node import Node
host = "131.215.159.130"
port = int(sys.argv[1])
n = Node(host, port, debug=False)
