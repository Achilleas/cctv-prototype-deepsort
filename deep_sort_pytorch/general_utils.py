import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance

def get_millis():
    """
    Get current time in milliseconds
    """
    return int(round(time.time() * 1000))

def get_millis_past(past_seconds=0):
    return int(round((time.time() - past_seconds) * 1000))

def get_class_from_id(id):
    classes_l = ['person',
                'bicycle',
                'car',
                'motorbike',
                'aeroplane',
                'bus',
                'train',
                'truck',
                'boat',
                'traffic light',
                'fire hydrant',
                'stop sign',
                'parking meter',
                'bench',
                'bird',
                'cat',
                'dog',
                'horse',
                'sheep',
                'cow',
                'elephant',
                'bear',
                'zebra',
                'giraffe',
                'backpack',
                'umbrella',
                'handbag',
                'tie',
                'suitcase',
                'frisbee',
                'skis',
                'snowboard',
                'sports ball',
                'kite',
                'baseball bat',
                'baseball glove',
                'skateboard',
                'surfboard',
                'tennis racket',
                'bottle',
                'wine glass',
                'cup',
                'fork',
                'knife',
                'spoon',
                'bowl',
                'banana',
                'apple',
                'sandwich',
                'orange',
                'broccoli',
                'carrot',
                'hot dog',
                'pizza',
                'donut',
                'cake',
                'chair',
                'sofa',
                'pottedplant',
                'bed',
                'diningtable',
                'toilet',
                'tvmonitor',
                'laptop',
                'mouse',
                'remote',
                'keyboard',
                'cell phone',
                'microwave',
                'oven',
                'toaster',
                'sink',
                'refrigerator',
                'book',
                'clock',
                'vase',
                'scissors',
                'teddy bear',
                'hair drier',
                'toothbrush']
    return classes_l[id]

def extract_rectangle_centers(rectangle_l):
    rectangle_center_l = []

    for rectangle in rectangle_l:
        x1,y1,x2,y2 = [int(i) for i in rectangle]

        x_avg = int(np.mean([x1, x2]))
        y_avg = int(np.mean([y1, y2]))

        rectangle_center_l.append([x_avg, y_avg])
    return rectangle_center_l

def extract_rectangle_vector_dl(rectangle_l):
    '''
    Extract from list of rectangles the general direction vector
    and starting location. Return as tuple (start_x, start_y), vec
    '''
    rectangle_center_l = extract_rectangle_centers(rectangle_l)

def distance_similarity_metric(reference_locs, loc, img_shape):
    '''
    Return distance similarity metric (1 for max similarity same location)
    '''
    distances = [distance.euclidean(rf_loc, loc) for rf_loc in reference_locs]

    #For each reference_loc calculate maximum possible distance
    max_x, max_y, c = img_shape

    #Pretty hacky but whatever
    edge_points = [[0, 0], [0, max_y], [max_x, 0], [max_x, max_y]]

    #print('REF LOCS:', reference_locs)
    #print('LOC', loc)
    #print('DISTANCES', distances)
    #print('REF MAX DIST ')

    norm_dist = np.copy(np.array(distances))
    max_dist = np.zeros([len(reference_locs)])
    for i, rf_loc in enumerate(reference_locs):
        #with reference location and edges of box what is the max distance
        max_dist[i] = np.max([distance.euclidean(edge_point, rf_loc) for edge_point in edge_points])

    #print('MAX DIST', max_dist)
    #print('NORM DIST', norm_dist)
    #divide distances by this value for corresponding ref dinstance
    norm_dist /= max_dist

    #Least normalized distance = More similarity
    sim_metric = 1 - np.min(norm_dist)
    #print('SIMILARITY METRIC value', sim_metric)
    return sim_metric

def direction_similarity_metric(reference_vectors, vector):
    '''
    Find maximum cosine cosine_similarity given metric
    '''
    #print('DOING DIRECTION SIMILARITY METRIC')
    #print(reference_vectors, 'vs', vector)
    similarities = [np.abs(cosine_similarity(np.array(rf_v).reshape(1, -1),
                                      np.array(vector).reshape(1,-1))[0]) for rf_v in reference_vectors]
    #print('similarities' , similarities)
    return np.max(similarities)

def dd_metric(reference_locs, reference_vectors, loc, vector, img_shape):
    dist_sim = distance_similarity_metric(reference_locs, loc, img_shape)
    direction_sim = direction_similarity_metric(reference_vectors, vector)

    #print('DIST SIM', dist_sim)
    #print('DIRECTION SIM', direction_sim)

    return 0.5*dist_sim + 0.5*direction_sim

def tracker_similarity_check(ref_loc_l, ref_vec_l, rectangle_l, img_shape, threshold=0.3):
    loc = extract_rectangle_centers([rectangle_l[0]])[0]
    vec = get_vector_from_rectangle_l(rectangle_l)

    #print('REC LIST', rectangle_l)
    #print('VEC', vec)
    #print('LOC', loc)

    dd_metric_val = dd_metric(ref_loc_l, ref_vec_l, loc, vec, img_shape)

    #print('DD METRI VAL', dd_metric_val)

    if dd_metric_val < threshold:
        return False, dd_metric_val
    return True, dd_metric_val

def get_vector_from_rectangle_l(rectangle_l):
    '''
    Given a set of boxes, calculate center point of each box.
    Then take vector between first and last spot
    '''
    rec_centers = extract_rectangle_centers([rectangle_l[0], rectangle_l[1]])
    #print('REC CENTERS', rec_centers)
    vec = np.array(rec_centers[1]) - np.array(rec_centers[0])
    return vec / np.linalg.norm(vec)
