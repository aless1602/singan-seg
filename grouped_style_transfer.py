def transfer_style_to_folder_single_style(content_img_dir, style_img_path, output_dir, num_epochs, content_weight, style_weight, device, vgg_model, verbose=False):
    content_images = [f for f in os.listdir(content_img_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    os.makedirs(output_dir, exist_ok=True)

    pbar = tqdm(content_images, position=0, leave=True)
    for cimg in pbar:
        cimg_path = os.path.join(content_img_dir, cimg)
        pbar.set_description(f"Processing {cimg}")
        out_img = transfer_style(cimg_path, style_img_path, num_epochs, content_weight, style_weight, device, vgg_model, verbose, tqdm_position=0, tqdm_leave=False)
        out_img.save(os.path.join(output_dir, cimg.split('.')[0] + '_ST.png'))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--cimg_path", help="Content image path")
    parser.add_argument("--simg_path", help="Style image path")
    parser.add_argument("--cimg_dir", help="Content images directory")
    parser.add_argument("--output_dir", help="Output directory", default="./style_transferred")
    parser.add_argument("--num_epochs", help="Number of epochs", default=1000)
    parser.add_argument("--cw", help="Content weight", default=1)
    parser.add_argument("--sw", help="Style weight", default=1000)
    parser.add_argument("--device_id", help="Device ID", default=0)
    parser.add_argument("--vgg", help="VGG model", default="vgg16")

    opt = parser.parse_args()

    run_device = torch.device("cuda:{}".format(opt.device_id) if torch.cuda.is_available() else "cpu")

    if opt.cimg_dir and opt.simg_path:
        # Process multiple content images with a single style image
        transfer_style_to_folder_single_style(opt.cimg_dir, opt.simg_path, opt.output_dir,
                                              int(opt.num_epochs), int(opt.cw), int(opt.sw),
                                              run_device, opt.vgg, verbose=False)
    elif opt.cimg_path and opt.simg_path:
        # Process a single image
        pil_img = transfer_style(opt.cimg_path, opt.simg_path, int(opt.num_epochs), int(opt.cw), int(opt.sw),
                                 run_device, opt.vgg, verbose=False, tqdm_position=0, tqdm_leave=True)

        save_path = opt.cimg_path.split(".")[0] + "_ST" + ".png"
        print(save_path)
        pil_img.save(save_path)
    else:
        print("Please provide either --cimg_path and --simg_path for single image processing, or --cimg_dir and --simg_path for batch processing.")