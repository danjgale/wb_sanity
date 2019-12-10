
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


def _binarize_img(img, label_value=None):
    """Binarize label image to original label value or new label value"""

    img = nib.load(img)
    data = img.get_fdata()

    if label_value is None:
        label = np.max(data)

    res = np.where(data > np.max(data) / 2, label, 0)
    res_img = nib.MGHImage(res, img.affine)
    res_img.to_filename(img)


def _vol2surf_command():
    pass


def _metric_resample_command():
    pass
    

def vol_to_fslr32k(vol_img, output_path, reg_file, mesh_path, 
                   is_label=False, label_value=None, projmeth='frac', 
                   projsum='avg', projarg=[0, 1, .01], smooth_fwhm=False):
    
    os.makedirs(output_path, exist_ok=True)

    fs_home = os.getenv('FREESURFER_HOME')
    if fs_home is None:
        raise RuntimeError('FreeSurfer environment not defined. Define the '
                           'FREESURFER_HOME environment variable.')

    # set up vol2surf call
    vol2surf = ['mri_vol2surf', 
                '--mov', vol_img,
                '--o', output_path]

    if reg_file == 'mni':
        vol2surf.append('--mni152reg')
    else:
        vol2surf.extend(['--reg', reg_file])

    ### --- From pysurfer `project_volume_data` ---
    # Specify the projection
    proj_flag = "--proj" + projmeth
    if projsum != "point":
        proj_flag += "-"
        proj_flag += projsum
    if hasattr(projarg, "__iter__"):
        proj_arg = list(map(str, projarg))
    else:
        proj_arg = [str(projarg)]
    vol2surf.extend([proj_flag] + proj_arg)

    # Set misc args
    if smooth_fwhm:
        vol2surf.extend(["--surf-fwhm", str(smooth_fwhm)])
    ### --- 

    fname = os.path.basename(vol_img).split('.')[0]
    for hemi in ['lh', 'rh']:
        # mgz_img = pjoin(output_path, '{}.{}.mgz'.format(hemi, fname))
        gii_img = pjoin(output_path, '{}.{}.gii'.format(hemi, fname))
        vol2surf_cmd = vol2surf + ['--o', gii_img, '--hemi', hemi, 
                                   '--out_type', 'gii']
        subprocess.call(vol2surf_cmd)

        # if is_label:
        #     _binarize_img(gii_img, label_value)

        # subprocess.call(['mri_convert', mgz_img, gii_img])

        hemi_ = hemi[0].upper()

        current_sphere = pjoin(mesh_path, (f'fsaverage_std_sphere.{hemi_}'
                                           f'.164k_fsavg_{hemi_}.surf.gii'))
        new_sphere = pjoin(mesh_path, (f'fs_LR-deformed_to-fsaverage.{hemi_}'
                                       f'.sphere.32k_fs_LR.surf.gii'))

        metric_out = pjoin(output_path, f'{fname}.{hemi_}.32k_fs_LR.func.gii')

        current_area = pjoin(mesh_path, (f'fsaverage.{hemi_}.midthickness_va_avg.'
                                         f'164k_fsavg_{hemi_}.shape.gii'))

        new_area = pjoin(mesh_path, (f'fs_LR.{hemi_}.midthickness_va_avg.'
                                      '32k_fs_LR.shape.gii'))

        # inputs = [current_sphere, new_sphere, current_area]
        # inputs = [pjoin(mesh_path, x) for x in inputs]

        # check_inputs = [os.path.exists(x) for x in inputs]
        # if not all(check_inputs):
        #     not_found = [x for (x, y) in zip(inputs, check_inputs) if not y]
        #     raise FileNotFoundError(f"The following file(s) not found: {not_found}") 
        
        wb_command = ['wb_command', '-metric-resample', gii_img, 
                      current_sphere, new_sphere, 'ADAP_BARY_AREA',
                      metric_out, '-area-metrics', current_area, 
                      new_area]
        subprocess.call(wb_command)








        # wb_command_cmd = wb_command
        # wb_command_cmd += ['fsaverage_std_sphere.{}'
        #                    '.164k_fsavg_{}.surf.gii'.format(wb_hemi, wb_hemi),
        #                    'fs_LR-deformed_to-fsaverage.?.sphere.???k_fs_LR.surf.gii']
            
        

    # resample to fslr32k






def threshold_stat_map():
    pass