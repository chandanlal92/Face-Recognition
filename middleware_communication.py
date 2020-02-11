#!/usr/bin/python

import time
import ctypes
from ctypes import *
import json
import copy

# Load the shared lib
lib = cdll.LoadLibrary('./libcppconnector.so')

# Call function from lib
lib.middleware_connect.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.middleware_connect.restype = ctypes.c_void_p

lib.middleware_register.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.middleware_register.restype = ctypes.c_void_p


#~ global data_middleware
#~ global request_data
data_middleware={}
request_data={}

def msg_handler(group, msg): 
    print("msg_handler", group, msg)
    data_middleware=copy.deepcopy(msg)
    data_middleware=(msg)
    return None
def msg_handler_2(group, msg):
    global request_data
    print("msg_handler", group, msg)
    request_data=msg
    print(request_data)
    msg_data=json.dumps(request_data)
    #~ print(msg_data["/camera_id/"])
    return None    

MSGHANDLERFUNC = CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_char_p)
msg_handler_func = MSGHANDLERFUNC(msg_handler)
msg_handler_func_2=MSGHANDLERFUNC(msg_handler_2)
lib.middleware_subscribe.argtypes = [ctypes.c_void_p, ctypes.c_char_p, MSGHANDLERFUNC]
lib.middleware_subscribe.restype = None

lib.middleware_publish.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
lib.middleware_publish.restype = None

lib.middleware_join.argtypes = [ctypes.c_void_p]
lib.middleware_join.restype = None

con_name = "python-con"
host_name = "localhost"

connection_handle = lib.middleware_connect(con_name.encode('utf-8'), host_name.encode('utf-8'), 5336)
#~ connection_handle_2 = lib.middleware_connect(con_name.encode('utf-8'), host_name.encode('utf-8'), 5336)
time.sleep(1)
middleware_handle = lib.middleware_register(connection_handle, "python-application".encode('utf-8'))
middleware_handle_2=lib.middleware_register(connection_handle, "face_request".encode('utf-8'))
print("client registered")
time.sleep(1)

# Subscribe to msg_group and receive test message
msg_group = "EchoRequest"
msg_group_2="FaceRequest"
#~ lib.middleware_subscribe(middleware_handle_2, msg_group.encode('utf-8'), msg_handler_func)
#~ print("client subscribed")
def get_subscription_msg():
	lib.middleware_subscribe(middleware_handle, msg_group_2.encode('utf-8'),msg_handler_func_2)
	print(request_data)
	return request_data
time.sleep(1)
'''lib.middleware_publish(middleware_handle, msg_group.encode('utf-8'), "{
  "tpe": "de.hawhamburg.csti.example.ReplyFaceRecognition",
  "url": "http://test.de/image.jpg",
  detectedFaces: [
        {userId: 123, coordinates: {x: 100, y: 101}, 
        {userId: 124, coordinates: {x: 200, y: 201}
    ],
    keyframe: "empty-String-if-not-available",
    timestamp: 3428943982987
  }
}".encode('utf-8'))'''

# Run forever
#lib.middleware_join(connection_handle)
time.sleep(10)
