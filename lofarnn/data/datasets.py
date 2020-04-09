import multiprocessing
import os

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
from astropy.wcs.utils import skycoord_to_pixel
from itertools import repeat
from scipy.ndimage.filters import gaussian_filter

from lofarnn.utils.coco import create_coco_style_directory_structure
from lofarnn.visualization.cutouts import plot_three_channel_debug
from lofarnn.utils.fits import extract_subimage


def get_lotss_objects(fname, verbose=False):
    """
    Load the LoTSS objects from a file
    """

    with fits.open(fname) as hdul:
        table = hdul[1].data

    if verbose:
        print(table.columns)

    # convert from astropy.io.fits.fitsrec.FITS_rec to astropy.table.table.Table
    return Table(table)


def pad_with(vector, pad_width, iaxis, kwargs):
    """
    Taken from Numpy documentation, will pad with zeros to make lofar image same size as other image
    :param vector:
    :param pad_width:
    :param iaxis:
    :param kwargs:
    :return:
    """
    pad_value = kwargs.get('padder', 0)
    vector[:pad_width[0]] = pad_value
    vector[-pad_width[1]:] = pad_value
    return vector


def make_layer(value, value_error, size, non_uniform=False):
    """
    Creates a layer based on the value and the error, if non_uniform is True.

    Designed for adding catalogue data to image stacks

    :param value:
    :param value_error:
    :param size:
    :param non_uniform:
    :return:
    """

    if non_uniform:
        return np.random.normal(value, value_error, size=size)
    else:
        return np.full(shape=size, fill_value=value)


def determine_visible_catalogue_sources(ra, dec, wcs, size, catalogue, l_objects, verbose=False):
    """
    Find the sources in the catalogue that are visible in the cutout, and returns a smaller catalogue for that
    :param ra: Radio RA
    :param dec: Radio DEC
    :param wcs: WCS of Radio FITS files
    :param size: Size of cutout in degrees
    :param catalogue: Pan-AllWISE catalogue
    :param l_objects: LOFAR Value Added Catalogue objects
    :return: Subcatalog of catalogue that only contains sources near the radio source in the cutout size, as well as
    SkyCoord of their world coordinates
    """
    try:
        ra_array = np.array(catalogue['ra'], dtype=float)
        dec_array = np.array(catalogue['dec'], dtype=float)
    except:
        ra_array = np.array(catalogue['ID_ra'], dtype=float)
        dec_array = np.array(catalogue['ID_dec'], dtype=float)
    sky_coords = SkyCoord(ra_array, dec_array, unit='deg')

    source_coord = SkyCoord(ra, dec, unit='deg')
    other_source = SkyCoord(l_objects['ID_ra'], l_objects['ID_dec'], unit="deg")
    search_radius = size * u.deg
    d2d = source_coord.separation(sky_coords)
    catalogmask = d2d < search_radius
    idxcatalog = np.where(catalogmask)[0]
    objects = catalogue[idxcatalog]

    if verbose:
        print(source_coord)
        print(other_source)
        print(skycoord_to_pixel(source_coord, wcs, 0))
        print(skycoord_to_pixel(other_source, wcs, 0))

    return objects


def make_catalogue_layer(column_name, wcs, shape, catalogue, gaussian=None, verbose=False):
    """
    Create a layer based off the data in
    :param column_name: Name in catalogue of data to include
    :param shape: Shape of the image data
    :param wcs: WCS of the Radio data, so catalog data can be translated correctly
    :param catalogue: Catalogue to query
    :param gaussian: Whether to smooth the point values with a gaussian
    :return: A Numpy array that holds the information in the correct location
    """

    ra_array = np.array(catalogue['ra'], dtype=float)
    dec_array = np.array(catalogue['dec'], dtype=float)
    sky_coords = SkyCoord(ra_array, dec_array, unit='deg')

    # Now have the objects, need to convert those RA and Decs to pixel coordinates
    layer = np.zeros(shape=shape)
    coords = skycoord_to_pixel(sky_coords, wcs, 0)
    for index, x in enumerate(coords[0]):
        try:
            if ~np.isnan(catalogue[index][column_name]) and catalogue[index][
                column_name] > 0.0:  # Make sure not putting in NaNs
                layer[int(np.floor(coords[0][index]))][int(np.floor(coords[1][index]))] = catalogue[index][column_name]
        except Exception as e:
            if verbose:
                print(f"Failed: {e}")
    if gaussian is not None:
        layer = gaussian_filter(layer, sigma=gaussian)
    return layer

