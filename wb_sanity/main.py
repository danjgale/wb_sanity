
import os
import subprocess
import numpy as np
import pandas as pd
import nibabel as nib

pjoin = os.path.join

def _convert_to_text(label_img, vertex_file):
    """Generate vertex file from a cifti image"""
    
    cmd = 'wb_command -cifti-convert -to-text {} {}'.format(label_img,
                                                            vertex_file)
    print(cmd)
    subprocess.call(cmd.split())


def _to_cifti(vertex_file, output_img, template):
    """Convert vertex text file to cifti image"""

    cmd = 'wb_command -cifti-convert -from-text {} {} {}'.format(vertex_file,
                                                                 template, 
                                                                 output_img)
    print(cmd)
    subprocess.call(cmd.split())


def make_label_map(input_img, label_numbers, output_img, fill_value=0):
    """Create a label file that shows only certain regions of interest from an
    existing atlas in CIfTI format.

    Parameters
    ----------
    input_img : str
        File path of existing CIfTI label file (.dlabel.nii)
    label_numbers : list of int
        Selected integer labels in `input_img` that you retain.
    output_img : str
        File path of CIfTI label file (.dlabel.nii) that contains only 
        specified regions from `label_numbers`.  
    fill_value : int, optional
        Value to fill vertices are not specified by label_numbers. Default is 
        0, which will be transparent in Connectome Workbench.
    """
    
    output_dir, out_file = os.path.split(output_img)
    fname = out_file.split('.')[0]

    txt_file = pjoin(output_dir, 'tmp_vertices.txt')
    _convert_to_text(input_img, txt_file)
    
    # select labels
    vertices = pd.read_csv(txt_file, header=None)
    vertices[~vertices[0].isin(label_numbers)] = fill_value
    vertices.to_csv(txt_file, header=False, index=False)

    _to_cifti(txt_file, output_img, input_img)
    os.remove(txt_file)
    

def make_scalar_map(input_img, region_spec, value_name, output_img, scalar_img,
                    label_numbers=None, fill_value=0):
    """Assign arbitrary values/weightings to regions in an atlas in CIfTI 
    format

    The atlas regions can be restricted using `label_numbers`.
    
    Parameters
    ----------
    input_img : str
        File path of existing CIfTI label file (.dlabel.nii)
    region_spec : str
        File path of a comma-separated region specification file (.csv). The
        first row must be column names, and MUST include `Index`. 
    value_name : str
        Column name in `region_spec` to set the value to assign each region.
    output_img : str
        File path of output CIfTI file (.dscalar.nii).
    scalar_img : str
        Reference scalar image to map a the .dlabel.nii file to .dscalar.nii.
    label_numbers : list of int, optional
        Selected integer labels in `input_img` that you retain. By default 
        None, which will retain all regions from `input_img`. 
    fill_value : int, optional
        Value to fill vertices are not specified by `label_numbers` or are not
        in `region_spec`. Default is 0, which will be transparent in Connectome 
        Workbench.

    Notes
    -----
    `region_spec` is a .csv file that includes the data you wish to map to 
    regions. The first row must be column headers. One of these columns MUST
    be named `Index`, and include the integer labels found in `input_img`. The
    remaining columns can be named anything. `value_name` the specifies which
    of these remaining columns to use as fill values for the regions (e.g., r
    values, loading, etc).

    `scalar_img` is used as a reference for mapping the `.dlabel.nii` to 
    `.dscalar.nii`. Typically atlases provide both file types, so it is 
    recommended to use the one associated with the input `.dlabel.nii` file.
    """
    output_dir, out_file = os.path.split(output_img)
    fname = out_file.split('.')[0]

    txt_file = pjoin(output_dir, 'tmp_vertices.txt')
    _convert_to_text(input_img, txt_file)
    input_vertices = pd.read_csv(txt_file, header=None)

    if label_numbers is not None:
        mask = ~region_spec['Index'].isin(label_numbers)
        region_df.loc[mask, value_name] = fill_value

    map_dict = dict(zip(region_spec['Index'], region_spec[value_name]))
    map_dict[0] = fill_value

    output_vertices = input_vertices[0].map(map_dict)
    output_vertices.to_csv(txt_file, header=False, index=False)

    _to_cifti(txt_file, output_img, scalar_img)
    os.remove(txt_file)


