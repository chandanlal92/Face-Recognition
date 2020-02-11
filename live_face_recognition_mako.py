from __future__ import absolute_import, print_function, division
import face_recognition
import cv2
from pymba import *
import numpy as np
import time
import sys
import datetime
import middleware_communication
from face_recognition.face_recognition_cli import image_files_in_folder
import json
import os
import pickle
from PIL import Image,ImageDraw
import io
import urllib2
# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)

            
#video_capture = cv2.VideoCapture(1+800)
#location of Images and Locations of the trained face encodings
train_dir=('/home/chandanlal/face_encoding')
face_encode=('/home/chandanlal/face_encoding/face_encodings')

global Known_face_encodings

Known_face_encodings=[]
known_face_names=[]
verbose=False
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# Load a sample picture and learn how to recognize it.
#obama_image = face_recognition.load_image_file("obama.jpg")
#obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
#biden_image = face_recognition.load_image_file("biden.jpg")
#biden_face_encoding = face_recognition.face_encodings(biden_image)[0]
#Load a sample picture and learn how to recognize it.
#chandan_image = face_recognition.load_image_file("chandan.jpg")
#chandan_face_encoding = face_recognition.face_encodings(chandan_image)[0]
  
   

"""
# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding,
    chandan_face_encoding 
]
known_face_names = [
    "Barack Obama",
    "Joe Biden",
    "Chandan lal"
    
]
"""

#Load Trained Face_encodings
print("Loading Face_encodings.....")
data_face_encodings=pickle.loads(open(face_encode,"rb").read())
Known_face_encodings=data_face_encodings["encodings"]
known_face_names=data_face_encodings["names"]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
counts = {}
process_this_frame = True
camera_id_request={}
topic={}
face_recognition_request={}

#Default data format
data={"tpe": "de.hawhamburg.csti.example.ReplyFaceRecognition",
               "url": "http://test.de/image.jpg",
               "detectedFaces": [
               {"userId": 'name_1', 'coordinates': {'x': 200, 'y': 201}}],
               'timestamp': 3428943982987
              }
#~ print(data["url"])

#Face Recognition with Camera Interface

