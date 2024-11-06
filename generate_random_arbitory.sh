#!/bin/sh

python random_samples.py --input_name 0035-sample.png \
                         --mode random_samples_arbitrary_sizes \
                         --gen_start_scale 0 \
                         --nc_z 4 \
                         --nc_im 4 \
                         --gpu_id 0 \
                         --input_dir /home/aless/singan-seg/Input/Images \
                         --scale_h 1.039 \
                         --scale_v 1.039 \
                         --scale_factor 0.75 \
                         --alpha 10 \
                         --num_samples 1000 