def vol_to_metric(vol_img, surface, output_img, mapping='trilinear'):
    """Project volume data to a metric file for displaying stat maps.

    Converts a NIfTI volume (.nii/.nii.gz) to a GIfTI surface (.shape.gii or
    .func.gii).

    Parameters
    ----------
    vol_img : str
        File path of 3D volumetric data. Must be a NIfTI file and cannot be 4D
        (timeseries). 
    surface : str
        File path of GIfTI surface file (.surf.gii). 
    output_img : str
        File path of the output surface. If `.shape.gii` or `.func.gii` is not
        provided, then `.shape.gii` will automatically be appended to the file
        name.
    mapping : {'trilinear', 'enclosing', 'cubic'}, optional
        Mapping method. `trilinear` performs 3D linear interpolation, 
        `enclosing` uses the value from the voxel the vertex lies inside, and
        `cubic` uses cubic splines. Currently these are the only supported
        mapping methods, with `trilinear` as default.

    Notes
    -----
    Metric file are used to show statistical results. The original volumetric
    image should contain continuous values (e.g., t-scores, z-scores). If
    thresholding is desired, it must be done on the volume prior to projection. 
    
    The surface:
    I've found best results when projecting to a "very inflated" surface, so
    this is recommended. Otherwise, you may find best results when projecting
    the data to the surface that you are ultimately hoping to use to visualize
    your data. Best to test out a few and compare.
    """
    output_dir = os.path.dirname(output_img)
    os.makedirs(output_dir, exist_ok=True)

    if ((not output_img.endswith('.func.gii')) and 
        (not output_img.endswith('.shape.gii'))):
        output_img += '.shape.gii'

    cmd = ['wb_command', '-volume-to-surface-mapping', vol_img, surface, 
          output_img, f'-{mapping}']
    print(''.join(cmd))
    subprocess.call(cmd)


def vol_to_label(vol_img, surface, label_file, output_img):
    """Project volume data to a label file for displaying regions of interest.

    Converts a NIfTI volume (.nii/.nii.gz) to a GIfTI surface (.label.gii)

    Parameters
    ----------
    vol_img : str
        File path of 3D volumetric data. Must be a NIfTI file and cannot be 4D
        (timeseries). 
    surface : str
        File path of GIfTI surface file (.surf.gii). 
    label_file : str
        File path of a label file (.txt). See notes for formatting. 
    output_img : str
        File path of the output surface. If `.label.gii` is not provided, then
        it will automatically be appended to the file name.

    Notes
    -----
    Label file are used to show regions of interests. The original volumetric
    image should have a single integer label/value for each ROI, which will be 
    retained on the surface projection. 
    
    The label file:
    Each region is assigned a color using the label file, which contains the 
    following format:

    <region name>
    <integer label> <red> <green> <blue> <alpha>

    Each region therefore occupies two lines in a text file: the name, and the
    specifications. Red, green, and blue are values from 0 to 255. Alpha is a
    value from 0 to 1.

    The surface:
    I've found best results when projecting to a "very inflated" surface, so
    this is recommended. Otherwise, you may find best results when projecting
    the data to the surface that you are ultimately hoping to use to visualize
    your data. Best to test out a few and compare.
    """
    if not output_img.endswith('.label.gii'):
        output_img += '.label.gii'

    output_dir = os.path.dirname(output_img)
    tmp_file = pjoin(output_dir, 'tmp.shape.gii')

    vol_to_metric(vol_img, surface, tmp_file, mapping='enclosing')

    cmd = ['wb_command', '-metric-label-import', tmp_file, label_file, 
           output_img]
    print(''.join(cmd))
    subprocess.call(cmd)
    
    os.remove(tmp_file)
