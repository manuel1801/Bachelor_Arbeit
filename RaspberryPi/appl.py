import obj_det_asyc_class as infer_modul
import os
import cv2
import connection_non_blocking as conn

# select model
model_dir = 'models'
test_dir = 'test'
dataset = 'Samples'
model_ind = 2
model = {
    'Samples':
        ['faster_inception',
         'ssd_mobilenet_v2',
         'faster_rcnn_inception_v2_gray'],
    'Animals':
        ['faster_rcnn_inception_v2',
         'faster_rcnn_inception_v2_gray',
         'ssd_inception_v2',
         'ssd_mobilenet_v2']
}

# start inferenc engine
inference = infer_modul.Inference(model_dir)
inference.load_plugin(dataset, model[dataset][model_ind])


# infer images
images = [
    os.path.join(test_dir, img) for img in os.listdir(test_dir) if img[-3:] == 'jpg']
for img_path in images:
    img = inference.infer_image(img_path, threshhold=0.5)
    cv2.imshow('image', img)
    if cv2.waitKey(0) == 113:
        break

# infer camera input
# inference.infer_stream(0, 0.5)
