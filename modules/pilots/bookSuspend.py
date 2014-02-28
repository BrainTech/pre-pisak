#!/bin/env python2.7
# -*- coding: utf-8 -*-

# This file is part of AT-Platform.
#
# AT-Platform is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AT-Platform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AT-Platform. If not, see <http://www.gnu.org/licenses/>.

import wxversion
wxversion.select( '2.8' )

import wx, os, time
import wx.lib.buttons as bt

from pymouse import PyMouse

import bookPilot


#=============================================================================
class suspend( wx.Frame ):
	def __init__(self, parent, id):

	    self.winWidth, self.winHeight = wx.DisplaySize( )

            wx.Frame.__init__( self , parent , id, 'bookSuspend', size = ( 210, 280 ), pos = ( self.winWidth - 215, self.winHeight - 312 ) )

            style = self.GetWindowStyle( )
            self.SetWindowStyle( style | wx.STAY_ON_TOP )
            self.parent = parent

            self.MakeModal( True )
            
            self.initializeParameters( )            
            self.createGui( )
            self.initializeTimer( )
            self.createBindings( )						

	    self.Show( True )
	    self.SetTransparent( 0 )

	#-------------------------------------------------------------------------
	def initializeParameters(self):

            with open( '.pathToATPlatform' ,'r' ) as textFile:
		    self.pathToATPlatform = textFile.readline( )

	    with open( self.pathToATPlatform + 'parameters' ,'r' ) as parametersFile:
		    line = parametersFile.readline( )

		    try:
			    self.timeGap = int( line[ line.rfind( '=' ) + 2: -1 ] )
		    except ValueError:
		    	    print '\nNiewłaściwie opisany parametr. Błąd w linii:\n%s' % line
		    	    self.timeGap = 1500

            self.mouseCursor = PyMouse( )
	    self.mousePosition = self.winWidth - 8, self.winHeight - 8
            self.mouseCursor.move( *self.mousePosition )
	    
	    self.numberOfPresses = 3

	#-------------------------------------------------------------------------
	def createGui(self):

		self.mainSizer = wx.BoxSizer( wx.VERTICAL )

		self.subSizer = wx.GridBagSizer( 4, 4 )

                b = bt.GenButton( self, -1, '', name='' )
                b.Bind( wx.EVT_LEFT_DOWN, self.onPress )

                self.subSizer.Add( b, ( 0, 0 ), wx.DefaultSpan, wx.EXPAND )

                self.subSizer.AddGrowableRow( 0 )
                self.subSizer.AddGrowableCol( 0 )

		self. mainSizer.Add( self.subSizer, proportion = 1, flag = wx.EXPAND )
		self.SetSizer( self. mainSizer )

	#-------------------------------------------------------------------------
	def initializeTimer(self):
		self.stoper = wx.Timer( self )
		self.Bind( wx.EVT_TIMER , self.timerUpdate , self.stoper )
		self.stoper.Start( self.timeGap )

	#-------------------------------------------------------------------------
	def createBindings(self):
		self.Bind( wx.EVT_CLOSE, self.OnCloseWindow )

	#-------------------------------------------------------------------------
	def OnCloseWindow(self, event):

		self.mousePosition = self.winWidth/1.85, self.winHeight/1.85	
		self.mouseCursor.move( *self.mousePosition )	

		dial = wx.MessageDialog(None, 'Czy napewno chcesz wyjść z programu?', 'Wyjście',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            
		ret = dial.ShowModal()
		
		if ret == wx.ID_YES:
			os.system( 'wmctrl -c Przeglądarka\ książek' )
			os.system( 'wmctrl -c E-book\ Viewer' )

			try:
				self.parent.parent.parent.Destroy()
				self.parent.parent.Destroy()
				self.parent.Destroy()
				self.Destroy()

			except AttributeError:
				try:
					self.parent.parent.Destroy()
					self.parent.Destroy()
					self.Destroy()

				except AttributeError:
					try:		
						self.parent.Destroy()
						self.Destroy()

					except AttributeError:
						self.Destroy()

		else:
			event.Veto()
			self.mousePosition = self.winWidth - 8, self.winHeight - 8
			self.mouseCursor.move( *self.mousePosition )	

	#-------------------------------------------------------------------------
	def onExit(self):
		if __name__ == '__main__':
			self.stoper.Stop( )
			self.Destroy( )
		else:
			self.stoper.Stop( )
			self.MakeModal( False )
			self.parent.Show( True )
			self.parent.stoper.Start( self.parent.timeGap )
			self.Destroy( )

	#-------------------------------------------------------------------------
        def onPress(self, event):
		
		self.stoper.Stop( )
		self.numberOfPresses += 1
		# print self.numberOfPresses

		if self.numberOfPresses == 1:
			self.suspendTime = time.time( )

			while True: 
				if time.time ( ) - self.suspendTime < 6:
					os.system( 'wid=`xdotool search --onlyvisible --name Przeglądarka\ książek` && xdotool windowfocus $wid && xdotool key --window $wid Page_Down' )
					os.system( 'wid=`xdotool search --onlyvisible --name E-book\ Viewer` && xdotool windowfocus $wid && xdotool key --window $wid Page_Down' )
					self.stoper.Start( self.timeGap )
					break

		elif self.numberOfPresses == 2:
			# if time.time( ) - self.suspendTime > 6:
			# 	self.stoper.Start( self.timeGap )
			# 	os.system( 'wid=`xdotool search --onlyvisible --name Przeglądarka\ książek` && xdotool windowfocus $wid && xdotool key --window $wid Page_Down' )
			# 	self.stoper.Start( self.timeGap )
			
			# else:
			bookPilot.pilot( self, id = 2 ).Show( True )
			self.Hide( )
	
		else:
			pass
		
	#-------------------------------------------------------------------------
	def timerUpdate(self, event):
		
               	self.mouseCursor.move( *self.mousePosition )
		self.numberOfPresses = 0

			
#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = suspend( parent = None, id = -1 )
        frame.Show( True )
	app.MainLoop( )
