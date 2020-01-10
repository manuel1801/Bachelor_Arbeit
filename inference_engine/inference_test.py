import obj_det_asyc_class
import os
import cv2
import connection

dataset_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit/dataset')
workspace_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit/workspace')
eval_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit/evaluation')
test_images = []

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

model = {1: ['Beispiel_Set', 'ssd_inception_v2_coco_out'],
         2: ['Beispiel_Set', 'ssd_mobilenet_v2_coco_out'],
         3: ['Beispiel_Set_Aug_gray', 'faster_rcnn_inception_v2_coco_2018_01_28_out'],
         4: ['OI_Animals_Augmented_9_2000', 'ssd_mobilenet_v2_coco_2018_03_29_out'],
         5: ['OI_Animals_Augmented_9_2000', 'ssd_inception_v2_coco_2018_01_28_out'],
         6: ['OI_Animals_Augmented_9_2000', 'faster_rcnn_inception_v2_coco_2018_01_28_out'],
         7: ['OI_Animals_Augmented_9_2000_gray', 'faster_rcnn_inception_v2_coco_2018_01_28_out_gray_opencv']}


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


# infer_images_ind = 6  # handy gry

for infer_images_ind in range(2, 4):

    for model_ind in range(4, 7):

            # get test image paths
        test_images = get_image_paths(infer_images[infer_images_ind])

        # start inferenc engine
        inference = obj_det_asyc_class.Inference(workspace_dir)
        inference.load_plugin(model[model_ind][0], model[model_ind][1])

        # create output dir
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

        # infer all images
        if test_images:
            for i in range(len(test_images)):
                img = inference.infer_image(test_images[i], threshhold=0.5)
                # cv2.imshow('infered image', img)
                if i > 0:  # erstes bild wird nicht inferiert
                    cv2.imwrite(os.path.join(
                        output_dir, test_images[i-1].split('/')[-1][:-4] + '_' + model[model_ind][1] + '.jpg'), img)
                # if cv2.waitKey(0) == 113:
                #     break

        else:
            inference.infer_stream(input_stream=0, threshhold=0.5,
                                   save_image_files=True, save_time_in_sec=20)
