from pytz import timezone

DOCKER_IMAGES = {
    "cpu": {
        "tensorflow-0.12": "floydhub/tensorflow:latest-py3",
        "tensorflow-0.12:py2": "floydhub/tensorflow:latest-py2",
        "tensorflow-1.0": "floydhub/tensorflow:1.0.0-py3",
        "tensorflow-1.0:py2": "floydhub/tensorflow:1.0.0-py2",
        "tensorflow-1.1": "floydhub/tensorflow:1.1.0-py3",
        "tensorflow-1.1:py2": "floydhub/tensorflow:1.1.0-py2",
        "tensorflow": "floydhub/tensorflow:1.1.0-py3",
        "tensorflow:py2": "floydhub/tensorflow:1.1.0-py2",
        "keras": "floydhub/tensorflow:1.1.0-py3",
        "keras:py2": "floydhub/tensorflow:1.1.0-py2",
        "theano": "floydhub/theano:latest-py3",
        "theano:py2": "floydhub/theano:latest-py2",
        "caffe": "floydhub/caffe:latest-py3",
        "caffe:py2": "floydhub/caffe:latest-py2",
        "torch": "floydhub/torch:latest-py3",
        "torch:py2": "floydhub/torch:latest-py2",
        "pytorch": "floydhub/pytorch:latest-py3",
        "pytorch:py2": "floydhub/pytorch:latest-py2",
        "chainer": "floydhub/chainer:latest-py3",
        "chainer:py2": "floydhub/chainer:latest-py2",
        "mxnet:py2": "floydhub/mxnet:latest-py2",
        "kur": "floydhub/kur:latest-py3",
    },
    "gpu": {
        "tensorflow-0.12": "floydhub/tensorflow:latest-gpu-py3",
        "tensorflow-0.12:py2": "floydhub/tensorflow:latest-gpu-py2",
        "tensorflow-1.0": "floydhub/tensorflow:1.0.0-gpu-py3",
        "tensorflow-1.0:py2": "floydhub/tensorflow:1.0.0-gpu-py2",
        "tensorflow-1.1": "floydhub/tensorflow:1.1.0-gpu-py3",
        "tensorflow-1.1:py2": "floydhub/tensorflow:1.1.0-gpu-py2",
        "tensorflow": "floydhub/tensorflow:1.1.0-gpu-py3",
        "tensorflow:py2": "floydhub/tensorflow:1.1.0-gpu-py2",
        "keras": "floydhub/tensorflow:1.1.0-gpu-py3",
        "keras:py2": "floydhub/tensorflow:1.1.0-gpu-py2",
        "theano": "floydhub/theano:latest-gpu-py3",
        "theano:py2": "floydhub/theano:latest-gpu-py2",
        "caffe": "floydhub/caffe:latest-gpu-py3",
        "caffe:py2": "floydhub/caffe:latest-gpu-py2",
        "torch": "floydhub/torch:latest-gpu-py3",
        "torch:py2": "floydhub/torch:latest-gpu-py2",
        "pytorch": "floydhub/pytorch:latest-gpu-py3",
        "pytorch:py2": "floydhub/pytorch:latest-gpu-py2",
        "chainer": "floydhub/chainer:latest-gpu-py3",
        "chainer:py2": "floydhub/chainer:latest-gpu-py2",
        "mxnet:py2": "floydhub/mxnet:latest-gpu-py2",
        "kur": "floydhub/kur:latest-gpu-py3",
    }
}

DEFAULT_DOCKER_IMAGE = "floydhub/tensorflow:latest-py3"
DEFAULT_ENV = "default"
DEFAULT_ARCH = "cpu"

PST_TIMEZONE = timezone("America/Los_Angeles")

DEFAULT_FLOYD_IGNORE_LIST = """
# Directories and files to ignore when uploading code to floyd

.git
.eggs
eggs
lib
lib64
parts
sdist
var
*.pyc
*.swp
.DS_Store
"""

C1_INSTANCE_TYPE = 'c1'
G1_INSTANCE_TYPE = 'g1'
C1P_INSTANCE_TYPE = 'c1p'
G1P_INSTANCE_TYPE = 'g1p'
C2_INSTANCE_TYPE = 'c2'
G2_INSTANCE_TYPE = 'g2'

INSTANCE_ARCH_MAP = {
    C1_INSTANCE_TYPE: 'cpu',
    G1_INSTANCE_TYPE: 'gpu',
    C1P_INSTANCE_TYPE: 'cpu',
    G1P_INSTANCE_TYPE: 'gpu',
    C2_INSTANCE_TYPE: 'cpu',
    G2_INSTANCE_TYPE: 'gpu2',
}

INSTANCE_NAME_MAP = {
    C1_INSTANCE_TYPE: 'cpu',
    G1_INSTANCE_TYPE: 'gpu',
    C1P_INSTANCE_TYPE: 'cpu+',
    G1P_INSTANCE_TYPE: 'gpu+',
    C2_INSTANCE_TYPE: 'cpu2',
    G2_INSTANCE_TYPE: 'gpu2',
}

INSTANCE_TYPE_MAP = {
    INSTANCE_NAME_MAP[t]: t
    for t in INSTANCE_NAME_MAP
}

FIRST_STEPS_DOC = """
Start by cloning the sample project
    git clone https://github.com/floydhub/tensorflow-examples.git
    cd tensorflow-examples

And init a floyd project inside that.
    floyd init --project example-proj
"""
