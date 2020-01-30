checkpoint_dir=$1   # absolut
model=$2            # nur name ordner in eval/
eval_conf=$3        # name von config und record file in eval/model (ohne endung)


python3 /home/manuel/Bachelor_Arbeit/TensorFlow_Models/object_detection/legacy/eval.py \
--logtostderr \
--checkpoint_dir $checkpoint_dir \
--eval_dir /home/manuel/Bachelor_Arbeit/evaluation/eval/results/$output/$eval_conf \
--pipeline_config_path /home/manuel/Bachelor_Arbeit/evaluation/eval/$model/${eval_conf}.config

