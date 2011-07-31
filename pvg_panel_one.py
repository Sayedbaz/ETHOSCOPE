#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       pvg_panel_one.py
#       
#       Copyright 2011 Giorgio Gilestro <giorgio@gilest.ro>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import wx, os
from pvg_common import previewPanel, options

import wx.lib.newevent
ThumbnailClickedEvt, EVT_THUMBNAIL_CLICKED = wx.lib.newevent.NewCommandEvent()

from wxPython.lib.filebrowsebutton import FileBrowseButton, DirBrowseButton

class thumbnailPanel(previewPanel):
    '''
    A small preview Panel to be used as thumbnail
    '''
    
    def __init__( self, parent, monitor_number, thumbnailSize=(320,240) ):
        previewPanel.__init__(self, parent, size=thumbnailSize)

        self.number = int(monitor_number)
        self.allowEditing = False
        
        self.displayNumber()

        self.Bind(wx.EVT_LEFT_UP, self.onLeftClick)


    def displayNumber(self):
        '''
        '''
        # font type: wx.DEFAULT, wx.DECORATIVE, wx.ROMAN, wx.SCRIPT, wx.SWISS, wx.MODERN
        # slant: wx.NORMAL, wx.SLANT or wx.ITALIC
        # weight: wx.NORMAL, wx.LIGHT or wx.BOLD
        #font1 = wx.Font(10, wx.SWISS, wx.ITALIC, wx.NORMAL)
        # use additional fonts this way ...
        pos = int(self.size[0]/2 - 20), int(self.size[1]/2 - 20),
        font1 = wx.Font(35, wx.SWISS, wx.NORMAL, wx.NORMAL)
        text1 = wx.StaticText( self, wx.ID_ANY, '%s' % (self.number+1), pos)
        text1.SetFont(font1)    
        
    def onLeftClick(self, evt):
        '''
        Send signal around that the thumbnail was clicked
        '''
        event = ThumbnailClickedEvt(self.GetId())
        
        event.id = self.GetId()
        event.number = self.number
        event.thumbnail = self
       
        self.GetEventHandler().ProcessEvent(event)
        


class panelGridView(wx.ScrolledWindow):
    '''
    '''
    def __init__(self, parent, gridSize, thumbnailSize=(320,240) ):
        '''
        '''
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY, size=(-1,600))
        self.SetScrollbars(1, 1, 1, 1)
        self.SetScrollRate(10, 10)
        self.parent = parent
        self.thumbnailSize = thumbnailSize
        
        grid_mainSizer = wx.GridSizer(6,3,2,2)

        #Populate the thumbnail grid
        self.previewPanels = []
        for i in range (int(gridSize)):
            self.previewPanels.append ( thumbnailPanel(self, monitor_number=i, thumbnailSize=self.thumbnailSize) )
            grid_mainSizer.Add(self.previewPanels[i])#, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
            
        self.SetSizer(grid_mainSizer)
        
        self.Bind(EVT_THUMBNAIL_CLICKED, self.onThumbnailClicked)
        
    def onThumbnailClicked(self, event):
        '''
        Relay event to sibling panel
        '''
        wx.PostEvent(self.parent.lowerPanel, event)
        event.Skip()
        
        
