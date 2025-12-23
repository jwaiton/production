===================
tag               :  test_1525
verbose           :  1
processing_style  :  LDC
LDCs              :  7
RUNS              :  ['00000', '00001']
flow_priority     :  JOB
global_path       :  /home/e78368jw/Documents/NEXT_CODE/production/test_data/example_data/
max_num_jobs      :  7
env_script        :  home/e78368jw/Documents/NEXT_CODE/production/templates/env_templates/dipc_helena.sh
timestamp         :  251223_1512
config_path       :  /home/e78368jw/Documents/NEXT_CODE/production/test_data/example_data/test_1525/configs
data_path         :  /home/e78368jw/Documents/NEXT_CODE/production/test_data/example_data/test_1525/data
job_path          :  /home/e78368jw/Documents/NEXT_CODE/production/test_data/example_data/test_1525/jobs
===================
    ===================
    IC-beersheba  :
        ===================
        city       :  beersheba
        pre_path   :  /home/e78368jw/Documents/NEXT_CODE/production/test_data/example_data/
        post_path  :  sophronia/
        fixed      :
            ===================
            compression  :  'ZLIB4'
            e_cut        :  0.1
            n_iter       :  10
            threshold    :  2 * pes
            same_peak    :  True
            q_cut        :  50
            ===================
        ===================


    move_files    :
        ===================
        IC      :  True
        input   :  beersheba
        output  :  isaura
        ===================


    IC-isaura     :
        ===================
        city     :  isaura
        in_path  :  beersheba.h5
        fixed    :
            ===================
            voxel_size  :  [15, 15, 15]
            ===================
        ===================


    ===================
