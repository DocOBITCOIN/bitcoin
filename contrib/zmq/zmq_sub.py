#!/usr/bin/env python2

import array
import binascii
import zmq
import struct

port = 28332

zmqContext = zmq.Context()
zmqSubSocket = zmqContext.socket(zmq.SUB)
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, "hashblock")
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, "hashtx")
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, "rawblock")
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, "rawtx")
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, "mempooladded")
zmqSubSocket.setsockopt(zmq.SUBSCRIBE, "mempoolremoved")
zmqSubSocket.connect("tcp://127.0.0.1:%i" % port)

# Reasons for removal of transaction from mempool
MPR_REASONS = {0:'UNKNOWN', 1:'EXPIRY', 2:'SIZELIMIT', 3:'REORG', 4:'BLOCK', 5:'REPLACED'}

try:
    while True:
        msg = zmqSubSocket.recv_multipart()
        topic = str(msg[0])
        body = msg[1]

        if topic == "hashblock":
            print "- HASH BLOCK -"
            print binascii.hexlify(body)
        elif topic == "hashtx":
            print '- HASH TX -'
            print binascii.hexlify(body)
        elif topic == "rawblock":
            print "- RAW BLOCK HEADER -"
            print binascii.hexlify(body[:80])
        elif topic == "rawtx":
            print '- RAW TX -'
            print binascii.hexlify(body)
        elif topic == 'mempooladded':
            print '- MEMPOOL ADDED -'
            (hash, fee, size) = struct.unpack('<32sQI', body)
            print '%s fee=%i size=%i' % (binascii.hexlify(hash), fee, size)
        elif topic == 'mempoolremoved':
            print '- MEMPOOL REMOVED -'
            (hash, reason) = struct.unpack('<32sB', body)
            print '%s reason=%s' % (binascii.hexlify(hash), MPR_REASONS.get(reason, 'UNKNOWN %i' % reason))

except KeyboardInterrupt:
    zmqContext.destroy()
