import threading
import time

from src.common import config
from src.detection import detection

class DetectionWorker:
    def __init__(self, id):
        """Initializes this Detection Worker object's main thread."""
        self.TIMEOUT = 3

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True
        # self.model = detection.load_model()
        self.id = id

    def start(self):
        """Starts this Detection Worker's thread."""

        print('\n[~] Started Detection Worker')
        self.thread.start()

    def _main(self):
        """Polls the frame queue for work."""
        self.ready = True
        while True:
            if config.enabled and config.frame_queue.not_empty:
                self.classify_image()
            time.sleep(0.05)

    def classify_image(self):
        """Classifies image if result not found already."""
        frame = config.frame_queue.get()
        if config.detection_result is None and config.bot.rune_active:
            print(f'Worker {self.id} getting inference')
            detection_result = detection.merge_detection(config.model, frame)
            result_tuple = tuple(detection_result)

            if result_tuple in config.detection_inferences or (config.bot.NUM_DETECTION_WORKERS <= 1 and len(detection_result) == 4):
                print(f"Worker {self.id} got result {detection_result}")
                config.detection_result = detection_result
            elif len(detection_result) == 4:
                print(f"Worker {self.id} got inference {detection_result}")
                config.detection_inferences[result_tuple] = True

        config.frame_queue.task_done()