with Vimba() as vimba:
	
    system = vimba.getSystem()
    system.runFeatureCommand("GeVDiscoveryAllOnce")
    time.sleep(0.2)
    time.sleep(2)

    

    middleware_communication.lib.middleware_subscribe(middleware_communication.middleware_handle, middleware_communication.msg_group_2.encode('utf-8'),middleware_communication.msg_handler_func_2)
    time.sleep(10)
    face_recognition_request=middleware_communication.get_subscription_msg()
    face_recognition_request=json.loads(face_recognition_request)
    #If Image URL is Requested
    if "url" in face_recognition_request:
		print(face_recognition_request["url"])
		fd=urllib2.urlopen(face_recognition_request["url"])
		image_unknown=np.asarray(bytearray(fd.read()),dtype="uint8")
		image_unknown=cv2.imdecode(image_unknown,cv2.IMREAD_COLOR)
		face_locations=face_recognition.face_locations(image_unknown)
		face_encodings=face_recognition.face_encodings(image_unknown,face_locations)
		pil_im=Image.fromarray(image_unknown)
		draw=ImageDraw.Draw(pil_im)
		# Display the results
		for(top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
			matches = face_recognition.compare_faces(Known_face_encodings, face_encoding)
			name = "Unknown"
			time_stamp=datetime.datetime.now()
			if True in matches:
				first_match_index = matches.index(True)
				name = known_face_names[first_match_index]
			print(name)
			# Draw a box around the face using the Pillow module
			draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
			
			# Draw a label with a name below the face
			text_width, text_height = draw.textsize(name)
			draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
			draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))
			print(left,top,right,bottom)
			del draw
			pil_im.show()
			if name is "unknown":
			 data["detectedFaces"].append({})
			data["detectedFaces"].append({"UserID":name,"Coordinates":{'x':left,'y':top}})
			ts=str(datetime.datetime.now())
			data['url']=face_recognition_request["url"]
			data['timestamp']=ts
			data_json=json.dumps(data)
			middleware_communication.lib.middleware_publish(middleware_communication.middleware_handle, middleware_communication.msg_group.encode('utf-8'),data_json)
			#~ pil_im.show()
			#~ cv2.waitKey(0)
		sys.exit()
	#If Camera Stream ID is requested
    cam_req_id=face_recognition_request["camera_id"]
    print(cam_req_id)
    #open the camera with initial Settings
    #~ c0 = vimba.getCamera(camera_ids[0])
    c0 = vimba.getCamera(cam_req_id)
    c0.openCamera()
    c0.AcquisitionMode='Continuous'
    c0.ExposureAuto='Continuous'
    c0.GainAuto='Continuous'

    try:
        #gigE camera
        print("Packet size:", c0.GevSCPSPacketSize)
        c0.StreamBytesPerSecond = 100000000
        print("BPS:", c0.StreamBytesPerSecond)
    except:
        #not a gigE camera
        pass

    #set pixel format
    c0.PixelFormat = "BGR8Packed"  # OPENCV DEFAULT
    time.sleep(0.2)

    frame = c0.getFrame()
    frame.announceFrame()

    c0.startCapture()

    framecount = 0
    droppedframes = []

    while 1:
        try:
            frame.queueFrameCapture()
            success = True
        except:
            droppedframes.append(framecount)
            success = False
        c0.runFeatureCommand("AcquisitionStart")
        c0.runFeatureCommand("AcquisitionStop")
        frame.waitFrameCapture(1000)
        frame_data = frame.getBufferByteData()
        if success:
            img = np.ndarray(buffer=frame_data,
                             dtype=np.uint8,
                             shape=(frame.height, frame.width, frame.pixel_bytes))
            

	
	    # Grab a single frame of video
	    #ret, frame = video_capture.read()
	
	    # Resize frame of video to 1/4 size for faster face recognition processing
	    small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
	
	    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
	    rgb_small_frame = small_frame[:, :, ::-1]
	
	    # Only process every other frame of video to save time
	    if process_this_frame:
	        # Find all the faces and face encodings in the current frame of video
	        face_locations = face_recognition.face_locations(rgb_small_frame)
	        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
	
	        face_names = []
	        for face_encoding in face_encodings:
	            # See if the face is a match for the known face(s)
	            matches = face_recognition.compare_faces(data_face_encodings["encodings"], face_encoding)
	            name = "Unknown"
	
	            # If a match was found in known_face_encodings, just use the first one.
	            if True in matches:
	                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			    
	                #Finding the matched Index
	                for i in matchedIdxs:
						name = data_face_encodings["names"][i]
						counts[name] = counts.get(name, 0) + 1
	                #name = max(counts, key=counts.get)
	                #first_match_index = matches.index(True)
	                #name = known_face_names[first_match_index]
	            
	            
	            
	                 
	            face_names.append(name)
	
	    process_this_frame = not process_this_frame
	   
	    Detected_face=[]
        #data["DetectedFaces"]=[{"UserID":name,"Coordinates":{'x':left,'y':top}}]
        #lib = cdll.LoadLibrary('./libcppconnector.so')
        # Display the results
	    for(top, right, bottom, left), name in zip(face_locations, face_names):
	        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
	        top *= 4
	        right *= 4
	        bottom *= 4
	        left *= 4
	        time_stamp=datetime.datetime.now()
	        # Draw a box around the face
	        cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
	        print(left,top,right,bottom)
	        # Draw a label with a name below the face
	        cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
	        font = cv2.FONT_HERSHEY_DUPLEX
	        cv2.putText(img, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
	        if name is "unknown":
	         data["detectedFaces"].append({})
	        data["detectedFaces"].append({"UserID":name,"Coordinates":{'x':left,'y':top}})
	        ts=str(datetime.datetime.now())
	        data['timestamp']=ts
	        data_json=json.dumps(data)
	        middleware_communication.lib.middleware_publish(middleware_communication.middleware_handle, middleware_communication.msg_group.encode('utf-8'),data_json)
	        
	   
	    cv2.imshow('Video', img)
    	
	    # Hit 'q' on the keyboard to quit!
	    if cv2.waitKey(1) & 0xFF == ord('q'):
	        break
	
	# Release handle to the webcam
	#video_capture.release()
	
    c0.endCapture()
    c0.revokeAllFrames()

    c0.closeCamera()

	#cv2.destroyAllWindows()
	
