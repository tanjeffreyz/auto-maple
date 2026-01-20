"""
[視覺辨識模組]
這個模組負責使用 TensorFlow 和 OpenCV 來辨識畫面中的物件，
特別是用來解決遊戲中的「輪」(Rune) 箭頭謎題。
"""

import cv2
import tensorflow as tf
import numpy as np
from src.common import utils


#########################
#       功能函式        #
#########################
def load_model():
    """
    載入已儲存的 AI 模型權重到 Tensorflow 模型中。
    :return:    Tensorflow 模型物件。
    """

    model_dir = f'assets/models/rune_model_rnn_filtered_cannied/saved_model'
    return tf.saved_model.load(model_dir)


def canny(image):
    """
    對圖片執行 Canny 邊緣檢測。
    這會把圖片變成只有線條的樣子，幫助 AI 更容易辨識形狀。
    :param image:   輸入的圖片 (Numpy 陣列)。
    :return:        處理後的邊緣圖片。
    """

    image = cv2.Canny(image, 200, 300)
    colored = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return colored


def filter_color(image):
    """
    過濾掉不是橘色到綠色之間的顏色 (HSV 色彩空間)。
    這可以消除箭頭周圍的背景雜訊，讓箭頭更明顯。
    :param image:   輸入的圖片。
    :return:        過濾顏色後的圖片。
    """

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (1, 100, 100), (75, 255, 255))

    # 遮罩圖片 (只保留符合顏色的部分)
    color_mask = mask > 0
    arrows = np.zeros_like(image, np.uint8)
    arrows[color_mask] = image[color_mask]
    return arrows


def run_inference_for_single_image(model, image):
    """
    對單張圖片執行一次推論 (Inference)。
    也就是讓 AI 看這張圖，然後猜它是什麼。
    :param model:   要使用的模型物件。
    :param image:   輸入的圖片。
    :return:        模型的預測結果，包含邊界框 (bounding boxes) 和類別 (classes)。
    """

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
    """
    對圖片執行一次推論，並回傳信心度最高的四個分類結果。
    :param model:   要使用的模型物件。
    :param image:   輸入的圖片。
    :return:        模型的前四名預測結果。
    """

    output_dict = run_inference_for_single_image(model, image)
    zipped = list(zip(output_dict['detection_scores'],
                      output_dict['detection_boxes'],
                      output_dict['detection_classes']))
    # 過濾掉信心度低於 0.5 (50%) 的結果
    pruned = [t for t in zipped if t[0] > 0.5]
    # 依照信心度由高到低排序
    pruned.sort(key=lambda x: x[0], reverse=True)
    # 取前四個結果 (因為輪通常有四個箭頭)
    result = pruned[:4]
    return result


def get_boxes(model, image):
    """
    回傳前四個被分類出的箭頭的邊界框 (Bounding Boxes)。
    這可以用來定位箭頭在圖片中的位置。
    :param model:   要使用的模型物件。
    :param image:   輸入的圖片。
    :return:        最多四個邊界框。
    """

    output_dict = run_inference_for_single_image(model, image)
    zipped = list(zip(output_dict['detection_scores'],
                      output_dict['detection_boxes'],
                      output_dict['detection_classes']))
    pruned = [t for t in zipped if t[0] > 0.5]
    pruned.sort(key=lambda x: x[0], reverse=True)
    pruned = pruned[:4]
    boxes = [t[1:] for t in pruned]
    return boxes


@utils.run_if_enabled
def merge_detection(model, image):
    """
    執行兩次推論：一次是原本的直立圖片，一次是旋轉 90 度的圖片。
    只考慮垂直方向的箭頭，並將兩次推論的結果合併。
    (旋轉圖片中的垂直箭頭，其實就是原本圖片的水平箭頭)。
    這樣做通常能提高辨識準確度。
    :param model:   要使用的模型物件。
    :param image:   輸入的圖片。
    :return:        一個包含四個箭頭方向字串的清單。
    """

    label_map = {1: 'up', 2: 'down', 3: 'left', 4: 'right'}
    converter = {'up': 'right', 'down': 'left'}         # 用於轉換「旋轉後的推論結果」
    classes = []
    
    # 前處理 (Preprocessing)
    height, width, channels = image.shape
    # 裁切圖片，只保留可能出現輪的區域 (通常在螢幕中間偏上)
    cropped = image[120:height//2, width//4:3*width//4]
    filtered = filter_color(cropped)
    cannied = canny(filtered)

    # 隔離出輪的區域 (Rune Box)
    height, width, channels = cannied.shape
    boxes = get_boxes(model, cannied)
    if len(boxes) == 4:      # 只有在正確偵測到 4 個箭頭時才繼續
        y_mins = [b[0][0] for b in boxes]
        x_mins = [b[0][1] for b in boxes]
        y_maxes = [b[0][2] for b in boxes]
        x_maxes = [b[0][3] for b in boxes]
        left = int(round(min(x_mins) * width))
        right = int(round(max(x_maxes) * width))
        top = int(round(min(y_mins) * height))
        bottom = int(round(max(y_maxes) * height))
        rune_box = cannied[top:bottom, left:right]

        # 用黑色邊框填充輪的區域，這能有效消除周圍的雜訊
        height, width, channels = rune_box.shape
        pad_height, pad_width = 384, 455
        preprocessed = np.full((pad_height, pad_width, channels), (0, 0, 0), dtype=np.uint8)
        x_offset = (pad_width - width) // 2
        y_offset = (pad_height - height) // 2

        if x_offset > 0 and y_offset > 0:
            preprocessed[y_offset:y_offset+height, x_offset:x_offset+width] = rune_box

        # 對前處理後的圖片執行偵測
        lst = sort_by_confidence(model, preprocessed)
        # 依照 X 座標排序 (從左到右讀取箭頭)
        lst.sort(key=lambda x: x[1][1])
        classes = [label_map[item[2]] for item in lst]

        # 對旋轉後的圖片執行偵測
        rotated = cv2.rotate(preprocessed, cv2.ROTATE_90_COUNTERCLOCKWISE)
        lst = sort_by_confidence(model, rotated)
        # 依照 X 座標排序 (注意：這裡的座標因為旋轉過所以不同)
        lst.sort(key=lambda x: x[1][2], reverse=True)
        # 只取旋轉後辨識為 上(1) 或 下(2) 的結果，並轉換回原本的 右 或 左
        rotated_classes = [converter[label_map[item[2]]]
                           for item in lst
                           if item[2] in [1, 2]]
            
        # 合併兩次偵測的結果
        for i in range(len(classes)):
            # 如果原本辨識為 左 或 右，嘗試用旋轉後的結果替換 (因為模型對垂直箭頭辨識較準)
            if rotated_classes and classes[i] in ['left', 'right']:
                classes[i] = rotated_classes.pop(0)

    return classes


# 用來單獨測試偵測模組的腳本
if __name__ == '__main__':
    from src.common import config, utils
    import mss
    config.enabled = True
    monitor = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}
    model = load_model()
    while True:
        with mss.mss() as sct:
            frame = np.array(sct.grab(monitor))
            cv2.imshow('frame', canny(filter_color(frame)))
            arrows = merge_detection(model, frame)
            print(arrows)
            if cv2.waitKey(1) & 0xFF == 27:     # 27 是 Esc 鍵的 ASCII 碼
                break
