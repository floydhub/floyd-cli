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

# SimCity4 Loading messages
# https://www.gamefaqs.com/pc/561176-simcity-4/faqs/22135
# Credits: EA Games
LOADING_MESSAGES = [
    "Adding Hidden Layers",
    "Adjusting Bell Curves",
    "Aesthesizing Industrial Grade Containers",
    "Aligning Covariance Matrices",
    "Applying Feng Shui Backprops",
    "Applying Theano Soda Layer",
    "Asserting Packed Exemplars",
    "Attempting to Lock Back-Buffer",
    "Binding Sampling Root System",
    "Breeding Neural Nets",
    "Building Deep Data Trees",
    "Bureacritizing Deep Learning Bureaucracies",
    "Calculating Inverse Probability Matrices",
    "Calculating SGD Expectoration Trajectory",
    "Calibrating Blue Skies",
    "Charging Ozone Layer",
    "Coalescing Cloud Formations",
    "Cohorting Exemplars",
    "Collecting Meteor Particles",
    "Compounding Inert Tessellations",
    "Compressing Fish Files",
    "Computing Optimal Bin Packing",
    "Concatenating Sub-Contractors",
    "Containing Existential Buffer",
    "Debarking Ark Ramp",
    "Debunching Unionized Commercial Services",
    "Deciding What Message to Display Next",
    "Decomposing Singular Values",
    "Decrementing Tectonic Plates",
    "Deleting Ferry Routes",
    "Depixelating Inner Mountain Surface Back Faces",
    "Depositing Slush Funds",
    "Destabilizing Economic Indicators",
    "Determining Width of Blast Fronts",
    "Deunionizing Bulldozers",
    "Dicing Trained Models",
    "Diluting Livestock Nutrition Variables",
    "Downloading Satellite Terrain Data",
    "Exposing Flash Variables to Streak System",
    "Extracting Gradient Resources",
    "Factoring Pay Scale",
    "Fixing Election Outcome Matrix",
    "Flood-Filling Ground Water",
    "Flushing Pipe Network",
    "Gathering Particle Sources",
    "Generating Scheduled Jobs",
    "Gesticulating Mimes",
    "Graphing Container Migration",
    "Hiding Willio Webnet Mask",
    "Implementing Impeachment Routine",
    "Increasing Accuracy of RCI Simulators",
    "Increasing Neural Magmafacation",
    "Initializing My Sim Tracking Mechanism",
    "Initializing CNN Timetable",
    "Initializing Robotic Click-Path AI",
    "Inserting Sublimated Messages",
    "Integrating Multidimensional Curves",
    "Integrating Illumination Form Factors",
    "Integrating Population Graphs",
    "Iterating Cellular Automata",
    "Lecturing Errant Subsystems",
    "Mixing Dropouts in Genetic Pool",
    "Modeling Object Components",
    "Mopping Occupant Leaks",
    "Normalizing Power",
    "Obfuscating Quigley Matrix",
    "Overconstraining Dirty Industry Calculations",
    "Partitioning City Grid Singularities",
    "Perturbing Matrices",
    "Pixalating Overfitting Patches",
    "Polishing Water Highlights",
    "Populating Lot Templates",
    "Preparing Sprites for Random Walks",
    "Prioritizing Landmarks",
    "Projecting Law Enforcement Pastry Intake",
    "Realigning Alternate Time Frames",
    "Reconfiguring User Mental Processes",
    "Relaxing Splines",
    "Removing Road Network Speed Bumps",
    "Removing Texture Gradients",
    "Removing Vehicle Avoidance Behavior",
    "Resolving GUID Conflict",
    "Reticulating Splines",
    "Retracting Phong Shader",
    "Retrieving from Back Store",
    "Reverse Engineering Image Consultant",
    "Routing Neural Network Infanstructure",
    "Scrubbing Terrain",
    "Searching for Llamas",
    "Seeding Architecture Simulation Parameters",
    "Sequencing Particles",
    "Setting Advisor Moods",
    "Setting Inner Deity Indicators",
    "Setting Universal Physical Constants",
    "Sonically Enhancing Occupant-Free Timber",
    "Speculating Stock Market Indices",
    "Splatting Transforms",
    "Stratifying Ground Layers",
    "Sub-Sampling Water Data",
    "Synthesizing Gravity",
    "Synthesizing Wavelets",
    "Time-Compressing Simulator Clock",
    "Unable to Reveal Current Activity",
    "Weathering Buildings",
    "Zeroing Crime Network"
]
