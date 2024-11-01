import cv2
import math
import numpy as np

RGB_WHITE = (255, 255, 255)

LEFT_EYE = [362, 382, 381, 380, 374, 373, 390,
            249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154,
             155, 133, 173, 157, 158, 159, 160, 161, 246]

LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]


def euclidean_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def read_image(img_path):
    img = cv2.imread(img_path)
    if img_path.endswith('.png'):
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    elif img_path.endswith('.jpg'):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def get_sclera_location(mp_face_mesh, img_path, debug_path=None):

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        img = read_image(img_path)
        img_h, img_w = img.shape[:2]
        results = face_mesh.process(img)

        if results.multi_face_landmarks:

            mesh_points = np.array([
                np.multiply([p.x, p.y], [img_w, img_h]).astype(int) 
                for p in results.multi_face_landmarks[0].landmark
            ])

            hull_l_iris = cv2.convexHull(mesh_points[LEFT_IRIS]).squeeze()
            hull_r_iris = cv2.convexHull(mesh_points[RIGHT_IRIS]).squeeze()

            hull_l_eye = cv2.convexHull(mesh_points[LEFT_EYE]).squeeze()
            hull_r_eye = cv2.convexHull(mesh_points[RIGHT_EYE]).squeeze()

            xl, yl, wl, hl = cv2.boundingRect(mesh_points[LEFT_EYE])
            xr, yr, wr, hr = cv2.boundingRect(mesh_points[RIGHT_EYE])

            (l_cx, l_cy), l_radius = cv2.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), r_radius = cv2.minEnclosingCircle(mesh_points[RIGHT_IRIS])

            center_left = np.array([l_cx, l_cy], dtype=np.int32)
            center_right = np.array([r_cx, r_cy], dtype=np.int32)

            l_sclera = []
            r_sclera = []

            x1 = xl
            while x1 <= xl + wl:
                y1 = yl
                while y1 <= yl + hl:
                    if cv2.pointPolygonTest(hull_l_eye, (x1, y1), False) > 0:
                        if cv2.pointPolygonTest(hull_l_iris, (x1, y1), False) < 0:
                            if euclidean_distance(center_left, (x1, y1)) > l_radius:
                                l_sclera.append((x1, y1))
                                if debug_path:
                                    cv2.circle(img, (x1, y1), 1, RGB_WHITE, 1, cv2.LINE_AA)
                    y1 += 1
                x1 += 1

            x1 = xr
            while x1 < xr + wr:
                y1 = yr
                while y1 < yr + hr:
                    if cv2.pointPolygonTest(hull_r_eye, (x1, y1), False) > 0:
                        if cv2.pointPolygonTest(hull_r_iris, (x1, y1), False) < 0:
                            if euclidean_distance(center_right, (x1, y1)) > r_radius:
                                r_sclera.append((x1, y1))
                                if debug_path:
                                    cv2.circle(img, (x1, y1), 1, RGB_WHITE, 1, cv2.LINE_AA)
                    y1 += 1
                x1 += 1

            if debug_path:
                cv2.imwrite(debug_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

            return l_sclera, r_sclera

        else:
            return None, None
        

def get_sclera_pixels(imagepath, l_locations, r_locations):

    img = read_image(imagepath)

    l_sclera_pix_values = []
    r_sclera_pix_values = []

    for p in l_locations:
        l_sclera_pix_values.append(img[p[1], p[0]])

    for p in r_locations:
        r_sclera_pix_values.append(img[p[1], p[0]])

    l_sclera_pix_values = np.array(l_sclera_pix_values)
    r_sclera_pix_values = np.array(r_sclera_pix_values)

    return l_sclera_pix_values, r_sclera_pix_values