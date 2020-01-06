import time
import obj_det_asyc_class as infer_modul
import os
import cv2

workspace_dir = '/home/manuel/Bachelor_Arbeit/workspace'

inference = infer_modul.Inference(workspace_dir)
#inference.load_plugin('Beispiel_Set', 'ssd_mobilenet_v2_coco_out')
inference.load_plugin('OI_Animals_Augmented_9_2000',
                      'faster_rcnn_inception_v2_coco_2018_01_28_out')

test_images_dir = '/home/manuel/Bachelor_Arbeit/test'

# collect images


def collect_images(test_images_dir):
    if os.path.isdir(test_images_dir):
        images = [
            os.path.join(test_images_dir, img) for img in os.listdir(test_images_dir) if img[-3:] == 'jpg']
        print(str(len(images)) + ' images found')
        return images
        # shuffle(images)
    elif os.path.isfile(test_images_dir) and test_images_dir[-3:] == 'jpg':
        print('one image found')
        return images[test_images_dir]
    else:
        print('wrong input')
        return None


images = collect_images(test_images_dir)

for img_path in images:
    img = inference.infer_image(img_path, 0.5)
    cv2.imshow('image', img)
    if cv2.waitKey(0) == 113:
        break

test_images_dir = os.path.join(
    workspace_dir, 'OI_Animals_Augmented_9_2000', 'validation')
images = collect_images(test_images_dir)
for img_path in images:
    img = inference.infer_image(img_path, 0.5)
    cv2.imshow('image', img)
    if cv2.waitKey(0) == 113:
        break

inference.infer_stream(0, 0.6)

cv2.destroyAllWindows()
