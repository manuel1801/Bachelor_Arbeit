import detect_images as detection
import os
import cv2
import subprocess

dataset_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit/Dataset')
workspace_dir = os.path.join(
    os.environ['HOME'], 'Bachelor_Arbeit/TensorFlow/workspace')
models_dir = os.path.join(
    os.environ['HOME'], 'Bachelor_Arbeit/openvino_models')

infer_model = detection.InferenceModel()

n = 200

# Aus Validierungsset
validation_images = os.path.join(
    workspace_dir, 'OI_Animals_Augmented_9_3000', 'validation')
validation_images_gray = os.path.join(
    workspace_dir, 'OI_Animals_Augmented_9_3000_gray', 'validation_gray')

assert os.path.isdir(validation_images)
assert os.path.isdir(validation_images_gray)


# Eigne Bilder
handy_images = os.path.join(workspace_dir, 'test')
handy_images_gray = os.path.join(workspace_dir, 'test_gray')

assert os.path.isdir(handy_images)
assert os.path.isdir(handy_images_gray)

handy_videos = os.path.join(dataset_dir, 'handy_videos/frames')
assert os.path.isdir(handy_videos)

kaggle_iWildCam = os.path.join(dataset_dir, 'kaggle_iWildCam')
assert os.path.isdir(kaggle_iWildCam)


# infer_images_list = [validation_images, validation_images_gray,
#                      handy_images, handy_images_gray, kaggle_iWildCam]


#infer_images_list = [kaggle_iWildCam]
infer_images_list = [handy_videos]


def get_image_paths(imgs_dir, max_images=None):  # hier shuffle
    test_images = []
    for img_dir in os.listdir(imgs_dir):
        abs_img_dir = os.path.join(imgs_dir, img_dir)
        if img_dir[-3:] == 'jpg':
            test_images.append(abs_img_dir)
        elif os.path.isdir(abs_img_dir):
            for i, sub_img_dir in enumerate(os.listdir(abs_img_dir)):
                abs_sub_img_dir = os.path.join(abs_img_dir, sub_img_dir)
                if sub_img_dir[-3:] == 'jpg':
                    test_images.append(abs_sub_img_dir)
                if max_images and i == max_images:
                    break
    return test_images


# dataset_dir = os.path.join(models_dir, 'Animals')
# labels = [l.strip() for l in open(os.path.join(
#     dataset_dir, 'classes.txt')).readlines()]

for dataset in os.listdir(models_dir):
    if dataset != 'Animals':
        continue
    dataset_dir = os.path.join(models_dir, dataset)
    if not os.path.isdir(dataset_dir):
        continue

    for model in os.listdir(dataset_dir):

        model_dir = os.path.join(dataset_dir, model)
        if not os.path.isdir(model_dir):
            continue
        print('starting ', model)
        model_xml = os.path.join(model_dir, 'frozen_inference_graph.xml')
        model_bin = os.path.join(model_dir, 'frozen_inference_graph.bin')

        if os.path.isfile(os.path.join(dataset_dir, 'classes.txt')):
            labels = [l.strip() for l in open(os.path.join(
                dataset_dir, 'classes.txt')).readlines()]
        else:
            labels = None

        exec_model = infer_model.create_exec_infer_model(
            model_xml, model_bin, labels, num_requests=3)

        for infer_images in infer_images_list:
            test_images = get_image_paths(infer_images, max_images=n)

            eval_dir = os.path.join(
                os.environ['HOME'], 'Bachelor_Arbeit/Inference_Engine_Tools/infer_test_images/results')
            if not os.path.isdir(eval_dir):
                os.mkdir(eval_dir)

            infer_results = 'infer_results_' + \
                infer_images.split('/')[-1]
            output_dir = os.path.join(eval_dir, infer_results, dataset, model)

            print('starting ', infer_results)

            if not os.path.isdir(os.path.join(eval_dir, infer_results)):
                os.mkdir(os.path.join(eval_dir, infer_results))

            if not os.path.isdir(os.path.join(eval_dir, infer_results, dataset)):
                os.mkdir(os.path.join(eval_dir, infer_results, dataset))

            if not os.path.isdir(os.path.join(eval_dir, infer_results,
                                              dataset, model)):
                os.mkdir(os.path.join(eval_dir, infer_results,
                                      dataset, model))

            for test_image in test_images:
                image = cv2.imread(test_image)
                result = exec_model.infer_image(image, threshhold=0.7)
                cv2.imwrite(os.path.join(
                    output_dir, test_image.split('/')[-1][:-4] + '_' + model + '.jpg'), result)

            dataset_eval_dir = os.path.join(
                eval_dir, infer_results, dataset)
            if not os.path.isdir(os.path.join(dataset_eval_dir, 'all')):
                os.mkdir(os.path.join(dataset_eval_dir, 'all'))
            subprocess.Popen(['find', dataset_eval_dir, '-name', '*.jpg', '-exec', 'mv', '{}', os.path.join(dataset_eval_dir, 'all'), ';'],
                             stdout=subprocess.PIPE)
