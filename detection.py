import tensorflow as tf
import numpy as np
import cv2


#########################
#       Functions       #
#########################
def load_model():
    model_dir = f'assets/models/rune_model_rnn_filtered_cannied/saved_model'
    model = tf.saved_model.load(model_dir)
    return model

def canny(image):
    image = cv2.Canny(image, 200, 300)
    colored = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return colored

def filter_color(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (1, 100, 100), (75, 255, 255))

    # Mask the image
    imask = mask > 0
    arrows = np.zeros_like(image, np.uint8)
    arrows[imask] = image[imask]
    return arrows

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

def sort_by_confidence(model, image):
    output_dict = run_inference_for_single_image(model, image)
    zipped = list(zip(output_dict['detection_scores'], output_dict['detection_boxes'], output_dict['detection_classes']))
    pruned = [tuple for tuple in zipped if tuple[0] > 0.5]
    pruned.sort(key=lambda x: x[0], reverse=True)
    result = pruned[:4]
    return result

def merge_detection(image):
    label_map = {1: 'up', 2: 'down', 3: 'left', 4: 'right'}
    converter = {'up': 'right', 'down': 'left'}
    
    # Preprocessing
    height, width, channels = image.shape
    cropped = image[:height//2,width//4:3*width//4]
    filtered = filter_color(cropped)
    cannied = canny(filtered)

    # Run detection on preprocessed image
    lst = sort_by_confidence(detection_model, cannied)
    lst.sort(key=lambda x: x[1][1])
    classes = [label_map[item[2]] for item in lst]

    # Run detection rotated image
    rotated = cv2.rotate(cannied, cv2.ROTATE_90_COUNTERCLOCKWISE)
    lst = sort_by_confidence(detection_model, rotated)
    lst.sort(key=lambda x: x[1][2], reverse=True)
    rotated_classes = [converter[label_map[item[2]]]
                       for item in lst
                       if item[2] in [1, 2]]
        
    # Merge the two detection results
    for i in range(len(classes)):
        if rotated_classes and classes[i] in ['left', 'right']:
            classes[i] = rotated_classes.pop(0)

    return classes


#############################
#       Initialization      #
#############################
detection_model = load_model()

# Run the inference once to 'warm up' tensorflow (the first detection triggers a long setup process)
test_image = cv2.imread('assets/inference_test_image.jpg')
merge_detection(test_image)
print('Loaded detection model')


# import os
# os.chdir('C:/Users/tanje/Desktop/')

# files = [file for file in os.listdir() if os.path.isfile(file) and '.jpg' in file]
# for file_name in files:
#     img = cv2.imread(file_name)
#     print(merge_detection(img), '\n')

# import mss, time

# monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
# while True:
#     with mss.mss() as sct:
#         frame = np.array(sct.grab(monitor))
#         frame = frame[:768,:1366]
#         cv2.imshow('frame', frame)
#         arrows = merge_detection(frame)
#         print(arrows)
#         if cv2.waitKey(1) & 0xFF == 27:     # 27 is ASCII for the Esc key
#             break
        