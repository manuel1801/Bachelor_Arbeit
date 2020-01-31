    for j, model in enumerate(os.listdir(os.path.join(models_dir, dataset))):
            selected_model[i+1] = dataset, model
            print(i+j+1, dataset, model)

