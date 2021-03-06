import numpy as np
import cv2
from utils.general_utils import get_class_from_id

palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)


def compute_color_for_labels(label):
    """
    Simple function that adds fixed color depending on the class
    """
    color = [int((p * (label ** 2 - label + 1)) % 255) for p in palette]
    return tuple(color)


def draw_boxes(img, bbox, identities=None, class_ids=None, offset=(0,0)):
    for i,box in enumerate(bbox):
        x1,y1,x2,y2 = [int(i) for i in box]
        x1 += offset[0]
        x2 += offset[0]
        y1 += offset[1]
        y2 += offset[1]
        # box text and bar
        id = int(identities[i]) if identities is not None else 0
        class_str = get_class_from_id(class_ids[i]) if not None else '?'
        color = compute_color_for_labels(id)
        label = '{}{:d}'.format("", id)
        t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 2 , 2)[0]
        cv2.rectangle(img,(x1, y1),(x2,y2),color,3)
        cv2.rectangle(img,(x1, y1),(x1+t_size[0]+3,y1+t_size[1]+4), color,-1)
        cv2.putText(img,label + '={}'.format(class_str),(x1,y1+t_size[1]+4), cv2.FONT_HERSHEY_PLAIN, 2, [255,255,255], 2)

    return img

def draw_lines(img, coordinates_l, identity):
    """
    coordinates_l : a list of coordinates
    """
    color = compute_color_for_labels(identity)
    coordinates_np = np.array(coordinates_l)

    if coordinates_np.shape[0] > 1:
        for i in range(len(coordinates_l) - 1):
            img = cv2.line(img, tuple(coordinates_np[i, :]), tuple(coordinates_np[i+1, :]), color, 12)
    return img

if __name__ == '__main__':
    for i in range(82):
        print(compute_color_for_labels(i))
