Build a Yadoms SD card image for RaspberryPi
===============

This page explains how to build a Yadoms SD card image for the RaspberryPi micro-computer.

All these scripts are linux compatible, tested under Ubuntu 17.04.

# Dependancies

You first need to install these packages :

````
sudo apt-get install build-essential wget git lzop u-boot-tools binfmt-support qemu qemu-user-static multistrap parted dosfstools
````

# Create the image

## Easy method

Use the create-yadoms-pi-image script to build a Raspberry PI image containing a Yadoms version. You just have to specify Yadoms version, it will be downloaded from Github :

````
sudo create-yadoms-pi-image 2.0.0-rc.2
````

Result (image file) will be in the repository root.


## Step-by-step method

### Add Yadoms package

Download the Yadoms RaspberryPi package you want to put in the image :

````
wget https://github.com/Yadoms/yadoms/releases/download/2.0.0-rc.2/Yadoms-2.0.0-rc.2-RaspberryPI.tar.bz2
````

Copy the Yadoms RaspberryPi package content to image builder sources

````
mkdir -p plugins/yadoms/files/opt/yadoms
tar xjf Yadoms-2.0.0-rc.2-RaspberryPI.tar.bz2 -C plugins/yadoms/files/opt/yadoms --strip 1
````

### Build image

Root access is needed

````
sudo make
````

Result (image file) will be in the repository root.

## Check image content

You can mount the generated image to show its content :

````
cd yadomsScripts
./mountPiImage {generatedImage}.img
````

# Credits
Thanks for TheSin- for the powerful tool [rpi-img-builder](https://github.com/TheSin-/rpi-img-builder)

