from PIL import Image
import os

def upscale_images(input_dir, output_dir, scale_factor):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(input_dir, filename)
            img = Image.open(img_path)
            
            # Calculer la nouvelle taille
            new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
            
            # Agrandir l'image
            upscaled_img = img.resize(new_size, Image.BICUBIC)
            
            # Enregistrer l'image agrandie
            upscaled_img.save(os.path.join(output_dir, filename))
            print(f"Image {filename} agrandie et sauvegardée.")
            
# Exemple d'utilisation
input_directory = "/home/aless/singan-seg/Output/RandomSamples/0035-sample/gen_start_scale=0 old"
output_directory = "/home/aless/singan-seg/Output/original_size_Sample"
scale_factor = 1.75  # Par exemple, pour doubler la taille

upscale_images(input_directory, output_directory, scale_factor)
