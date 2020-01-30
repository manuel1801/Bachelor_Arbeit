import detection_v3 as detection
import os
import cv2
import subprocess

dataset_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit/dataset')
workspace_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit/workspace')
eval_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit/evaluation')
model_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit/models')


# Directories to Test images
flickr_images = os.path.join(dataset_dir, 'FlickrAnimals', 'Animals_9')
flickr_images_gray = os.path.join(
    dataset_dir, 'FlickrAnimals', 'Animals_9_gray')

validation_images = os.path.join(
    workspace_dir, 'OI_Animals_Augmented_9_2000', 'validation')

validation_images_gray = os.path.join(
    workspace_dir, 'OI_Animals_Augmented_9_2000_gray', 'validation_gray')

handy_images = os.path.join(workspace_dir, 'test')
handy_images_gray = os.path.join(workspace_dir, 'test_gray')

infer_images = {
    1: flickr_images,
    2: validation_images,
    3: handy_images,
    4: flickr_images_gray,
    5: validation_images_gray,
    6: handy_images_gray
}

for i in infer_images.items():
    print(i)
print('select image set')
infer_images_ind = int(input())
print(infer_images[infer_images_ind], ' selected')
assert os.path.isdir(infer_images[infer_images_ind])

model = {1: ['Samples', 'ssd_mobilenet_v2'],
         2: ['Samples', 'ssd_inception_v2'],
         3: ['Samples', 'faster_rcnn_inception_v2'],
         4: ['Samples', 'faster_rcnn_inception_v2_gray'],
         5: ['Animals', 'ssd_inception_v2'],
         6: ['Animals', 'faster_rcnn_inception_v2_3000'],
         7: ['Animals', 'faster_rcnn_inception_v2_gray'],
         8: ['Animals', 'faster_rcnn_inception_v2_gray_3000'],
         9: ['Animals', 'faster_rcnn_inception_v2_gray_geo'],
         10: ['Animals', 'faster_rcnn_inception_v2_geo'],
         12: ['Animals', 'ssd_mobilenet_oi']}

for m in model.items():
    print(m)
print('select model')
model_ind = int(input())
print(model[model_ind], ' selected')


def get_image_paths(imgs_dir):
    test_images = []
    for img_dir in os.listdir(imgs_dir):
        abs_img_dir = os.path.join(imgs_dir, img_dir)
        if img_dir[-3:] == 'jpg':
            test_images.append(abs_img_dir)
        elif os.path.isdir(abs_img_dir):
            for sub_img_dir in os.listdir(abs_img_dir):
                abs_sub_img_dir = os.path.join(abs_img_dir, sub_img_dir)
                if sub_img_dir[-3:] == 'jpg':
                    test_images.append(abs_sub_img_dir)
    return test_images


test_images = get_image_paths(infer_images[infer_images_ind])

infer_results = 'infer_results_' + \
    infer_images[infer_images_ind].split('/')[-1]
output_dir = os.path.join(eval_dir, infer_results,
                          model[model_ind][0], model[model_ind][1])
if not os.path.isdir(os.path.join(eval_dir, infer_results)):
    os.mkdir(os.path.join(eval_dir, infer_results))

if not os.path.isdir(os.path.join(eval_dir, infer_results, model[model_ind][0])):
    os.mkdir(os.path.join(eval_dir, infer_results,
                          model[model_ind][0]))


if not os.path.isdir(os.path.join(eval_dir, infer_results,
                                  model[model_ind][0], model[model_ind][1])):
    os.mkdir(os.path.join(eval_dir, infer_results,
                          model[model_ind][0], model[model_ind][1]))

infer_model = detection.InferenceModel()
exec_model = infer_model.create_exec_infer_model(model_dir,
                                                 model[model_ind][0],
                                                 model[model_ind][1],
                                                 num_requests=1,
                                                 conn_ip=None)

for test_image in test_images:
    image = cv2.imread(test_image)
    result = exec_model.infer_image(image)
    cv2.imwrite(os.path.join(
        output_dir, test_image.split('/')[-1][:-4] + '_' + model[model_ind][1] + '.jpg'), result)


dataset_eval_dir = os.path.join(eval_dir, infer_results, model[model_ind][0])
if not os.path.isdir(os.path.join(dataset_eval_dir, 'all')):
    os.mkdir(os.path.join(dataset_eval_dir, 'all'))
subprocess.Popen(['find', dataset_eval_dir, '-name', '*.jpg', '-exec', 'cp', '{}', os.path.join(dataset_eval_dir, 'all'), ';'],
                 stdout=subprocess.PIPE)
