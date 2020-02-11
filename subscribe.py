import time
import ctypes
from ctypes import *
import cv2
import json

# Load the shared lib
lib = cdll.LoadLibrary('./libcppconnector.so')

# Call function from lib
lib.middleware_connect.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.middleware_connect.restype = ctypes.c_void_p

lib.middleware_register.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.middleware_register.restype = ctypes.c_void_p

def msg_handler(group, msg):
    print("msg_handler", group, msg)
    return None

MSGHANDLERFUNC = CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_char_p)
msg_handler_func = MSGHANDLERFUNC(msg_handler)

lib.middleware_subscribe.argtypes = [ctypes.c_void_p, ctypes.c_char_p, MSGHANDLERFUNC]
lib.middleware_subscribe.restype = None

lib.middleware_publish.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
lib.middleware_publish.restype = None

lib.middleware_join.argtypes = [ctypes.c_void_p]
lib.middleware_join.restype = None

con_name = "python-con"
host_name = "localhost"
#~ con_name_2="face-con"

connection_handle = lib.middleware_connect(con_name.encode('utf-8'), host_name.encode('utf-8'), 5336)
#~ connection_handle_2 = lib.middleware_connect(con_name.encode('utf-8'), host_name.encode('utf-8'), 5336)
time.sleep(1)
middleware_handle = lib.middleware_register(connection_handle, "python-application".encode('utf-8'))
#~ middleware_handle_2=lib.middleware_register(connection_handle_2,"face_request".encode('utf-8'))
print("client registered")
time.sleep(1)

data_request={"tpe": "de.hawhamburg.csti.example.RequestFaceRecognition",
               "url": "https://www.biography.com/.image/ar_1:1%2Cc_fill%2Ccs_srgb%2Cg_face%2Cq_auto:good%2Cw_300/MTE4MDAzNDEwNzg5ODI4MTEw/barack-obama-12782369-1-402.jpg",
              }
data_request_2={"tpe": "de.hawhamburg.csti.example.RequestFaceRecognition",
                  "camera_id":"DEV_000F315BA97A",
                  }
              
data_request_json=json.dumps(data_request)
data_request_json_2=json.dumps(data_request_2)

# Subscribe to msg_group and receive test message
msg_group = "EchoRequest"
msg_group_2="FaceRequest"
lib.middleware_publish(middleware_handle,msg_group_2.encode('utf-8'),data_request_json)
lib.middleware_subscribe(middleware_handle, msg_group.encode('utf-8'), msg_handler_func)
print("client subscribed")
time.sleep(1)
while True:
 if cv2.waitKey(1) & 0xFF == ord('q'):
  break
 lib.middleware_publish(middleware_handle,msg_group_2.encode('utf-8'),data_request_json)
 lib.middleware_subscribe(middleware_handle, msg_group.encode('utf-8'), msg_handler_func)
 time.sleep(10)

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
#~ lib.middleware_join(connection_handle)
time.sleep(10)

