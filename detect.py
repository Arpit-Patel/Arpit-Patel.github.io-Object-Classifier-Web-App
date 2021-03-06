import numpy as np
import os
import timeit

import tensorflow as tf

from PIL import Image

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('object_detection', 'data', 'mscoco_label_map.pbtxt')
PATH_TO_IMAGES = 'static/images/uploads/'
NUM_CLASSES = 90

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def load_image_into_numpy_array(image):
	(im_width, im_height) = image.size
	return np.array(image.getdata()).reshape(
	    (im_height, im_width, 3)).astype(np.uint8)

def image_detect(filename, detection_graph):
	with detection_graph.as_default():
		with tf.Session(graph=detection_graph) as sess:
			image = Image.open(PATH_TO_IMAGES + filename)
			image_np = load_image_into_numpy_array(image)

			# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
			image_np_expanded = np.expand_dims(image_np, axis=0)
			image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

			# Each box represents a part of the image where a particular object was detected.
			boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

			# Each score represent how level of confidence for each of the objects.
			# Score is shown on the result image, together with the class label.
			scores = detection_graph.get_tensor_by_name('detection_scores:0')
			classes = detection_graph.get_tensor_by_name('detection_classes:0')
			num_detections = detection_graph.get_tensor_by_name('num_detections:0')

			# Actual detection.
			(boxes, scores, classes, num_detections) = sess.run(
			    [boxes, scores, classes, num_detections],
			    feed_dict={image_tensor: image_np_expanded})

			# Visualization of the results of a detection.
			vis_util.visualize_boxes_and_labels_on_image_array(
			    image_np,
			    np.squeeze(boxes),
			    np.squeeze(classes).astype(np.int32),
			    np.squeeze(scores),
			    category_index,
			    use_normalized_coordinates=True,
			    line_thickness=8)

			image = Image.fromarray(image_np)
			os.remove(PATH_TO_IMAGES + filename)
			image.save(PATH_TO_IMAGES + filename)
			return