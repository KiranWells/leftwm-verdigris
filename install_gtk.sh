#!/bin/bash

# This script fetches the rose-pine theme from the github repo and installs it

# fetch all the files
mkdir gtk_themes && cd gtk_themes

# fetch the theme
wget https://github.com/rose-pine/gtk/releases/download/v2.1.0/gtk3.tar.gz
wget https://github.com/rose-pine/gtk/releases/download/v2.1.0/gtk4.tar.gz
wget https://github.com/rose-pine/gtk/releases/download/v2.1.0/rose-pine-icons.tar.gz

# extract the theme
tar -xf gtk3.tar.gz
tar -xf gtk4.tar.gz
tar -xf rose-pine-icons.tar.gz

# make the necessary directories
mkdir -p ~/.themes
mkdir -p ~/.icons
mkdir -p ~/.config/gtk-4.0

# move the theme to the correct location
mv gtk3/rose-pine-gtk ~/.themes/
mv gtk4/rose-pine.css ~/.config/gtk-4.0/
mv icons/rose-pine-icons ~/.icons/