def make_proposal_boxes(wcs, shape, catalogue, gaussian=None):
    """
   Create Faster RCNN proposal boxes for all sources in the image

   The sky_coords seems to be swapped x and y on the boxes, so should be swapped here too
   :param column_name: Name in catalogue of data to include
   :param shape: Shape of the image data
   :param wcs: WCS of the Radio data, so catalog data can be translated correctly
   :param catalogue: Catalogue to query
   :param gaussian: Whether to smooth the point values with a gaussian
   :return: A Numpy array that holds the information in the correct location
   """

    ra_array = np.array(catalogue['ra'], dtype=float)
    dec_array = np.array(catalogue['dec'], dtype=float)
    sky_coords = SkyCoord(ra_array, dec_array, unit='deg')

    # Now have the objects, need to convert those RA and Decs to pixel coordinates
    proposals = []
    coords = skycoord_to_pixel(sky_coords, wcs, 0)
    for index, x in enumerate(coords[0]):
        try:
            proposals.append(make_bounding_box(ra_array[index], dec_array[index], wcs=wcs, class_name="Proposal Box", gaussian=gaussian))
        except Exception as e:
            print(f"Failed Proposal: {e}")
    return proposals

def make_bounding_box(ra, dec, wcs, class_name="Optical source", gaussian=None):
    """
    Creates a bounding box and returns it in (xmin, ymin, xmax, ymax, class_name) format
    :param class_name: Class name for the bounding box
    :param ra: RA of the object to make bounding box
    :param dec: Dec of object
    :param wcs: WCS to convert to pixel coordinates
    :param gaussian: Whether gaussian is being used, in which case the box is not int'd but left as a float, and the
    width of the gaussian is used for the width of the bounding box, if it is being used, instead of 'None', it should
    be the width of the Gaussian
    :return: Bounding box coordinates for COCO style annotation
    """
    source_skycoord = SkyCoord(ra, dec, unit='deg')
    box_center = skycoord_to_pixel(source_skycoord, wcs, 0)
    if gaussian is None:
        # Now create box, which will be accomplished by taking int to get xmin, ymin, and int + 1 for xmax, ymax
        xmin = int(np.floor(box_center[0])) - 0.5
        ymin = int(np.floor(box_center[1])) - 0.5
        ymax = ymin + 1
        xmax = xmin + 1
    else:
        xmin = int(np.floor(box_center[0])) - gaussian
        ymin = int(np.floor(box_center[1])) - gaussian
        xmax = np.ceil(int(np.floor(box_center[0])) + gaussian)
        ymax = np.ceil(int(np.floor(box_center[1])) + gaussian)

    return xmin, ymin, xmax, ymax, class_name, box_center


