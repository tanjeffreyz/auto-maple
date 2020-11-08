import numpy as np
import os
import tensorflow as tf
import cv2
from object_detection.utils import label_map_util


#################################
#       Global Variables        #
#################################
model_name = 'rune_model_rnn'


#################################
#        Initialization         #
#################################
model_dir = f'assets/models/{model_name}/saved_model'
detection_model = tf.saved_model.load(str(model_dir))
category_index = label_map_util.create_category_index_from_labelmap('assets/label_map.pbtxt', use_display_name=True)


#################################
#           Functions           #
#################################
def crop_and_canny(image):
    height, width, channels = image.shape
    image = cv2.Canny(image, 200, 300)
    cropped = image[:height//2,width//3:2*width//3]
    colored = cv2.cvtColor(cropped, cv2.COLOR_GRAY2BGR)
    return colored

def run_inference_for_single_image(model, image):
    image = np.asarray(image)

    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis,...]

    model_fn = model.signatures['serving_default']
    output_dict = model_fn(input_tensor)
    
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0,:num_detections].numpy() 
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
    return output_dict

def get_arrows(image):
    output_dict = run_inference_for_single_image(detection_model, image)
    zipped = list(zip(output_dict['detection_scores'], output_dict['detection_boxes'], output_dict['detection_classes']))
    pruned = [tuple for tuple in zipped if tuple[0] > 0.5]
    pruned.sort(key=lambda x: x[0], reverse=True)
    pruned = pruned[:4]
    pruned.sort(key=lambda x: x[1][1])
    classes = [category_index[tuple[2]]['name'] for tuple in pruned]
    return classes


# os.chdir('C:/Users/tanje/Desktop')
# desktop_files = [file for file in os.listdir() if os.path.isfile(file) and '.jpg' in file and 'test' in file]
# for file_name in desktop_files:
#     img = cv2.imread(file_name)
#     processed = crop_and_canny(img)
#     print(get_arrows(processed))