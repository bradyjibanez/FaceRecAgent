import face_recognition as fr
import cv2


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret,image = self.video.read()
        boxes = fr.face_locations(image)
        
        for box in boxes:
            """
                box[0] = top
                box[1] = right
                box[2] = bot
                box[3] = left
            """
            # Args - image, top-left coords, bottom-right coords, color(rgb), line thickness
            cv2.rectangle(image, (box[1], box[0]), (box[3],box[2]), (0,0, 255), 3)

        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()