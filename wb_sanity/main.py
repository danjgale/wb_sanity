
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


def make_label_map(region_df, label_numbers, input_img, output_img,
                   fill_value=0):
    
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
    

def make_scalar_map(region_df, value, input_img, output_img, scalar_img,
                    label_numbers=None, fill_value=0):

    output_dir, out_file = os.path.split(output_img)
    fname = out_file.split('.')[0]

    txt_file = pjoin(output_dir, 'tmp_vertices.txt')
    _convert_to_text(input_img, txt_file)
    input_vertices = pd.read_csv(txt_file, header=None)

    if label_numbers is not None:
        region_df.loc[~region_df['Index'].isin(label_numbers), value] = fill_value

    map_dict = dict(zip(region_df['Index'], region_df[value]))
    map_dict[0] = fill_value

    output_vertices = input_vertices[0].map(map_dict)
    output_vertices.to_csv(txt_file, header=False, index=False)

    _to_cifti(txt_file, output_img, scalar_img)
    os.remove(txt_file)


def vol_to_metric(vol_img, surface, output_img, mapping='trilinear'):

    if (not output_img.endswith('.func.gii') or 
        not output_img.endswith('.shape.gii')):
        output_img += '.shape.gii'

    cmd = ['wb_command', '-volume-to-surface-mapping', vol_img, surface, 
          output_img, mapping]
    print(''.join(cmd))
    subprocess.call(cmd)


def vol_to_label(vol_img, surface, label_file, output_img):
    
    output_dir = os.path.dirname(output_img)
    tmp_file = os.path.join(output_dir, 'tmp.shape.gii')

    vol_to_metric(vol_img, surface, tmp_file, mapping='enclosing')

    cmd = ['wb_command', '-metric-label-import', tmp_file, label_file, 
           output_img]
    print(''.join(cmd))
    subprocess.call(cmd)
    
    os.remove(tmp_file)


def threshold_stat_map():
    pass