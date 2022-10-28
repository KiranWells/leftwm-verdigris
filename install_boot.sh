#!/bin/bash

# check to see if we are root
# otherwise, quit
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# install the plymouth theme
mkdir -p /usr/share/plymouth/themes/tail
cp -r ./plymouth/* /usr/share/plymouth/themes/tail

echo << EOF
# /etc/plymouth/plymouthd.conf
[Daemon]
Theme=tail
ShowDelay=0
EOF > /etc/plymouth/plymouthd.conf

# rebuild the initramfs
plymouth-set-default-theme -R tail

# install the grub theme
mkdir -p /boot/grub/themes/bubbles
cp -r ./grub/* /boot/grub/themes/bubbles

echo << EOF
# grub theme set by install.sh
GRUB_THEME="/boot/grub/themes/bubbles/theme.txt"
EOF >> /etc/default/grub

# update grub
echo "Make sure to update grub after checking the /etc/default/grub file"
