from openvino.inference_engine import IENetwork, IECore
import os
from time import time

ie = IECore()

workspace_dir = '/home/manuel/Bachelor_Arbeit/'
models_dir = os.path.join(
    workspace_dir, 'openvino_models/Animals/faster_rcnn_inception_v2_l2')


model_xml = os.path.join(
    models_dir,  'frozen_inference_graph.xml')
model_bin = os.path.join(
    models_dir,  'frozen_inference_graph.bin')
model_export = os.path.join(models_dir, 'faster_export')

export = False

if export:
    # export
    net = IENetwork(model_xml, model_bin)
    exec_net = ie.load_network(net, num_requests=2, device_name='MYRIAD')

    print(type(exec_net))

    exec_net.export(model_export)

    del exec_net
else:
    # import
    t_start = time()
    exec_net = ie.import_network(model_file=model_export, device_name='MYRIAD')
    print(time() - t_start)

    print(type(exec_net))
