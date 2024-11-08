
import torch
import os
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import PIL
from torch import optim
from torch._C import device
from tqdm import tqdm, trange
import torchvision
import torchvision.transforms as transforms
from torchvision.transforms.functional import to_pil_image
import torch.nn.functional as F

import torchvision.models as models
import argparse


def imgtensor2pil(img_tensor, mean_rgb, std_rgb):
    img_tensor_c = img_tensor.clone().detach()
    img_tensor_c*=torch.tensor(std_rgb).view(3,1,1)
    img_tensor_c+=torch.tensor(mean_rgb).view(3,1,1)
    img_tensor_c = img_tensor_c.clamp(0,1)
    img_pil = to_pil_image(img_tensor_c)
    return img_pil


def get_features(x, model, layers):
    features = {}
    for name, layer in enumerate(model.children()):
        x = layer(x)
        if str(name) in layers:
            features[layers[str(name)]] = x
    return features



def gram_matrix(x):
    n, c, h, w = x.size()
    x = x.view(n*c, h * w)
    gram = torch.mm(x, x.t())
    return gram


def get_content_loss(pred_features, target_features, layer):
    target = target_features[layer]
    pred = pred_features[layer]
    loss = F.mse_loss(pred, target)
    return loss


def get_style_loss(pred_features, target_features, style_layers_dict):
    loss = 0
    for layer in style_layers_dict:
        pred_fea = pred_features[layer]
        pred_gram = gram_matrix(pred_fea)
        n, c, h, w = pred_fea.shape
        target_gram = gram_matrix(target_features[layer])
        layer_loss = style_layers_dict[layer] * F.mse_loss(pred_gram, target_gram)
        loss += layer_loss/ (n* c * h * w)
    return loss


def transfer_style(content_img_path: str, style_img_path: str, num_epochs: int, content_weight: int, style_weight: int, 
                   device: torch.device, vgg_model:str, verbose=False, tqdm_position = 0, tqdm_leave = True ,*args, **kwargs) -> PIL.Image:
    ''' Trnsfering style from a source image to a target image.
    
    Parameters
    ==========

    content_img_path: str
        A path to an image to which the style is going to be transfered.
    style_img: str
        A path to an image which has the required style to be transferred.
    num_epochs: int
        Number of epoch to iterate for transfering style to content image.
    content_weight: int
        Weight to keep the content of the destination image.
    style_weight: int
        Weight to transfer style from the source image.
    device: torch.device
        Torch device object, either "CPU" or "CUDA". Refer Pytoch documentation for more detials.
    vgg_model: str
        A model to extract features.
    verbose: bool
        If true, loss values will be printed to stdout.
    


    Return
    =======
    PIL.Image
        Style transferred image.
    
    '''
    
    # These values are from VGG implementations
    mean_rgb = (0.485, 0.456, 0.406)
    std_rgb = (0.229, 0.224, 0.225)


    content_img = Image.open(content_img_path).convert("RGB")
    style_img = Image.open(style_img_path).convert("RGB") 
    
    # pre-defined values
    feature_layers = {'0': 'conv1_1',
                   '5': 'conv2_1',
                   '10': 'conv3_1',
                   '19': 'conv4_1',
                   '21': 'conv4_2',
                   '28': 'conv5_1'
                  }
    
    content_layer = "conv5_1"
    
    style_layers_dict = {'conv1_1': 0.75,
                         'conv2_1': 0.5,
                         'conv3_1': 0.25,
                         'conv4_1': 0.25,
                         'conv5_1': 0.25
                      }

    
    
    loader = transforms.Compose([
        transforms.Resize((content_img.height,content_img.width)),
        transforms.ToTensor(),
        transforms.Normalize(mean_rgb, std_rgb)
    ])
    
    content_tensor = loader(content_img)
    style_tensor = loader(style_img)
    
    con_tensor = content_tensor.unsqueeze(0).to(device)
    sty_tensor = style_tensor.unsqueeze(0).to(device)
    
    # Model preparation
    model_vgg = getattr(models, vgg_model)(pretrained=True).features.to(device).eval()
    
    for param in model_vgg.parameters():
        param.requires_grad_(False)
        
    input_tensor = con_tensor.clone().requires_grad_(True)
    content_features = get_features(con_tensor, model_vgg, feature_layers)
    style_features = get_features(sty_tensor, model_vgg, feature_layers)
    
    optimizer = optim.Adam([input_tensor], lr=0.01)
    
    t = trange(num_epochs, desc="Progress", position=tqdm_position, leave=tqdm_leave)

    for epoch in t:
        optimizer.zero_grad()
        input_features = get_features(input_tensor, model_vgg, feature_layers)
        content_loss = get_content_loss(input_features, content_features, content_layer)
        style_loss = get_style_loss(input_features, style_features, style_layers_dict)
        neural_loss = content_weight * content_loss + style_weight * style_loss
        neural_loss.backward(retain_graph=True)
        optimizer.step()

        t.set_description('Progress: epoch {}, content loss: {:.2}, style loss {:.2}'.format(epoch,content_loss,style_loss))
        if verbose:
            if epoch % 100 == 0:
                print('epoch {}, content loss: {:.2}, style loss {:.2}'.format(epoch,content_loss,style_loss))

    return imgtensor2pil(input_tensor[0].detach().cpu(), mean_rgb, std_rgb)





