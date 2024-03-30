DATASET_PATHS = [
    "datasets/COVID-19_Radiography.zip",
    "datasets/VinXRay.zip"
]
MODELS_DIR_NAME = "models"

# TRAINING SETTINGS
NUM_EPOCHS = 1

# LEARNING RATE SETTINGS
BASE_LR = 0.0001
DECAY_WEIGHT = 0.1 
EPOCH_DECAY = 30 

# DATASET INFO
NUM_CLASSES = 2

# DATALOADER PROPERTIES
BATCH_SIZE = 64
NUM_WORKERS = 8

TARGET_SITE_PERCENTAGE_IN_TESTING_DATASET = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
