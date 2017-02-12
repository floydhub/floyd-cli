from pytz import timezone

DOCKER_IMAGES = {
    "cpu": {
        "default": "tensorflow/tensorflow:0.12.1-py3",
        "tensorflow_py3": "tensorflow/tensorflow:0.12.1-py3",
        "tensorflow_py2": "tensorflow/tensorflow:0.12.1",
    },
    "gpu": {
        "default": "tensorflow/tensorflow:0.12.1-gpu-py3",
        "tensorflow_py3": "tensorflow/tensorflow:0.12.1-gpu-py3",
        "tensorflow_py2": "tensorflow/tensorflow:0.12.1-gpu",
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
