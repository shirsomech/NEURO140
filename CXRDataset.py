from abc import abstractmethod
import torchvision
from torch.utils.data import Dataset
import torchvision.transforms as transforms
import pandas as pd
import os
import matplotlib.pyplot as plt
from enum import Enum
from utils import file_operations
import zipfile
from PIL import Image 
import io

class CXRLabel(Enum):
    NORMAL = 0
    ABNORMAL = 1

class CXRDataset(Dataset):
  def __init__(self, archive_file, config=None):
    self.archive_file = archive_file
    self.image_to_label = {}
    self.inner_datasets = {}
    self.extract_data(config)
    self.items = list(self.image_to_label.items())

  @abstractmethod
  def extract_data(self, **kwargs):
    raise NotImplementedError

  @abstractmethod
  def __getitem__(self, idx):
    raise NotImplementedError
    
  def __len__(self):
    return len(self.items)

class VinXRay(CXRDataset):
  """
  └── VinXRay/
      ├── Images/
      ├── vietnam_test.csv
      ├── vietnam_train.csv
      └── vietnam_val.csv
  """
  
  def __init__(self, config=None):
    super().__init__("datasets/VinXRay.zip")

  def __getitem__(self, idx):
      img_path, label = self.items[idx]
      with open(img_path, "rb") as file:
        img = Image.open(io.BytesIO(file.read()))
        
        transform = transforms.Compose([
          transforms.RandomResizedCrop(224),
          #transforms.RandomHorizontalFlip(),
          transforms.ToTensor(),
          transforms.Grayscale()
        ])

        img = transform(img)

        return img, label.value

  def extract_data(self, config):
    with zipfile.ZipFile(self.archive_file, "r") as zip_ref:
      zip_ref.extractall()

    self.inner_datasets = {'test':[], 'train':[], 'val':[]}
    image_dir = os.path.join(os.getcwd(), 'vinxray', "train")
    for category in self.inner_datasets.keys():
      metadata_file = os.path.join(os.getcwd(), 'vinxray', f'vietnam_{category}.csv')
      metadata = pd.read_csv(metadata_file)
      for index, row in metadata.iterrows():
        image_path = row['full_path'][1:]
        file_path = os.getcwd() + image_path
        if file_operations.is_valid_image_file(file_path):
          # Read the image file from the zip
          with open(file_path, "rb") as file:
            try:
              img_data = file.read()
              img = Image.open(io.BytesIO(img_data))
              img.verify()
              self.inner_datasets[category].append(row['full_path'])
              label = CXRLabel.NORMAL if row['class_name'] == 'No finding' else CXRLabel.ABNORMAL 
              self.image_to_label[file_path] = label

            except (IOError, SyntaxError) as e:
              logging.info(f"Invalid image file {filename}: {e}, skipping..")
              continue


class COVID19_Radiography(CXRDataset):
  """
  └── COVID-19_Radiography_Dataset/
      ├── COVID/
      │   ├── images/
      │   └── masks/
      ├── COVID.metadata.xlsx
      ├── Lung Opacity/
      │   ├── images/
      │   └── masks/
      ├── Lung_Opacity.metadata.xlsx
      ├── Viral Pneumonia/
      │   ├── images/
      │   └── masks/
      ├── Viral Pneumonia.metadata.xlsx
      ├── Normal/
      │   ├── images/
      │   └── masks/
      ├── Normal.metadata.xlsx
      └── README.md.txt
    """

  class Datasets(Enum):
    NORMAL_1 = 1
    NORMAL_2 = 2
    COVID_1 = 3
    COVID_2 = 4
    COVID_3 = 5
    COVID_4 = 6
    COVID_5 = 7
    COVID_6 = 8
    LO_1 = 9
    VP_1 = 10

  DATASET_TO_INDEX = {
    'Normal_https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/data': Datasets.NORMAL_1,
    'Normal_https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia': Datasets.NORMAL_2,
    'COVID_https://sirm.org/category/senza-categoria/covid-19/': Datasets.COVID_1,
    'COVID_https://github.com/ml-workgroup/covid-19-image-repository/tree/master/png': Datasets.COVID_2,
    'COVID_https://eurorad.org': Datasets.COVID_3,
    'COVID_https://github.com/armiro/COVID-CXNet' : Datasets.COVID_4,
    'COVID_https://github.com/ieee8023/covid-chestxray-dataset': Datasets.COVID_5,
    'COVID_https://bimcv.cipf.es/bimcv-projects/bimcv-covid19/#1590858128006-9e640421-6711': Datasets.COVID_6,
    'Lung_Opacity_https://www.kaggle.com/c/rsna-pneumonia-detection-challenge/data': Datasets.LO_1,
    'Viral Pneumonia_https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia': Datasets.VP_1
  }

  def __init__(self, config=None):
    super().__init__("datasets/COVID-19_Radiography.zip")

  def __getitem__(self, idx):
      img_path, label = self.items[idx]
      with open(img_path, "rb") as file:
        img = Image.open(io.BytesIO(file.read()))
        
        transform = transforms.Compose([
          transforms.RandomResizedCrop(224),
          #transforms.RandomHorizontalFlip(),
          transforms.ToTensor(),
          transforms.Grayscale()
        ])

        img = transform(img)

        return img, label.value

  def extract_data(self, config):
    self.normal = ["Normal"]
    self.abnormal = ["COVID", "Lung_Opacity", "Viral Pneumonia"]
    images_directories = []

    with zipfile.ZipFile(self.archive_file, "r") as zip_ref:
      zip_ref.extractall()

    for category in (self.normal + self.abnormal):
      metadata_file = os.path.join(os.getcwd(), 'COVID-19_Radiography_Dataset', f'{category}.metadata.xlsx')
      image_dir = os.path.join(os.getcwd(), 'COVID-19_Radiography_Dataset', category, 'images')
      metadata = pd.read_excel(metadata_file)
      for index, row in metadata.iterrows():
        dataset_id = f"{category}_{row['URL']}"
        if dataset_id not in self.inner_datasets:
          # Encountered new dataset
          self.inner_datasets[dataset_id] = []
        file_path = os.path.join(image_dir, f"{row['FILE NAME']}.png")
        if file_operations.is_valid_image_file(file_path):
          # Read the image file from the zip
          with open(file_path, "rb") as file:
            try:
              img_data = file.read()
              img = Image.open(io.BytesIO(img_data))
              img.verify()
              self.inner_datasets[dataset_id].append(file_path)
              if not config or self.DATASET_TO_INDEX[dataset_id] in config:
                self.image_to_label[file_path] = CXRLabel.NORMAL if category in self.normal else CXRLabel.ABNORMAL
            except (IOError, SyntaxError) as e:
              logging.info(f"Invalid image file {filename}: {e}, skipping..")
              continue

          


              