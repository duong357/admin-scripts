# TODO: convert to Python 3 script
cd ~/Downloads/archives
ln -s $(find / -wholename '*Passport1*iso' -type d 2> /dev/null | head -1)
cd ~
# vboxmanage is the chief command; for help, run `vboxmanage | less`
# To list OS types, use vboxmanage list ostypes

# List VMs
# vboxmanage list (-l) vms

# create VM
# vboxmanage createvm --name $NAME --ostype $OS_TYPE --register
# The --register parameter is important as it puts the VM into VirtualBox

# TO list a VM's properties, use
# vboxmanage showVMinfo $VM

# To modify VM properties, use
# vboxmanage modifyvm $VM --option $PARAM --memory 2048 (in MB) --vram $VRAM (presumably in MB, between 0 and 256) --cpus $NUMBER_OF_CPUS

# To create a virtual hard disk, you need three steps
# vboxmanage createhd --filename /path/to/hard_drive_image/$DISK_NAME.vdi --size $SIZE (in MB) --variant (Standard (dynamically allocated)|Fixed)
# vboxmanage storagectl $VM --name "SATA Controller" --add sata --bootable on
# When choosing Serial ATA (SATA) as the controller type, make sure that your guest OS has device support for Advanced Host Controller Interface (AHCI), which is the standard interface for SATA controllers. Be warned that older operating systems, such as Windows XP, do not support AHCI. In that case, you should rely on an Integrated Drive Electronics (IDE) controller.

# vboxmanage storageattach $VM --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium /path/to/hard_drive_image/$DISK_NAME
# vboxmanage storagectl $VM --name "IDE Controller" --add ide 
# vboxmanage storageattach $VM --storagectl "IDE Controller" --port 0  --device 0 --type dvddrive --medium $PATH_TO_ISO

declare -A weirdNames=(['bubuntu']='ubuntu-budgie' ['mubuntu']='ubuntu-mate' ['stubuntu']='ubuntustudio')
for OS_NAME in devuan alpine android guix kubuntu mint bubuntu xubuntu trisquel mubuntu peppermint lubuntu pop elementary pup neon stubuntu zorin tails solus mx parrot pureos kali antix gnewsense debian centos-{6..8} centos-stream fedora leap tumbleweed tails slackware solus dragora dynebolic manjaro parabola archlinux ${!weirdNames[@]}
do
	#echo "-----------------------------------------\n$OS_NAME\n-----------------------------------------"
	OS_PATH=~"/VirtualBox VMs/${OS_NAME}.vdi"
	vboxmanage unregistervm $OS_NAME --delete
	vboxmanage createvm --name $OS_NAME --ostype Linux_64 --register
	vboxmanage modifyvm $OS_NAME --memory 1024 --vram 256
	vboxmanage createhd --filename "$OS_PATH" --size 12000 --variant Standard
	vboxmanage storagectl $OS_NAME --name "SATA Controller" --add sata --bootable on
	vboxmanage storageattach $OS_NAME --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "$OS_PATH"
	vboxmanage storagectl $OS_NAME --name "IDE Controller" --add ide
	if [[ ! -z ${weirdNames["$OS_NAME"]} ]]
	then
		vboxmanage storageattach $OS_NAME --storagectl "IDE Controller" --port 0  --device 0 --type dvddrive --medium $(realpath $(find ~/Downloads/archives/iso/ -iname "*${weirdNames[$OS_NAME]}*iso" -type f | head -1))
	else
		vboxmanage storageattach $OS_NAME --storagectl "IDE Controller" --port 0  --device 0 --type dvddrive --medium $(realpath $(find ~/Downloads/archives/iso/ -iname "*$OS_NAME*iso" -type f | head -1))
	fi
done