class panelConfigure(wx.Panel):
    '''
    '''
    def __init__(self, parent):
        '''
        '''
        wx.Panel.__init__(self, parent, wx.ID_ANY, size=(-1,300), style=wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.thumbnail = None
        self.mask_file = None
        self.source = None
        self.sourceType = None
        self.track = None
        
        lowerSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #Static box1
        sb_1 = wx.StaticBox(self, -1, "Select Monitor")#, size=(250,-1))
        sbSizer_1 = wx.StaticBoxSizer (sb_1, wx.VERTICAL)
        
        n_monitors = options.GetOption("Monitors")
        self.MonitorList = ['Monitor %s' % (int(m) + 1) for m in range( n_monitors )]
        self.thumbnailNumber = wx.ComboBox(self, -1, size=(-1,-1) , choices=self.MonitorList, style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        self.Bind ( wx.EVT_COMBOBOX, self.onChangingMonitor, self.thumbnailNumber)

        self.currentSource = wx.TextCtrl (self, -1, "No Source Selected", style=wx.TE_READONLY)
        
        btnSizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.btnPlay = wx.Button( self, wx.ID_FORWARD, label="Play")
        self.btnStop = wx.Button( self, wx.ID_STOP, label="Stop")
        self.Bind(wx.EVT_BUTTON, self.onPlay, self.btnPlay)
        self.Bind(wx.EVT_BUTTON, self.onStop, self.btnStop)
        self.btnPlay.Enable(False); self.btnStop.Enable(False)
        
        btnSizer_1.Add ( self.btnPlay , 0, wx.ALIGN_LEFT|wx.ALL, 5 )
        btnSizer_1.Add ( self.btnStop , 0, wx.ALIGN_RIGHT|wx.LEFT|wx.TOP|wx.DOWN, 5 )
        
        sbSizer_1.Add ( self.thumbnailNumber, 0, wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
        sbSizer_1.Add (self.currentSource, 0, wx.EXPAND|wx.ALIGN_CENTRE|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
        sbSizer_1.Add ( btnSizer_1, 0, wx.EXPAND|wx.ALIGN_BOTTOM|wx.TOP, 5 )
       
        lowerSizer.Add (sbSizer_1, 0, wx.EXPAND|wx.ALL, 5)
        
        #Static box2
        sb_2 = wx.StaticBox(self, -1, "Select Video input" )
        sbSizer_2 = wx.StaticBoxSizer (sb_2, wx.VERTICAL)
        grid2 = wx.FlexGridSizer( 0, 2, 0, 0 )

        n_cams = options.GetOption("Webcams")
        self.WebcamsList = [ 'Webcam %s' % (int(w) +1) for w in range( n_cams ) ]
        rb1 = wx.RadioButton(self, -1, 'Camera', style=wx.RB_GROUP)
        source1 = wx.ComboBox(self, -1, size=(285,-1) , choices = self.WebcamsList, style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        self.Bind(wx.EVT_COMBOBOX, self.sourceCallback, source1)
        
        rb2 = wx.RadioButton(self, -1, 'File' )
        source2 = FileBrowseButton(self, -1, labelText='', size=(300,-1), changeCallback = self.sourceCallback)
        
        rb3 = wx.RadioButton(self, -1, 'Folder' )
        source3 = DirBrowseButton (self, style=wx.DD_DIR_MUST_EXIST, labelText='', size=(300,-1), changeCallback = self.sourceCallback)
        
        self.applyButton = wx.Button( self, wx.ID_APPLY  )
        
        self.controls = []
        self.controls.append((rb1, source1))
        self.controls.append((rb2, source2))
        self.controls.append((rb3, source3))

        for radio, source in self.controls:
            grid2.Add( radio , 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )
            grid2.Add( source , 0, wx.ALIGN_CENTRE|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )
            self.Bind(wx.EVT_RADIOBUTTON, self.onChangeSource, radio )
            source.Enable(False)
        
        self.controls[0][1].Enable(True)
        
        grid2.Add(wx.StaticText(self, -1, ""))
        grid2.Add( self.applyButton, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
        self.Bind(wx.EVT_BUTTON, self.onApplySource, self.applyButton)
        
        sbSizer_2.Add( grid2 )        
        lowerSizer.Add(sbSizer_2, 0, wx.EXPAND|wx.ALL, 5)
       
        
        sb_3 = wx.StaticBox(self, -1, "Set Tracking Parameters")
        sbSizer_3 = wx.StaticBoxSizer (sb_3, wx.VERTICAL)
        self.activateTracking = wx.CheckBox(self, -1, "Activate Tracking")
        self.activateTracking.SetValue(False)
        self.Bind ( wx.EVT_CHECKBOX, self.onActivateTracking)
        
        self.pickMaskBrowser = FileBrowseButton(self, -1, labelText='Mask File')
                
        sbSizer_3.Add ( self.activateTracking , 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
        sbSizer_3.Add ( self.pickMaskBrowser , 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5 )
        
        lowerSizer.Add(sbSizer_3, -1, wx.EXPAND|wx.ALL, 5)


        self.SetSizer(lowerSizer)
        self.Bind(EVT_THUMBNAIL_CLICKED, self.onThumbnailClicked)

    def onPlay (self, event):
        '''
        '''
        if self.thumbnail:
            self.thumbnail.Play()
            self.btnStop.Enable(True)
        
    def onStop (self, event):
        '''
        '''
        if self.thumbnail:
            self.thumbnail.Stop()
            self.btnStop.Enable(False)

    def onThumbnailClicked(self, evt):
        '''
        Picking thumbnail by clicking on it
        '''
        self.monitor_number = evt.number
        self.thumbnail = evt.thumbnail
        self.thumbnailNumber.SetValue(self.MonitorList[self.monitor_number])
        self.updateThumbnail()

    def onChangingMonitor(self, evt):
        '''
        Picking thumbnail by using the dropbox
        '''
        sel = evt.GetString()
        self.monitor_number = self.MonitorList.index(sel)
        self.thumbnail = self.parent.scrollThumbnails.previewPanels[self.monitor_number]         #this is not very elegant
        self.updateThumbnail()

    def updateThumbnail(self):
        '''
        Refreshing thumbnail data
        '''
        if options.HasMonitor(self.monitor_number):
            sourceType, source, track, mask_file = options.GetMonitor(self.monitor_number)
        else:
            sourceType, source, track, mask_file = [0, '', False, '']

        self.source = self.thumbnail.source = source
        self.sourceType = self.thumbnail.sourceType = sourceType
        self.thumbnail.track = track
        
        active = self.thumbnail.hasMonitor()
        self.applyButton.Enable ( active )
        self.btnPlay.Enable ( active )
        self.btnStop.Enable ( active and self.thumbnail.isPlaying )
        
        for radio, source in self.controls:
            source.Enable(False); source.SetValue('')

        text = os.path.split(self.source)[1] or "No Source Selected"
        self.currentSource.SetValue( text )
        
        radio, source = self.controls[self.sourceType]
        radio.SetValue(True); source.Enable(True)
        source.SetValue(self.source)
      
        self.activateTracking.SetValue(self.thumbnail.track)
        self.pickMaskBrowser.SetValue(mask_file or '')

    def sourceCallback (self, event):
        '''
        '''
        self.applyButton.Enable(True)


    def onChangeSource(self, event):
        '''
        
        '''
        
        radio_selected = event.GetEventObject()

        for radio, source in self.controls:
            if radio is radio_selected:
                source.Enable(True)
            else:
                source.Enable(False)
        
        self.applyButton.Enable(True)
 
    def onApplySource(self, event):
        '''
        '''
        
        for (r, s), st in zip(self.controls,range(3)):
            if r.GetValue():
                source = s.GetValue()
                sourceType = st
        
        track = self.activateTracking.GetValue()
        self.mask_file = self.pickMaskBrowser.GetValue()
        
        if self.thumbnail:

            self.thumbnail.source = source
            self.thumbnail.sourceType = sourceType

            self.currentSource.SetValue( os.path.split(source)[1] )
            
            if sourceType > 0:
                camera = source
            else:
                camera = self.WebcamsList.index(source)
            
            ts = self.thumbnail.size
            self.thumbnail.setMonitor(camera, ts )
            self.btnPlay.Enable(True)
            
            self.activateTracking.Enable(True)
            self.pickMaskBrowser.Enable(True)
        
            self.saveMonitorConfiguration()
        
    def saveMonitorConfiguration(self):
        '''
        '''
        
        options.SetMonitor(self.monitor_number,
                           self.thumbnail.sourceType,
                           self.thumbnail.source,
                           self.thumbnail.track,
                           self.mask_file
                           )


    def onActivateTracking(self, event):
        '''
        '''
        if self.thumbnail:
            self.thumbnail.track = event.IsChecked()
        
class panelOne(wx.Panel):
    '''
    Panel number One
    All the thumbnails
    '''
    def __init__(self, *args, **kwds):
        
        wx.Panel.__init__(self, *args, **kwds)
    
        monitor_number = options.GetOption("Monitors")
        tn_size = options.GetOption("ThumbnailSize")
       
        self.temp_source  = ''
        self.source = ''
        self.sourceType = -1
        
        self.scrollThumbnails = panelGridView(self, gridSize=monitor_number, thumbnailSize=tn_size)
        self.lowerPanel = panelConfigure(self)
        
        self.PanelOneSizer = wx.BoxSizer(wx.VERTICAL)
        self.PanelOneSizer.Add(self.scrollThumbnails, 1, wx.EXPAND, 0)
        self.PanelOneSizer.Add(self.lowerPanel, 0, wx.EXPAND, 0)
        self.SetSizer(self.PanelOneSizer)  

        
 
        

