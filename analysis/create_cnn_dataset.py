import os
import numpy as np

# from lofarnn.data.datasets import create_variable_source_dataset
from lofarnn.utils.coco import create_cnn_dataset
from lofarnn.data.datasets import create_variable_source_dataset

try:
    environment = os.environ["LOFARNN_ARCH"]
except:
    os.environ["LOFARNN_ARCH"] = "XPS"
    environment = os.environ["LOFARNN_ARCH"]

if environment == "ALICE":
    dr_two = (
        "/home/s2153246/data/data/LoTSS_DR2/lofar-surveys.org/downloads/DR2/mosaics/"
    )
    vac = "/home/s2153246/data/catalogues/LOFAR_HBA_T1_DR1_merge_ID_optical_f_v1.2_restframe.fits"
    comp_cat = "/home/s2153246/data/catalogues/LOFAR_HBA_T1_DR1_merge_ID_v1.2.comp.fits"
    cutout_directory = "/home/s2153246/data/processed/variable_lgz_rotated/"
    pan_wise_location = "/home/s2153246/data/catalogues/pan_allwise.fits"
    multi_process = True
else:
    pan_wise_location = "/mnt/LargeSSD/hetdex_ps1_allwise_photoz_v0.6.fits"
    dr_two = "/mnt/LargeSSD/mosaics/"
    comp_cat = "/mnt/LargeSSD/LOFAR_HBA_T1_DR1_merge_ID_v1.2.comp.fits"
    vac = "/mnt/LargeSSD/LOFAR_HBA_T1_DR1_merge_ID_optical_f_v1.2_restframe.fits"
    cutout_directory = "/mnt/HDD/fixed_lgz_rotated/"
    multi_process = True

rotation = 180
size = (300.0 / 3600.0) * np.sqrt(2)
print(size)
'''
create_variable_source_dataset(
    cutout_directory=cutout_directory,
    pan_wise_location=pan_wise_location,
    value_added_catalog_location=vac,
    dr_two_location=dr_two,
    component_catalog_location=comp_cat,
    use_multiprocessing=multi_process,
    all_channels=True,
    filter_lgz=True,
    fixed_size=size,
    no_source=False,
    filter_optical=True,
    strict_filter=False,
    verbose=False,
    gaussian=False,
)
'''
create_cnn_dataset(
    root_directory=cutout_directory,
    pan_wise_catalog=pan_wise_location,
    rotation=rotation,
    convert=False,
    all_channels=True,
    vac_catalog=vac,
    normalize=True,
    segmentation=False,
    multi_rotate_only=vac,
    resize=None,
)
create_cnn_dataset(
    root_directory=cutout_directory,
    pan_wise_catalog=pan_wise_location,
    rotation=rotation,
    convert=False,
    all_channels=True,
    vac_catalog=vac,
    normalize=False,
    segmentation=False,
    multi_rotate_only=vac,
    resize=None,
)