def create_cutouts(mosaic, value_added_catalog, pan_wise_catalog, mosaic_location,
                   save_cutout_directory, gaussian=None, all_channels=False, source_size=None, verbose=False):
    """
    Create cutouts of all sources in a field
    :param mosaic: Name of the field to use
    :param value_added_catalog: The VAC of the LoTSS data release
    :param pan_wise_catalog: The PanSTARRS-ALLWISE catalogue used for Williams, 2018, the LoTSS III paper
    :param mosaic_location: The location of the LoTSS DR2 mosaics
    :param save_cutout_directory: Where to save the cutout npy files
    :param all_channels: Whether to include all possible channels (grizy,W1,2,3,4 bands) in npy file or just (radio,i,W1)
    :param fixed_size: Whether to use fixed size cutouts, in arcseconds, or the LGZ size (default: LGZ)
    :param verbose: Whether to print extra information or not
    :return:
    """
    lofar_data_location = os.path.join(mosaic_location, mosaic, "mosaic-blanked.fits")
    lofar_rms_location = os.path.join(mosaic_location, mosaic, "mosaic.rms.fits")
    if gaussian is False:
        gaussian = None
    if type(pan_wise_catalog) == str:
        print("Trying To Open")
        pan_wise_catalog = fits.open(pan_wise_catalog, memmap=True)
        pan_wise_catalog = pan_wise_catalog[1].data
        print("Opened Catalog")
    # Load the data once, then do multiple cutouts
    try:
        fits.open(lofar_data_location, memmap=True)
        fits.open(lofar_rms_location, memmap=True)
    except:
        if verbose:
            print(f"Mosaic {mosaic} does not exist!")

    mosaic_cutouts = value_added_catalog[value_added_catalog["Mosaic_ID"] == mosaic]
    # Go through each cutout for that mosaic
    for l, source in enumerate(mosaic_cutouts):
        if not os.path.exists(os.path.join(save_cutout_directory, source['Source_Name'])):
            img_array = []
            # Get the ra and dec of the radio source
            source_ra = source["RA"]
            source_dec = source["DEC"]
            # Get the size of the cutout needed
            if source_size is None or source_size is False:
                source_size = (source["LGZ_Size"] * 1.5) / 3600.  # in arcseconds converted to archours
            try:
                lhdu = extract_subimage(lofar_data_location, source_ra, source_dec, source_size, verbose=verbose)
            except:
                if verbose:
                    print(f"Failed to make data cutout for source: {source['Source_Name']}")
                continue
            try:
                lrms = extract_subimage(lofar_rms_location, source_ra, source_dec, source_size, verbose=verbose)
            except:
                if verbose:
                    print(f"Failed to make rms cutout for source: {source['Source_Name']}")
                continue
            img_array.append(lhdu[0].data / lrms[0].data)  # Makes the Radio/RMS channel
            header = lhdu[0].header
            wcs = WCS(header)

            # Now time to get the data from the catalogue and add that in their own channels
            if verbose:
                print(f"Image Shape: {img_array[0].data.shape}")
            # Should now be in Radio/RMS, i, W1 format, else we skip it
            # Need from catalog ra, dec, iFApMag, w1Mag, also have a z_best, which might or might not be available for all
            if all_channels:
                layers = ["iFApMag", "w1Mag", "gFApMag", "rFApMag", "zFApMag", "yFApMag", "w2Mag", "w3Mag", "w4Mag"]
            else:
                layers = ["iFApMag", "w1Mag"]
            # Get the catalog sources once, to speed things up
            # cuts size in two to only get sources that fall within the cutout, instead of ones that go twice as large
            cutout_catalog = determine_visible_catalogue_sources(source_ra, source_dec, wcs, source_size/2,
                                                                 pan_wise_catalog, source)
            # Now determine if there are other sources in the area
            other_visible_sources = determine_visible_catalogue_sources(source_ra, source_dec, wcs, source_size/2,
                                                                        mosaic_cutouts, source)

            # Now make proposal boxes
            proposal_boxes = np.asarray(make_proposal_boxes(wcs, img_array[0].shape, cutout_catalog, gaussian=gaussian))
            for layer in layers:
                tmp = make_catalogue_layer(layer, wcs, img_array[0].shape, cutout_catalog, gaussian=gaussian)
                img_array.append(tmp)

            img_array = np.array(img_array)
            if verbose:
                print(img_array.shape)
            img_array = np.moveaxis(img_array, 0, 2)
            # Include another array giving the bounding box for the source
            bounding_boxes = []
            source_bbox = make_bounding_box(source['ID_ra'], source['ID_dec'], wcs, gaussian=gaussian)
            try:
                assert source_bbox[1] >= 0
                assert source_bbox[0] >= 0
                assert source_bbox[3] < img_array.shape[0]
                assert source_bbox[2] < img_array.shape[1]
            except:
                print("Source not in bounds")
                continue
            source_bounding_box = list(source_bbox)
            bounding_boxes.append(source_bounding_box)
            if verbose:
                plot_three_channel_debug(img_array, bounding_boxes, 1, bounding_boxes[0][5])
            # Now go through and for any other sources in the field of view, add those
            for other_source in other_visible_sources:
                other_bbox = make_bounding_box(other_source['ID_ra'], other_source['ID_dec'],
                                               wcs, class_name="Other Optical Source", gaussian=gaussian)
                if ~np.isclose(other_bbox[0], bounding_boxes[0][0]) and ~np.isclose(other_bbox[1], bounding_boxes[0][
                    1]):  # Make sure not same one
                    if other_bbox[1] >= 0 and other_bbox[0] >= 0 and other_bbox[3] < img_array.shape[0] and other_bbox[2] < img_array.shape[1]:
                        bounding_boxes.append(
                            list(other_bbox))  # Only add the bounding box if it is within the image shape
            # Now save out the combined file

            bounding_boxes = np.array(bounding_boxes)
            if verbose:
                print(bounding_boxes)
            combined_array = [img_array, bounding_boxes, proposal_boxes]
            try:
                np.save(os.path.join(save_cutout_directory, source['Source_Name']), combined_array)
            except Exception as e:
                if verbose:
                    print(f"Failed to save: {e}")
        else:
            print(f"Skipped: {l}")

