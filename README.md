Build a Yadoms SD card image for RaspberryPi
===============

This page explains how to build a Yadoms SD card image for the RaspberryPi micro-computer.

All these scripts are linux compatible, tested under Ubuntu 17.04.

> Image will be created with user `yadoms` (password `yadoms2017`)
> Root password is `yadoms2017`

# Dependancies

You first need to install these packages :

````
sudo apt-get install build-essential wget git lzop u-boot-tools binfmt-support qemu qemu-user-static multistrap parted dosfstools
````

# Create the image

Use the create-yadoms-pi-image script to build a Raspberry PI image containing a Yadoms version. You just have to specify Yadoms version, it will be downloaded from Github :

````
sudo ./create-yadoms-pi-image 2.0.0-rc.5
````

Two outputs are expected (in the repository root) :
* `Yadoms-{YadomsVersion}-RaspberryPI.img` : The generated image
* `Yadoms-{YadomsVersion}-RaspberryPI.img.zip` : The generated image zipped


# Check image content

You can mount the generated image to show its content :

````
cd yadomsScripts
./mountPiImage {generatedImage}.img
````

# Credits
Thanks for [TheSin-](https://github.com/TheSin-) for the powerful tool [rpi-img-builder](https://github.com/TheSin-/rpi-img-builder)