def transfer_style_to_folder(generated_img_dir_path, style_img_path, output_dir, num_epochs: int, content_weight: int, style_weight: int, 
                             device: torch.device, vgg_model:str, verbose=False, *args, **kwargs):
    '''
    Apply style transfer to each image in a directory with a single style image.
    Parameters
    ==========
    generated_img_dir_path: str
        Path to the folder containing images to apply style transfer to.
    style_img_path: str
        Path to a single style image.
    output_dir: str
        Path to save style transferred images.
    num_epochs: int
        Number of epochs for style transfer.
    content_weight: int
        Content weight.
    style_weight: int
        Style weight.
    device: torch.device
        CUDA or CPU device.
    vgg_model: str
        Model name for VGG.
    verbose: bool
        Print details if True.
    '''
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter out mask images and only keep the content images
    generated_images_filtered = [img for img in os.listdir(generated_img_dir_path) if "mask" not in img]
    
    pbar = tqdm(generated_images_filtered, position=0, leave=False)
    for gen_img in pbar:
        gen_img_path = os.path.join(generated_img_dir_path, gen_img)
        
        pbar.set_description(f"Processing {gen_img}")
        
        # Apply style transfer
        out_img = transfer_style(
            content_img_path=gen_img_path,
            style_img_path=style_img_path,
            num_epochs=num_epochs,
            content_weight=content_weight,
            style_weight=style_weight,
            device=device,
            vgg_model=vgg_model,
            verbose=verbose,
            *args, **kwargs
        )
        
        # Save the output image
        out_img.save(os.path.join(output_dir, gen_img.split(".")[0] + "_ST.png"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cimg_path", help="Content img path")
    parser.add_argument("--simg_path", help="Style image path")
    parser.add_argument("--output_dir", help="Output directory", default="/work/vajira/DATA/michael_data/style_transferred")
    parser.add_argument("--num_epochs", help="Number of epochs", type=int, default=1000)
    parser.add_argument("--cw", help="Content weight", type=int, default=1)
    parser.add_argument("--sw", help="Style weight", type=int, default=1000)
    parser.add_argument("--device_id", help="Device ID", type=int, default=0)
    parser.add_argument("--vgg", help="VGG model", default="vgg16")

    opt = parser.parse_args()

    run_device = torch.device(f"cuda:{opt.device_id}" if torch.cuda.is_available() else "cpu")

    transfer_style_to_folder(
        generated_img_dir_path=opt.cimg_path,
        style_img_path=opt.simg_path,
        output_dir=opt.output_dir,
        num_epochs=opt.num_epochs,
        content_weight=opt.cw,
        style_weight=opt.sw,
        device=run_device,
        vgg_model=opt.vgg,
        verbose=False
    )


    