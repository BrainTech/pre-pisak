#!/bin/env python2.7
# -*- coding: utf-8 -*-

# This file is part of EPlatform.
#
# EPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EPlatform. If not, see <http://www.gnu.org/licenses/>.

import wxversion
wxversion.select('2.8')

import os, time
from random import shuffle

import wx
import wx.lib.buttons as bt
from pymouse import PyMouse

import subprocess as sp
import shlex
from pygame import mixer

import check, spellerCW

#=============================================================================
class cwiczenia(wx.Frame):
	def __init__(self, parent, id):

		self.winWidth, self.winHeight = wx.DisplaySize( )
		
		wx.Frame.__init__( self , parent , id , 'EGaps' )
                style = self.GetWindowStyle( )
		self.SetWindowStyle( style | wx.STAY_ON_TOP ) 
		self.parent = parent

		self.Maximize( True )
		self.Centre( True )
		self.MakeModal( True )

		self.initializeParameters( )
		self.createGui( )
		self.createBindings( )

		self.initializeTimer( )
		
	#-------------------------------------------------------------------------	
	def initializeParameters(self):

		with open( './.pathToATPlatform' ,'r' ) as textFile:
			self.pathToATPlatform = textFile.readline( )

		with open( self.pathToATPlatform + 'parameters', 'r' ) as parametersFile:
			for line in parametersFile:

				if line[ :line.find('=')-1 ] == 'timeGap':
					self.timeGap = int( line[ line.rfind('=')+2:-1 ] )
				elif line[ :line.find('=')-1 ] == 'backgroundColour':
					self.backgroundColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'textColour':
					self.textColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'scanningColour':
					self.scanningColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'selectionColour':
					self.selectionColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'filmVolume':
					self.filmVolumeLevel = int( line[ line.rfind('=')+2:-1 ] )
				elif line[ :line.find('=')-1 ] == 'musicVolume':
					self.musicVolumeLevel = int( line[ line.rfind('=')+2:-1 ] )
				elif line[ :line.find('=')-1 ] == 'control':
					self.control = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'x_border':
					self.xBorder = int( line[ line.rfind('=')+2:-1 ] )
				elif line[ :line.find('=')-1 ] == 'y_border':
					self.yBorder = int( line[ line.rfind('=')+2:-1 ] )

				elif not line.isspace( ):
					print 'Niewłaściwie opisane parametry'
					print 'Błąd w linii', line
					
					self.timeGap = 1500
					self.backgroundColour = 'white'
					self.textColour = 'black'
					self.scanningColour =  '#E7FAFD'
					self.selectionColour = '#9EE4EF'
					self.filmVolumeLevel = 100
					self.musicVolumeLevel = 70
					self.control = 'switch'
					self.xBorder = 4
					self.yBorder = 4 

                with open( self.pathToATPlatform + 'ewritingParameters', 'r' ) as parametersFile:
			for line in parametersFile:                                                                

                                if line[ :line.find('=')-1 ] == 'textSize':
					self.textSize = int( line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'maxPoints':
					self.maxPoints = int(line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'checkTime':
                                        self.checkTime = int(line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'colorGrat':
					self.colorGrat = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'colorNiest':
                                        self.colorNiest = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'ileLuk':
                                        self.ileLuk = int(line[ line.rfind('=')+2:-1 ])
				elif line[ :line.find('=')-1 ] == 'sex':
                                        self.sex = line[ line.rfind('=')+2:-1 ]
		
				elif not line.isspace( ):
					print 'Niewłaściwie opisane parametry'
					print 'Błąd w linii', line
					print 'Wczytano parametry domyślne'
					
					self.textSize = 80
					self.checkTime = 8000
					self.colorGrat = 'lime green'
					self.colorNiest = 'indian red'
					self.ileLuk = 1
					self.maxPoints = 2
					self.sex = 'D'

		self.ownWord = ''
		self.flaga = 0
		self.PicNr = 0
		self.result = 0

		self.WordsList = os.listdir( self.pathToATPlatform + 'multimedia/ewriting/pictures' )
		shuffle( self.WordsList )

                self.poczatek = True
		self.czyBack = False

		self.numberOfPresses = 1
		self.pressFlag = False
		
		if self.control != 'tracker':
			self.mouseCursor = PyMouse( )
			self.mousePosition = self.winWidth - 8, self.winHeight - 8
			self.mouseCursor.move( *self.mousePosition )			

		mixer.init( )

	#-------------------------------------------------------------------------	
	def initializeTimer(self):

                id1 = wx.NewId( )
                wx.RegisterId( id1 )
		self.stoper = wx.Timer( self, id1 )
		self.Bind( wx.EVT_TIMER, self.timerUpdate, self.stoper,id1 )
		
		self.id2 = wx.NewId( )
                wx.RegisterId( self.id2 )
                self.stoper2 = wx.Timer( self, self.id2 )

                self.id3 = wx.NewId( )
                wx.RegisterId( self.id3 )
                self.stoper3 = wx.Timer( self, self.id3 )

                self.id4 = wx.NewId( )
                wx.RegisterId( self.id4 )
                self.stoper4=wx.Timer( self, self.id4 )
                self.Bind( wx.EVT_TIMER, self.pomocniczyStoper, self.stoper4, self.id4 )
                
		# if self.control != 'tracker':
		self.stoper.Start( self.timeGap * 0.15 )

	#-------------------------------------------------------------------------		
	def createGui( self ):

		self.pressFlag = False

                if self.PicNr == len( self.WordsList ):
                        self.PicNr = 0

		self.picture = self.WordsList[ self.PicNr ]
                self.PicNr += 1

		self.path = self.pathToATPlatform + 'multimedia/ewriting/pictures/'

		if self.control != 'tracker':
			event = eval('wx.EVT_LEFT_DOWN')
		else:
			event = eval('wx.EVT_BUTTON')

                im = wx.ImageFromStream( open( self.path + self.picture, "rb" ) )

		x = im.GetWidth( )
		y = im.GetHeight( )

		if x > y:
			im = im.Scale( 500, 400 )
                elif x == y:
                        im = im.Scale( 500, 500 )
                else:
                        im = im.Scale( 400, 500 )

		picture = wx.BitmapFromImage( im )
		self.word = self.picture[ :self.picture.index( '.' ) ]
		self.WORD = self.word.upper( )

		b = bt.GenBitmapButton( self, -1, bitmap=picture )
		# b.SetBackgroundColour( self.backgroundColour )
		b.Bind( event, self.onPress )

                be = bt.GenButton( self, -1, self.WORD )
		be.SetFont( wx.Font( self.textSize, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False ) )
		# be.SetBackgroundColour( self.backgroundColour )
		be.Bind( event, self.onPress )

                res = bt.GenButton( self, -1, u'TWÓJ WYNIK:   ' + str( self.result ) + ' / ' + str( self.maxPoints ) )
		res.SetFont( wx.Font(27, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
		# res.SetBackgroundColour( self.backgroundColour )
		res.Bind( event, self.onPress )
		
		try:
                        self.subSizerP.Hide( 0 )
                        self.subSizerP.Remove( 0 )
                        self.subSizerP.Add( res, 0, wx.EXPAND )
                        self.subSizer0.Hide( 0 )
                        self.subSizer0.Remove( 0 )
                        self.subSizer0.Hide( 0 )
                        self.subSizer0.Remove( 0 )
                        self.subSizer0.Add( b, 0, wx.EXPAND )
		        self.subSizer0.Add( be, 0, wx.EXPAND )

		        items = self.subSizer.GetChildren( )

                        for i in items:
                                b=i.GetWindow( )
                                b.SetBackgroundColour( self.backgroundColour )
                                b.Update
                                
                except AttributeError:
                        if self.czyBack:
                                self.czyBack = False
                        else:
                                self. mainSizer = wx.BoxSizer( wx.VERTICAL )

                        self.subSizerP = wx.GridSizer( 1, 1, self.xBorder, self.yBorder )
                        self.subSizer0 = wx.GridSizer( 1, 2, self.xBorder, self.yBorder )
                        self.subSizer=wx.GridSizer( 1, 5, self.xBorder, self.yBorder )
                        self.subSizerP.Add( res, 0, wx.EXPAND )
                        self.subSizer0.Add( b, 0, wx.EXPAND )
		        self.subSizer0.Add( be, 0, wx.EXPAND )

                        self.icons = sorted( os.listdir( self.pathToATPlatform + 'icons/ewriting/' ) )
                        self.path = self.pathToATPlatform + 'icons/ewriting/'

                        for idx, icon in enumerate( self.icons ):
                                if icon[ 0 ].isdigit( ):
                                        i = wx.BitmapFromImage( wx.ImageFromStream( open(self.path+icon, "rb") ) )
                                        b = bt.GenBitmapButton( self, -1, bitmap = i )
                                        b.SetBackgroundColour( self.backgroundColour )
					b.name = idx
                                        b.Bind( event, self.onPress )
                                        self.subSizer.Add( b, 0, wx.EXPAND )

                        self. mainSizer.Add( self.subSizerP, proportion = 1, flag = wx.EXPAND )
                        self. mainSizer.Add( self.subSizer0, proportion = 7, flag = wx.EXPAND | wx.TOP | wx.BOTTOM, border = self.xBorder )
                        self. mainSizer.Add( self.subSizer, proportion = 2, flag = wx.EXPAND )
                        self.SetSizer( self. mainSizer, deleteOld = True )

                self.SetBackgroundColour( 'black' )
		self.Layout( )
		self.Refresh( )
		self.Center( )
		self.MakeModal( True ) 
		self.flaga = 0
		self.poczatek = True

	#-------------------------------------------------------------------------
	def createBindings(self):
		self.Bind( wx.EVT_CLOSE , self.OnCloseWindow )

	#-------------------------------------------------------------------------	
	def OnCloseWindow(self, event):
		
		if self.control != 'tracker':
			if True in [ 'debian' in item for item in os.uname( ) ]:				
				self.mousePosition = self.winWidth/6.5, self.winHeight/6.
				self.mouseCursor.move( *self.mousePosition )
			else:
				self.mousePosition = self.winWidth/1.85, self.winHeight/1.85	
				self.mouseCursor.move( *self.mousePosition )	

		dial = wx.MessageDialog(None, 'Czy napewno chcesz wyjść z programu?', 'Wyjście',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            
		ret = dial.ShowModal( )
		
		if ret == wx.ID_YES:
			try:
				self.parent.parent.parent.parent.Destroy()
				self.parent.parent.parent.Destroy()
				self.parent.parent.Destroy()
				self.parent.Destroy()
				self.Destroy()
				
			except AttributeError:
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
			event.Veto( )

			if self.control != 'tracker':
				self.mousePosition = self.winWidth - 8, self.winHeight - 8
				self.mouseCursor.move( *self.mousePosition )	

	#-------------------------------------------------------------------------	
	def onExit( self ):

		if __name__ == '__main__':
			self.stoper.Stop( )
			self.Destroy( )
		else:
			self.stoper.Stop( )
			self.MakeModal( False )
			self.parent.Show( True )
			if self.control == 'tracker':
				self.parent.stoper.Start( 0.15 * self.parent.timeGap )
			else:
				self.parent.stoper.Start( self.parent.timeGap )

			self.Destroy( )

	#-------------------------------------------------------------------------	
	def onPress( self, event ):

		if self.control == 'tracker':
			if self.pressFlag == False:
				try:
					self.button = event.GetEventObject( )
					self.name = self.button.name
					self.button.SetBackgroundColour( self.selectionColour )
					self.Update()
					self.pressFlag = True

					if self.name == 0:
						self.stoper.Stop( )
						self.mainSizer.Clear( deleteWindows = True )
						self.spellerW = spellerCW.speller( self )
						self.Bind( wx.EVT_TIMER, self.spellerW.timerUpdate, self.stoper2, self.id2 )
						self.stoper2.Start( self.spellerW.timeGap )

					if self.name == 4:
						self.onExit( )

					if self.name == 1:
						# time.sleep( 0.5 )
						# self.stoper.Stop( )
						mixer.music.load( self.pathToATPlatform + 'multimedia/ewriting/voices/' + str( self.word ) + '.ogg' )
						mixer.music.play( )
						self.stoper.Start( self.timeGap )
						# self.stoper4.Start( 2000 )

					if self.name == 2:
						self.stoper.Stop( )

						if str( self.word ) + '.ogg' not in os.listdir( self.pathToATPlatform + 'multimedia/ewriting/spelling/' ):        
							command = 'sox -m '+ self.pathToATPlatform + 'sounds/phone/' + list( self.word )[ 0 ].swapcase( ) + '.wav'
							ile = 0

							for l in list( self.word )[ 1: ]:
								ile += 2
								command += ' "|sox ' + self.pathToATPlatform + 'sounds/phone/' + l.swapcase() + '.wav' + ' -p pad ' + str( ile ) + '"'

							command += ' ' + self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.word + '.ogg'
							wykonaj = sp.Popen( shlex.split( command ) )

						# time.sleep( 1.5 )
						do_literowania = mixer.Sound( self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.word + '.ogg' )
						do_literowania.play( )
						self.stoper4.Start( ( do_literowania.get_length( ) + 0.5 ) * 1000 )

					if self.name == 3:
						# self.button = event.GetEventObject( )
						# self.button.SetBackgroundColour( self.selectionColour )
						self.stoper.Stop( )
						self.createGui( )
						self.stoper.Start( self.timeGap*0.15 )

				except AttributeError:
					pass
		else:
			self.numberOfPresses += 1

			if self.numberOfPresses == 1:

				item = self.subSizer.GetItem( self.flaga - 1 )
				b = item.GetWindow( )
				b.SetBackgroundColour( self.selectionColour )
				b.SetFocus( )
				b.Update( )

				if 'speller' in self.icons[ self.flaga - 1 ]:
					self.stoper.Stop( )
					self.mainSizer.Clear( deleteWindows = True )
					self.spellerW = spellerCW.speller( self )
					self.Bind( wx.EVT_TIMER, self.spellerW.timerUpdate, self.stoper2, self.id2 )
					self.stoper2.Start( self.spellerW.timeGap )

				if 'cancel' in self.icons[ self.flaga - 1 ] or self.flaga == 0:
					self.onExit( )

				if 'speak' in self.icons[ self.flaga - 1 ]:
					time.sleep( 1 )
					self.stoper.Stop( )
					mixer.music.load( self.pathToATPlatform + 'multimedia/ewriting/voices/' + str( self.word ) + '.ogg' )
					mixer.music.play( )
					self.stoper4.Start( 2000 )

				if 'literuj' in  self.icons[ self.flaga - 1 ]:
					self.stoper.Stop( )

					if str( self.word ) + '.ogg' not in os.listdir( self.pathToATPlatform + 'multimedia/ewriting/spelling/' ):        
						command = 'sox -m '+ self.pathToATPlatform + 'sounds/phone/' + list( self.word )[ 0 ].swapcase( ) + '.wav'
						ile = 0

						for l in list( self.word )[ 1: ]:
							ile += 2
							command += ' "|sox ' + self.pathToATPlatform + 'sounds/phone/' + l.swapcase() + '.wav' + ' -p pad ' + str( ile ) + '"'

						command += ' ' + self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.word + '.ogg'
						wykonaj = sp.Popen( shlex.split( command ) )

					time.sleep( 1.5 )
					do_literowania = mixer.Sound( self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.word + '.ogg' )
					do_literowania.play( )
					self.stoper4.Start( ( do_literowania.get_length( ) + 0.5 ) * 1000 )

				if 'undo' in self.icons[ self.flaga - 1 ]:

					self.stoper.Stop( )
					self.createGui( )		
					self.stoper.Start( self.timeGap )

			else:
				event.Skip( )

	#-------------------------------------------------------------------------	
        def pomocniczyStoper(self, event):

                self.stoper4.Stop( )

                if hasattr( self, 'spellerW' ):
                        self.stoper2.Start( self.spellerW.timeGap )
                else:
                        self.stoper.Start( self.timeGap )

	#-------------------------------------------------------------------------	        
	def check(self):

                self.mainSizer.Clear( deleteWindows = True )
		self.checkW = check.check( self )
		# self.Bind( wx.EVT_TIMER, self.checkW.zamknij, self.stoper3, self.id3 )

	#-------------------------------------------------------------------------	
	def back(self):

                self.czyBack = True

                try:
                        del self.spellerW
                except NameError:
                        del self.checkW

                self.mainSizer.Clear( deleteWindows = True )
		self.createGui( )
		self.stoper.Start( self.timeGap )

	#-------------------------------------------------------------------------	
	def timerUpdate( self, event ):

		if self.control == 'tracker':
			try:
				# if self.button.GetBackgroundColour( ) == self.backgroundColour:
				# 	self.button.SetBackgroundColour( self.selectionColour )

				# else:
				self.button.SetBackgroundColour( self.backgroundColour )	
					
				self.stoper.Stop( )
				self.pressFlag = False

			except AttributeError:
				pass

			if self.poczatek:
				# time.sleep(  )
				self.stoper.Stop( )
				mixer.music.load( self.pathToATPlatform+'multimedia/ewriting/voices/' + str( self.word ) + '.ogg' )
				mixer.music.play( )
				self.poczatek = False

		else:
			self.mouseCursor.move( *self.mousePosition )

			self.numberOfPresses = 0

			if self.poczatek:
				time.sleep( 1 )
				self.stoper.Stop( )
				mixer.music.load( self.pathToATPlatform+'multimedia/ewriting/voices/' + str( self.word ) + '.ogg' )
				mixer.music.play( )
				time.sleep( 2 )
				self.stoper.Start( self.timeGap )
				self.poczatek = False

			for i in range( 5 ):
				item = self.subSizer.GetItem( i )
				b = item.GetWindow( )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetFocus( )

			if self.flaga == 5:
				item = self.subSizer.GetItem( 0 )
				b = item.GetWindow( )
				b.SetBackgroundColour( self.scanningColour )
				b.SetFocus( )

				self.flaga = 1

			else:
				item = self.subSizer.GetItem( self.flaga )
				b = item.GetWindow( )
				b.SetBackgroundColour( self.scanningColour )
				b.SetFocus( )

				self.flaga += 1

		
#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = cwiczenia( parent = None, id = -1 ) 
	frame.Show( )
	app.MainLoop( )
