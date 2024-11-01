import mediapipe as mp
import sclera

mp_face_mesh = mp.solutions.face_mesh

image_path = 'face-image.jpg'
debug_path = 'debug-image.jpg'

l_locations, r_locations = sclera.get_sclera_location(mp_face_mesh, image_path, debug_path=debug_path)

print(len(l_locations))
print(len(r_locations))

if l_locations and r_locations:
    l_values, r_values = sclera.get_sclera_pixels(image_path, l_locations, r_locations)

print(len(l_values))
print(len(r_values))