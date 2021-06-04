# change GNOME settings
currentDir=$(dirname $(realpath $0))
os=$(python3 $currentDir/determine_os.py)
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.desktop.privacy remember-recent-files false
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type nothing
gsettings set org.gnome.desktop.interface clock-format 12h
gsettings set org.gtk.Settings.FileChooser clock-format 12h
gsettings set org.gnome.desktop.wm.preferences button-layout appmenu:minimize,maximize,close
gsettings set org.gnome.desktop.interface clock-show-date true
gsettings set org.gnome.desktop.interface show-battery-percentage true
gsettings set org.gnome.shell favorite-apps "['firefox.desktop','org.gnome.Nautilus.desktop','org.gnome.Terminal.desktop']"
gsettings set org.gnome.desktop.input-sources sources "[('xkb', 'us'), ('xkb', 'de'), ('xkb', 'us+rus'), ('xkb', 'hu'), ('xkb', 'il+phonetic'), ('xkb', 'se')]"
gsettings set org.gnome.shell favorite-apps "['firefox.desktop', 'org.gnome.Nautilus.desktop', 'org.gnome.Terminal.desktop', 'gnome-control-center.desktop']"
gsettings set org.gnome.desktop.peripherals.touchpad send-events 'disabled'
gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled true
gsettings set org.gnome.desktop.interface enable-hot-corners false
gsettings set org.gnome.nautilus.preferences executable-text-activation launch
gsettings set org.gnome.nautilus.preferences click-policy single
gsettings set org.gnome.nautilus.preferences default-sort-order type
gsettings set org.gnome.settings-daemon.plugins.color night-light-temperature 5500
if [[ $os =~ 'ubuntu' ]]
then
	gsettings set org.gnome.shell.extensions.dash-to-dock extend-height false
	gsettings set org.gnome.shell.extensions.dash-to-dock dock-position BOTTOM
	gsettings set org.gnome.shell.extensions.dash-to-dock transparency-mode FIXED
	gsettings set org.gnome.shell.extensions.dash-to-dock dash-max-icon-size 50
	gsettings set org.gnome.shell.extensions.dash-to-dock unity-backlit-items true
	gsettings set org.gnome.shell favorite-apps "['firefox.desktop', 'org.gnome.Nautilus.desktop', 'google-chrome.desktop', 'b-browser.desktop', 'thunderbird.desktop', 'libreoffice-writer.desktop', 'libreoffice-impress.desktop', 'libreoffice-calc.desktop', 'libreoffice-draw.desktop', 'texstudio.desktop', 'discord.desktop', 'telegramdesktop.desktop', 'slack.desktop', 'org.gnome.Terminal.desktop', 'gnome-control-center.desktop']"
fi
cd $currentDir/nautilusOpenTerminalHereShortcut
chmod +x Terminal
cp Terminal ~/.local/share/nautilus/scripts/Terminal
nautilus -q
cp scripts-accels ~/.config/nautilus/
cd ~
xdg-mime default okularApplication_pdf.desktop application/pdf
for format in JPG jpg JPEG jpeg png PNG 
do
	xdg-mime default org.kde.gwenview.desktop application/$format
done
