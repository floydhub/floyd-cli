from pytz import timezone

DOCKER_IMAGES = {
    "cpu": {
        "keras": "floydhub/keras:latest-py3",
        "keras:py2": "floydhub/keras:latest-py2",
        "tensorflow": "floydhub/tensorflow:latest-py3",
        "tensorflow-1.0": "floydhub/tensorflow:1.0.0-py3",
        "tensorflow:py2": "floydhub/tensorflow:latest-py2",
        "tensorflow-1.0:py2": "floydhub/tensorflow:1.0.0-py2",
        "caffe": "floydhub/caffe:latest-py3",
        "caffe:py2": "floydhub/caffe:latest-py2",
        "theano": "floydhub/theano:latest-py3",
        "theano:py2": "floydhub/theano:latest-py2",
        "torch": "floydhub/torch:latest-py3",
        "torch:py2": "floydhub/torch:latest-py2",
    },
    "gpu": {
        "keras": "floydhub/tensorflow:latest-gpu-py3",
        "keras:py2": "floydhub/tensorflow:latest-gpu-py2",
        "tensorflow": "floydhub/tensorflow:latest-gpu-py3",
        "tensorflow-1.0": "floydhub/tensorflow:1.0.0-gpu-py3",
        "tensorflow:py2": "floydhub/tensorflow:latest-gpu-py2",
        "tensorflow-1.0:py2": "floydhub/tensorflow:1.0.0-gpu-py2",
        "caffe": "floydhub/caffe:latest-gpu-py3",
        "caffe:py2": "floydhub/caffe:latest-gpu-py2",
        "theano": "floydhub/theano:latest-gpu-py3",
        "theano:py2": "floydhub/theano:latest-gpu-py2",
    }
}

DEFAULT_DOCKER_IMAGE = "tensorflow/tensorflow:0.12.1-py3"

PST_TIMEZONE = timezone("America/Los_Angeles")

DEFAULT_FLOYD_IGNORE_LIST = """
# Directories to ignore when uploading code to floyd
# Do not add a trailing slash for directories

.git
.eggs
eggs
lib
lib64
parts
sdist
var
"""

CPU_INSTANCE_TYPE = "cpu_high"
GPU_INSTANCE_TYPE = "gpu_high"

FIRST_STEPS_DOC = """
Start by cloning the sample project
    git clone https://github.com/floydhub/tensorflow-examples.git
    cd tensorflow-examples

And init a floyd project inside that.
    floyd init --project example-proj
"""
