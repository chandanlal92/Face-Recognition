import math
from sklearn import neighbors
import os
import os.path
import pickle
from PIL import Image, ImageDraw
import face_recognition
import urllib
from face_recognition.face_recognition_cli import image_files_in_folder


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
Known_face_encodings=[]
known_face_names=[]
verbose=False

train_dir=('/home/chandanlal/face_encoding')
train_dir_face=('/home/chandanlal/face_encoding/face_encodings')
#Trains Face_encodings from the Images Stored in the Folder
for class_dir in os.listdir(train_dir):
	if not os.path.isdir(os.path.join(train_dir, class_dir)):
	 continue

# Loop through each training image for the current person
	for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
		image = face_recognition.load_image_file(img_path)
		face_bounding_boxes = face_recognition.face_locations(image)

		if len(face_bounding_boxes) != 1:
			# If there are no people (or too many people) in a training image, skip the image.
			if verbose:
				print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
		else:
		# Add face encoding for current image to the training set
			Known_face_encodings.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
			known_face_names.append(class_dir)

print("[INFO] serializing encodings...")
data = {"encodings": Known_face_encodings, "names": known_face_names}
f = open(train_dir_face, "wb")
f.write(pickle.dumps(data))
f.close()
