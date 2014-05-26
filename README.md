![alt text](/icons/gpl.png)

	PrePisak is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	PrePisak is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with PrePisak.  If not, see <http://www.gnu.org/licenses/>.

#PrePisak

We have build an interactive platform for people with severe expressive,
communication disorders (i.e. with severe impairements in speech, language
and writing).

We are working on Ubuntu 12.04 using Python2.7.

<h4>Contributors (in alphabetic order):</h4>
Jerzy Grynczewski, Andrzej Jeziorski, Bartosz Jura, Sasza Kijek, Tomasz Spustek

<h4>Dependencies:</h4>

* python2.7 and libaries: python-wxgtk2.8, python-pygame, python-alsaaudio, python-xlib, python-pip
* pyUserInput ( installed through pip )
* Calibre
* Smplayer
* Milena ( polish speech synthesizer for linux )
* xdotool
* wmctrl

<h4>Installation</h4>

Enter the following commands at the command line of a terminal window:

* Install git: `sudo apt-get install git`
* Clone the repo: `git clone git://github.com/jgrynczewski/AT-Platform.git`
* Enter the AT-Platform directory and install all dependencies: `cd pre-pisak && bash install.sh`

The installation process is now completed. To run AT-Platform, type the following in the AT-Platform directory:

`./PrePisak.py`

Click the left mouse button to navigate.
Calibre and Smplayer should have been configurated before running AT-Platform. Proposed configuration can be found in the *Configuration.pdf*.
