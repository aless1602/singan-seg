# singan-seg
This is the development repository of SinGAN-Seg

# Setup required packages

- Install requirements.txt using the following command
````python
pip install -r requirements.txt
````
- Install pytorch (tested with 1.12.1) as described in https://pytorch.org/

- Run the following commands to train or generate samples from pre-trained models



## To train

```
bash train.sh
```
or

````python
python random_samples.py --input_name 0035-sample.png --mode random_samples --gen_start_scale 0 --nc_z 4 --nc_im 4 --gpu_id 0 --num_samples 10
````

## Personal training
````python
python main_train.py --input_name 0035-sample.png  --nc_z 4 --nc_im 4 --gpu_id 0 --scale_factor 0.85
````
## To generate samples from pre-trained models
```
bash generate_random.sh

```
or

```python
python random_samples.py --input_name polyp_4_channel_test_1.png --mode random_samples --gen_start_scale 0 --nc_z 4 --nc_im 4
```

### To go back to official repository: [singan-seg-polyp](https://github.com/vlbthambawita/singan-seg-polyp)

## To applicate style transfer

```python
python style_transfer.py --cimg_path /home/aless/singan-seg/Output/RandomSamples_ArbitrerySizes/0035-sample/scale_v=1.050000_scale_h=1.050000/0_img.png --simg_path /home/aless/singan-seg/Input/Images/0035-sample.png  --num_epochs 1000 --cw 1 --sw 1000 --device_id 0 --vgg "vgg16"
```
## Or Style Transfert on directory
```python

python style_transfer.py   --cimg_path /home/aless/singan-seg/Output/RandomSamples_ArbitrerySizes/0035-sample/scale_v=1.040000_scale_h=1.040000   --simg_path /home/aless/singan-seg/Input/Images/0035-sample.png   --output_dir /home/aless/singan-seg/Output/Styled_Images   --num_epochs 1000   --cw 1   --sw 1000   --device_id 0   --vgg "vgg16"

```
