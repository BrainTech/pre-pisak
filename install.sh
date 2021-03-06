#! /bin/bash

#    This file is part of AT-Platform.
#
#    AT-Platform is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    AT-Platform is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with AT-Platform.  If not, see <http://www.gnu.org/licenses/>.

echo -e "\nThe Milena PPA repository will be add to your system and the following packages will be installed:\npython2.7 python-wxgtk2.8 python-alsaaudio python-pygame python-xlib python-pip pyuserinput calibre smplayer milena xdotool wmctrl\n"

read -p "Do you want to continue? [Y/n]"

if [ "$REPLY" == Y ] || [ "$REPLY" == y ]; then

   sudo add-apt-repository ppa:ethanak/milena
   sudo apt-get update

   sudo apt-get install python2.7 python-wxgtk2.8 python-alsaaudio python-pygame python-xlib python-pip calibre smplayer milena xdotool wmctrl

   sudo pip install pyuserinput

    echo "Done."

    else

    echo -e "Abort on request."
fi