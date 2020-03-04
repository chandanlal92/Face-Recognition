# Face-Recognition

This application is used to perform Real-time face recognition using Mako-G Camera. It handles face recognition request via videostream or picture.

System Requirements
  - Pymba(Python implementation of Vimba Library)
  - Face_recognition
  - openCV
  - numpy
  - pickle
  - scikit

1. Train Face Encodings			
   MainFile : train_face_encodings.py  
      - Input:Location of Images and Face Encodings 
      -  Train Images with its face encoding
2. Live Face recognition
    MainFile: live_face_recognition_mako.py
      -  Subcribes Video stream request or Image_request, display recognized faces
      -   Interfaces with mako_g camera stream
      -   Draws bounding boxes on known faces with Names and Unknown face as Unknown
      -   Displays the live video stream with bounding box on face
  
 
 
    

          
