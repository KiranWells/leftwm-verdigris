<pre style="width:100%;text-align:center">
║ ║╔═╝╔═║╔═ ╝╔═╝╔═║╝╔═╝
║ ║╔═╝╔╔╝║ ║║║ ║╔╔╝║══║
 ╝ ══╝╝ ╝══ ╝══╝╝ ╝╝══╝

Author: @KiranWells
</pre>

A [Rosè Pine](https://rosepinetheme.com/)-based theme for [Leftwm](https://github.com/leftwm/leftwm). Optimized for 1440p.

## Prerequisites

### Required:
- leftwm
- eww

### Required for boot config:
- plymouth
- grub
- install_boot.sh has been run as root to install themes

### Required for full functionality:
- rofi - app lancher
- gdbus - locker
- feh - wallpaper setter
- python - for eww scripts
- bluetoothctl
- nmcli - NetworkManager
- awk
- xdotool - changing desktops
- amixer - for sound management
- xbacklight - for brightness widget
- i3lock - lock screen
- jq - used in the weather script

### Configured if present:
- picom (will also start compton, but will not configure it)
- setxkbmap - enable compose key
- kitty
- firefox (requires Cascade theme, see below)
- dunst
- stalonetray

### Keybinds

The following lines need to be added to `leftwm/config.ron`:

```ron
    // Theme specific keybinds
    (command: Execute, value: "rofi -no-lazy-grab -show drun -theme ~/.config/leftwm/themes/current/rofi/launcher.rasi", modifier: ["modkey"], key: "space"),
    (command: Execute, value: "eww -c ~/.config/leftwm/themes/current/eww open-many background-overlay quit", modifier: ["modkey", "Shift"], key: "q"),
```

### Firefox Theme

This theme includes colors for the Cascade Firefox theme. 
It requires adding the following into the userChrome.css 
file, and removing the default colors.

```css
@import url("colors.css");
```

Cascade Repository:
  - Mouse edition: https://github.com/andreasgrafen/cascade
  - Original:      https://github.com/crambaud/cascade

### Weather API

For weather information to be fetched, an [openweathermap.org](https://openweathermap.org) API key needs to be put in `$HOME/.openapi_weather_key`. In addition, the following line needs to be added to your users crontab (adjust times if desired):

```crontab
*/5    *    *    *   *  ~/.config/leftwm/themes/current/eww/scripts/weather_info --getdata
```

## Configuration

Configurations for kitty, firefox, picom, dunst, and stalonetray are backed up and replaced if they exist. This can be disabled by commenting out the corresponding lines in the `up` script.

## Credits

See [credits](CREDITS).
