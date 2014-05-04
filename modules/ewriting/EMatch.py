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
import numpy as np

import subprocess as sp
import shlex
from pygame import mixer

import check

#=============================================================================
class cwiczenia(wx.Frame):
	def __init__(self, parent, id):

		self.winWidth, self.winHeight = wx.DisplaySize( )
		
		wx.Frame.__init__( self , parent , id , 'EMatch' )
                style = self.GetWindowStyle( )
		self.SetWindowStyle( style | wx.STAY_ON_TOP )
		self.parent = parent

		self.Maximize( True )
		self.Center( True )
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

		with open( self.pathToATPlatform + 'spellerParameters', 'r' ) as parametersFile:
			for line in parametersFile:
				
				if line[ :line.find('=')-1 ] == 'voice':
					self.voice = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'vowelColour':
					self.vowelColour = line[ line.rfind('=')+2:-1 ]
				elif line[ :line.find('=')-1 ] == 'polishLettersColour':
					self.polishLettersColour = line[ line.rfind('=')+2:-1 ]
			
				elif not line.isspace( ):
					print 'Niewłaściwie opisane parametry'
					print 'Błąd w pliku spellerParameters w linii', line
				    
					self.voice = False
					self.vowelColour = 'red'
					self.polishLettersColour = 'blue'

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
					
					self.textSize = 80
					self.checkTime = 8000
					self.colorGrat = 'lime green'
					self.colorNiest = 'indian red'
					self.ileLuk = 1
					self.maxPoints = 2
					self.sex = 'D'

		self.flaga = 0
		self.pressFlag = True
		self.PicNr = 0
		self.result = 0

		self.labels = [ 'speak', 'literuj', 'undo', 'exit' ]
		
		self.WordsList = os.listdir( self.pathToATPlatform + 'multimedia/ewriting/pictures' )
		shuffle( self.WordsList )
                self.poczatek = True
		self.czyBack = False
		self.numberOfExtraWords = 3

		self.numberOfPresses = 1

		self.mouseCursor = PyMouse( )
		self.mousePosition = self.winWidth - 8, self.winHeight - 8
               	self.mouseCursor.move( *self.mousePosition )			

		mixer.init( )
		
	#-------------------------------------------------------------------------
	def initializeTimer(self):

                id1=wx.NewId( )
                wx.RegisterId( id1 )
		self.stoper = wx.Timer( self, id1 )
		self.Bind( wx.EVT_TIMER, self.timerUpdate, self.stoper, id1 )

                self.id3=wx.NewId( )
                wx.RegisterId( self.id3 )
                self.stoper3 = wx.Timer( self, self.id3 )

                self.id4=wx.NewId( )
                wx.RegisterId( self.id4 )
                self.stoper4=wx.Timer( self, self.id4 )
                self.Bind( wx.EVT_TIMER, self.pomocniczyStoper, self.stoper4, self.id4 )
                
		self.stoper.Start( self.timeGap )

	#-------------------------------------------------------------------------
	def timerUpdate(self, event):

		if self.control == 'tracker':
			
			if not self.poczatek: 
				try:
					# if self.button.GetBackgroundColour( ) == self.backgroundColour:
					# 	self.button.SetBackgroundColour( self.selectionColour )

					# else:
					self.button.SetBackgroundColour( self.backgroundColour )	
					self.Update()
					self.stoper.Stop( )
					self.pressFlag = False

				except AttributeError:
					pass
				
			if self.poczatek:
				time.sleep( 1 )
				self.stoper.Stop( )
				mixer.music.load( self.pathToATPlatform + 'multimedia/ewriting/voices/' + str( self.word ) + '.ogg' )
				mixer.music.play( )
				time.sleep( 2 )
				self.stoper.Start( self.timeGap )
				self.poczatek = False
				self.pressFlag = False


		else:
			self.mouseCursor.move( *self.mousePosition )

			self.numberOfPresses = 0

			if self.flaga <= self.numberOfExtraWords + 1 and self.flaga > 0:
				item = self.wordSizer.GetChildren( )
				b = item[ self.flaga-1 ].GetWindow( )
				b.SetBackgroundColour( self.backgroundColour )
				b.SetFocus( )

			else:
				if self.flaga == 0:
					item = self.subSizer.GetChildren( )
					b = item[ len( item ) - 1 ].GetWindow( )
					b.SetBackgroundColour( self.backgroundColour )
					b.SetFocus( )
				else:
					item = self.subSizer.GetChildren( )
					b = item[ self.flaga - self.numberOfExtraWords - 2 ].GetWindow( )
					b.SetBackgroundColour( self.backgroundColour )
					b.SetFocus( )

			if self.poczatek:
				time.sleep( 1 )
				self.stoper.Stop( )
				mixer.music.load( self.pathToATPlatform + 'multimedia/ewriting/voices/' + str( self.word ) + '.ogg' )
				mixer.music.play( )
				time.sleep( 2 )
				self.stoper.Start( self.timeGap )
				self.poczatek = False

			if self.flaga >= self.numberOfExtraWords + 1:
				item = self.subSizer.GetChildren( )
				b = item[ self.flaga - self.numberOfExtraWords - 1 ].GetWindow( )
				b.SetBackgroundColour( self.scanningColour )
				b.SetFocus( )
			else:
				item = self.wordSizer.GetChildren( )
				b = item[ self.flaga ].GetWindow( )
				b.SetBackgroundColour( self.scanningColour )
				b.SetFocus( )

			if self.flaga == 3 + self.numberOfExtraWords + 1: 
				self.flaga = 0
			else:
				self.flaga += 1			
	
	#-------------------------------------------------------------------------
	def createGui(self):

                if self.PicNr == len( self.WordsList ):
                        self.PicNr = 0

		if self.control != 'tracker':
			event = eval('wx.EVT_LEFT_DOWN')
		else:
			event = eval('wx.EVT_BUTTON')
                                
		self.picture = self.WordsList[ self.PicNr ]
                self.PicNr += 1
		self.path = self.pathToATPlatform + 'multimedia/ewriting/pictures/'
                im = wx.ImageFromStream( open(self.path+self.picture, "rb"))
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

		self.extraWords = [ ] #wybiera dodatkowe slowa
		while len( self.extraWords ) < self.numberOfExtraWords:
                        slowo = self.WordsList[ np.random.randint( 0, len( self.WordsList ), 1 )[ 0 ] ] 
                        slowo = slowo[ :slowo.index( '.' ) ]
			SLOWO = slowo.upper( )
                        if SLOWO not in self.extraWords and SLOWO != self.WORD:
                                self.extraWords.append( SLOWO )
                                
		b = bt.GenBitmapButton( self, -1, bitmap = picture )
		# b.name = 'picture'
		# b.SetBackgroundColour( self.backgroundColour)
		# b.Bind( event, self.onPress )

                obiekty_wyrazow = [ ]
                self.wyrazy_w_kolejnosci = [ ]
                gdzie_poprawne = np.random.randint( 0, self.numberOfExtraWords, 1 )[ 0 ]

                for i, j in enumerate( self.extraWords ):
                        be = bt.GenButton( self, -1, j )
			be.name = j
                        be.SetFont( wx.Font(60, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
                        be.SetBackgroundColour( self.backgroundColour )
                        be.Bind( event, self.onPress )
                        obiekty_wyrazow.append( be )
                        self.wyrazy_w_kolejnosci.append( j )

                be = bt.GenButton( self, -1, self.WORD )
                be.SetFont( wx.Font(60, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
		be.name = self.WORD
                be.SetBackgroundColour( self.backgroundColour )
                be.Bind( event, self.onPress )
                obiekty_wyrazow.insert( gdzie_poprawne, be )
                self.wyrazy_w_kolejnosci.insert( gdzie_poprawne, self.WORD )
                
                res = bt.GenButton( self, -1, u'TWÓJ WYNIK:   ' + str(self.result) + ' / ' + str( self.maxPoints ) )
		res.SetFont( wx.Font(27, wx.FONTFAMILY_ROMAN, wx.FONTWEIGHT_LIGHT,  False) )
		# res.name = 'points'
		# res.SetBackgroundColour( self.backgroundColour )
		# res.Bind( event, self.onPress )
		
                self.wordSizer = wx.GridSizer( self.numberOfExtraWords + 1, 1, 3, 3 )
                for item in obiekty_wyrazow:
                        self.wordSizer.Add( item, proportion = 1, flag = wx.EXPAND )                                
		
		try:
			self.subSizerP.Hide( 0 )
                        self.subSizerP.Remove( 0 )
                        self.subSizerP.Add( res, 0, wx.EXPAND ) #dodanie wyniku
                        self.subSizer0.Hide( 0 )
                        self.subSizer0.Remove( 0 )
                        self.subSizer0.Hide( 0 )
                        self.subSizer0.Remove( 0 )
		        self.subSizer0.Add( self.wordSizer, 0, wx.EXPAND ) #tutaj trzeba dodac caly zagniezdzony subsizer ze slowami
                        self.subSizer0.Add( b, 0, wx.EXPAND) #dodanie zdjecia
                        items=self.subSizer.GetChildren( )
                        for item in items:
                                b=item.GetWindow( )
                                b.SetBackgroundColour( self.backgroundColour )
                                b.Update
                        

                except AttributeError:
                        if self.czyBack:
                                self.czyBack = False
                        else:
                                self. mainSizer = wx.BoxSizer( wx.VERTICAL )

                        self.subSizerP=wx.GridSizer( 1, 1, 3, 3 )
                        self.subSizer0 = wx.GridSizer( 1, 2, 3, 3 )
                        self.subSizer=wx.GridSizer( 1, 4, 3, 3 )
                        self.subSizerP.Add( res, 0, wx.EXPAND )
		        self.subSizer0.Add( self.wordSizer, 0, wx.EXPAND )
                        self.subSizer0.Add( b, 0, wx.EXPAND )
                        self.icons = sorted( os.listdir( self.pathToATPlatform + 'icons/ewriting/') )[ 1: ] #bo pierwszy to 1speller a tu ma go nie byc
                        self.path = self.pathToATPlatform + 'icons/ewriting/'

                        for idx, icon in enumerate( self.icons ):

                                if icon[ 0 ].isdigit( ):
                                        k = wx.BitmapFromImage( wx.ImageFromStream( open(self.path+icon, "rb") ) )
                                        b = bt.GenBitmapButton( self, -1, bitmap = k )
					b.name = self.labels[ idx ]
                                        b.SetBackgroundColour( self.backgroundColour )
                                        b.Bind( event, self.onPress )
                                        self.subSizer.Add( b, 0,wx.EXPAND )

                        self. mainSizer.Add( self.subSizerP, 1, wx.EXPAND | wx.BOTTOM, 2 )
                        self. mainSizer.Add( self.subSizer0, 7, wx.EXPAND )
                        self. mainSizer.Add( self.subSizer, 2, wx.EXPAND | wx.TOP, 2 )

                        self.SetSizer( self.mainSizer, deleteOld = True )

                self.SetBackgroundColour( 'black' )
		self.Layout( )
		self.Refresh( )
		self.Center( )
		self.MakeModal( True )
		self.flaga = 0
		self.poczatek = True

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
			if self.control == 'tracker':
				self.parent.stoper.Start( 0.15 * self.parent.timeGap )
			else:
				self.parent.stoper.Start( self.parent.timeGap )
				
			self.Destroy( )

	#-------------------------------------------------------------------------
	def onPress(self, event):

		if self.control == 'tracker':
			if self.pressFlag == False:
				self.button = event.GetEventObject( )
				self.button.SetBackgroundColour( self.selectionColour )
				self.Update()
				self.pressFlag = True
				self.name = self.button.name
				# print self.name

				# if self.flaga == 0 :
				# 	items = self.subSizer.GetChildren( )
				# 	item=items[ 3 ]

				# else:
				# 	if self.flaga >= self.numberOfExtraWords + 2:
				# 		items = self.subSizer.GetChildren( )
				# 		item=items[ self.flaga - self.numberOfExtraWords - 2 ]
				# 	else:
				# 		items = self.wordSizer.GetChildren( )
				# 		item=items[ self.flaga -1 ]

				# b = item.GetWindow( )
				# b.SetBackgroundColour( self.selectionColour )
				# b.SetFocus( )
				# b.Update( )

				# if 'speller' in self.icons[ self.flaga - self.numberOfExtraWords - 2 ] and self.flaga >= self.numberOfExtraWords + 2:
				# 	pass

				# if self.name == 'points' or self.name == 'picture':
				# 	pass

				if self.name == 'speak':
					# time.sleep( 1 )
					self.stoper.Stop( )
					mixer.music.load( self.pathToATPlatform + 'multimedia/ewriting/voices/' + str( self.word ) + '.ogg' )
					mixer.music.play( )
					self.stoper4.Start( 2000 )

				elif self.name == 'literuj':
					self.stoper.Stop( )
					if str( self.word ) + '.ogg' not in os.listdir( self.pathToATPlatform + 'multimedia/ewriting/spelling/' ):        
						command = 'sox -m ' + self.pathToATPlatform + 'sounds/phone/' + list( self.word )[ 0 ].swapcase( ) + '.wav'
						ile = 0
						for l in list( self.word )[ 1: ]:
							ile += 2
							command += ' "|sox ' + self.pathToATPlatform + 'sounds/phone/' + l.swapcase( ) + '.wav' + ' -p pad ' + str( ile ) + '"'
						command += ' ' + self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.word + '.ogg'
						wykonaj = sp.Popen( shlex.split( command ) )

					# time.sleep( 1.5 )
					do_literowania = mixer.Sound( self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.word + '.ogg' )
					do_literowania.play( )
					self.stoper4.Start( ( do_literowania.get_length( ) + 0.5 ) * 1000 )

				elif self.name == 'undo':

					self.stoper.Stop( )

					self.createGui( )			
					self.stoper.Start( self.timeGap )

				elif self.name == 'exit':
					self.onExit( )

				else:
					if self.name == self.WORD:
						self.ownWord = self.WORD

					else:
						self.ownWord=''

					self.stoper.Stop( )
					self.check( )

		else:
			self.numberOfPresses += 1

			if self.numberOfPresses == 1:

				if self.flaga == 0 :
					items = self.subSizer.GetChildren( )
					item=items[ 3 ]

				else:
					if self.flaga >= self.numberOfExtraWords + 2:
						items = self.subSizer.GetChildren( )
						item=items[ self.flaga - self.numberOfExtraWords - 2 ]
					else:
						items = self.wordSizer.GetChildren( )
						item=items[ self.flaga -1 ]

				b = item.GetWindow( )
				b.SetBackgroundColour( self.selectionColour )
				b.SetFocus( )
				b.Update( )

				if 'speller' in self.icons[ self.flaga - self.numberOfExtraWords - 2 ] and self.flaga >= self.numberOfExtraWords + 2:
					pass

				elif self.flaga == 0:
					self.onExit( )

				elif 'speak' in self.icons[ self.flaga - self.numberOfExtraWords - 2 ] and self.flaga >= self.numberOfExtraWords + 2:
					time.sleep( 1 )
					self.stoper.Stop( )
					mixer.music.load( self.pathToATPlatform + 'multimedia/ewriting/voices/' + str( self.word ) + '.ogg' )
					mixer.music.play( )
					self.stoper4.Start( 2000 )

				elif 'literuj' in  self.icons[ self.flaga - self.numberOfExtraWords - 2 ] and self.flaga >= self.numberOfExtraWords + 2:
					self.stoper.Stop( )
					if str( self.word ) + '.ogg' not in os.listdir( self.pathToATPlatform + 'multimedia/ewriting/spelling/' ):        
						command = 'sox -m ' + self.pathToATPlatform + 'sounds/phone/' + list( self.word )[ 0 ].swapcase( ) + '.wav'
						ile = 0
						for l in list( self.word )[ 1: ]:
							ile += 2
							command += ' "|sox ' + self.pathToATPlatform + 'sounds/phone/' + l.swapcase( ) + '.wav' + ' -p pad ' + str( ile ) + '"'
						command += ' ' + self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.word + '.ogg'
						wykonaj = sp.Popen( shlex.split( command ) )

					time.sleep( 1.5 )
					do_literowania = mixer.Sound( self.pathToATPlatform + 'multimedia/ewriting/spelling/' + self.word + '.ogg' )
					do_literowania.play( )
					self.stoper4.Start( ( do_literowania.get_length( ) + 0.5 ) * 1000 )

				elif 'undo' in self.icons[ self.flaga - self.numberOfExtraWords - 2 ] and self.flaga >= self.numberOfExtraWords + 2 :

					self.stoper.Stop( )

					self.createGui( )			
					self.stoper.Start( self.timeGap )

				else:
					if self.wyrazy_w_kolejnosci[ self.flaga - 1 ] == self.WORD:
						self.ownWord = self.WORD

					else:
						self.ownWord=''

					self.stoper.Stop( )
					self.check( )

			else:
				event.Skip( )

	#-------------------------------------------------------------------------
        def pomocniczyStoper(self, event):
                self.stoper4.Stop( )
                self.stoper.Start( self.timeGap )
        
	#-------------------------------------------------------------------------
	def check(self):

                self.mainSizer.Clear( deleteWindows = True )
		self.checkW = check.check( self )

	#-------------------------------------------------------------------------
	def back(self):
                
		self.czyBack = True
		
		del self.checkW
                self.mainSizer.Clear( deleteWindows = True )
		
		self.createGui( )
		self.stoper.Start( self.timeGap )

		
#=============================================================================
if __name__ == '__main__':

	app = wx.PySimpleApp( )
	frame = cwiczenia( parent = None, id = -1 )
	frame.Show( )
	app.MainLoop( )