def create_variable_source_dataset(cutout_directory, pan_wise_location,
                                   value_added_catalog_location, dr_two_location, gaussian=None, all_channels=False, fixed_size=None, filter_lgz=True,
                                   verbose=False, use_multiprocessing=False,
                                   num_threads=os.cpu_count()):
    """
    Create variable sized cutouts (hardcoded to 1.5 times the LGZ_Size) for each of the cutouts

    :param cutout_directory: Directory to store the cutouts
    :param pan_wise_location: The location of the PanSTARRS-ALLWISE catalog
    :param value_added_catalog_location: Location of the LoTSS Value Added Catalog
    :param dr_two_location: The location of the LoTSS DR2 Mosaic Locations
    :param gaussian: Whether to spread out data layers with Gaussian of specified width
    :param use_multiprocessing: Whether to use multiprocessing
    :param num_threads: Number of threads to use, if multiprocessing is true
    :return:
    """

    l_objects = get_lotss_objects(value_added_catalog_location, False)
    if filter_lgz:
        l_objects = l_objects[~np.isnan(l_objects['LGZ_Size'])]
    l_objects = l_objects[~np.isnan(l_objects["ID_ra"])]
    mosaic_names = set(l_objects["Mosaic_ID"])

    # Go through each object, creating the cutout and saving to a directory
    # Create a directory structure identical for detectron2
    all_directory, train_directory, val_directory, test_directory, annotations_directory \
        = create_coco_style_directory_structure(cutout_directory)

    # Now go through each source in l_objects and create a cutout of the fits file
    # Open the Panstarrs and WISE catalogue
    if fixed_size is False:
        fixed_size = None

    if use_multiprocessing:
        pool = multiprocessing.Pool(num_threads)
        pool.starmap(create_cutouts, zip(mosaic_names, repeat(l_objects), repeat(pan_wise_location),
                                         repeat(dr_two_location), repeat(all_directory), repeat(gaussian),
                                         repeat(all_channels), repeat(fixed_size),
                                         repeat(verbose)))
    else:
        pan_wise_catalogue = fits.open(pan_wise_location, memmap=True)
        pan_wise_catalogue = pan_wise_catalogue[1].data
        print("Loaded")
        for mosaic in mosaic_names:
            create_cutouts(mosaic=mosaic, value_added_catalog=l_objects, pan_wise_catalog=pan_wise_catalogue,
                           mosaic_location=dr_two_location,
                           save_cutout_directory=all_directory,
                           gaussian=gaussian,
                           all_channels=all_channels,
                           source_size=fixed_size,
                           verbose=verbose)
