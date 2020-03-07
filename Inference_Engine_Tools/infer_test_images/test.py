import os

configs = ['ssd_vs_faster',
           'faster_optimierungen_aug', 'faster_optimierungen_l2']

models_dir = os.path.join(
    os.environ['HOME'], 'Bachelor_Arbeit/openvino_models/Animals/')

test_config = {
    'ssd_vs_faster': [
        'ssd_inception_v2',
        'ssd_mobilenet_v2',
        'faster_rcnn_inception_v2_early_stopping',
        'faster_rcnn_inception_v2_early_stopping_ohne_aug'
    ],
    'faster_optimierungen_aug': [
        'faster_rcnn_inception_v2_early_stopping',
        'faster_rcnn_inception_v2_less_aug',
        'faster_rcnn_inception_v2_3000',
        'faster_rcnn_inception_v2_4000'
    ],
    'faster_optimierungen_l2': [
        'faster_rcnn_inception_v2_less_aug',
        'faster_rcnn_inception_v2_less_aug_l2',
        'faster_rcnn_inception_v2_3000',
        'faster_rcnn_inception_v2_l2'
    ]
}


for k, v in test_config.items():
    for model in os.listdir(models_dir):
        if not model in v:
            continue
        print(model)
    print()
