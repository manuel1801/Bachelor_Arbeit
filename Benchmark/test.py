import os
import cv2

workspace_dir = os.path.join(os.environ['HOME'], 'Bachelor_Arbeit')
test_image = cv2.imread(os.path.join(workspace_dir, 'Benchmark/car.png'))
models_dir = os.path.join(workspace_dir, 'openvino_models')

all_models = {}
i = 1
for dataset in os.listdir(models_dir):
    dataset_dir = os.path.join(models_dir, dataset)
    if os.path.isdir(dataset_dir):
        for model in os.listdir(dataset_dir):
            model_dir = os.path.join(dataset_dir, model)
            if os.path.isdir(model_dir):
                all_models[i] = dataset, model
                i += 1


for _, m in all_models.items():
    print(m)
