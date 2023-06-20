#!/bin/bash

set -ex

# check to see if we are root
# otherwise, quit
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# install the plymouth theme
rm -rf /usr/share/plymouth/themes/tail
mkdir -p /usr/share/plymouth/themes/tail
cp -r ./plymouth/* /usr/share/plymouth/themes/tail

cat << EOF > /etc/plymouth/plymouthd.conf
# /etc/plymouth/plymouthd.conf
[Daemon]
Theme=tail
ShowDelay=0
DeviceTimeout=8
EOF

# rebuild the initramfs
# mkinitcpio -P

# install the grub theme
rm -rf /boot/grub/themes/bubbles
mkdir -p /boot/grub/themes/bubbles
cp -r ./grub/* /boot/grub/themes/bubbles

# cat << EOF >> /etc/default/grub
# # grub theme set by install.sh
# GRUB_THEME="/boot/grub/themes/bubbles/theme.txt"
# EOF
echo "Make sure the following line is in /etc/default/grub:"
echo "GRUB_THEME=\"/boot/grub/themes/bubbles/theme.txt\""

# update grub
# grub-mkconfig -o /boot/grub/grub.cfg

echo "Run the following commands to update grub and initramfs:"
cat << EOF
grub-mkconfig -o /boot/grub/grub.cfg
mkinitcpio -P
EOF

