# -*- coding: utf-8 -*-
# Continuous Clock for NVDA
# Version: 1.0
# Author: Volkan Ozdemir Software Services

import threading
import time
import wx
import gui
import addonHandler
import globalPluginHandler
import ui
import tones
import webbrowser
import scriptHandler

# Initialize translation support
addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    # Category name for Input Gestures
    scriptCategory = _("Continuous Clock")

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        # Default Values
        self.interval = 10
        self.enableTicking = True # enable_ticking -> enableTicking
        self.isRunning = True # is_running -> isRunning
        
        # Add item to NVDA Tools menu
        self.menuItem = gui.mainFrame.sysTrayIcon.menu.Append(wx.ID_ANY, _("Continuous Clock Settings..."))
        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, self.menuItem)
        
        # Start timer thread
        self._timerThread = threading.Thread(target=self._clockLoop)
        self._timerThread.daemon = True
        self._timerThread.start()

    def _clockLoop(self): # _clock_loop -> _clockLoop
        """Main loop that monitors time in the background."""
        lastMinute = -1
        while self.isRunning:
            now = time.localtime()
            # Triggered at the beginning of every minute (0th second)
            if now.tm_min != lastMinute and now.tm_sec == 0:
                lastMinute = now.tm_min
                # Announce time at determined interval
                if lastMinute % self.interval == 0:
                    self.announceTime()
                # Play 'tick' sound every minute if enabled
                if self.enableTicking:
                    tones.beep(880, 40)
            time.sleep(1)

    def announceTime(self): # announce_time -> announceTime
        """Function that announces the time."""
        currentTime = time.strftime("%H:%M")
        ui.message(_("Time: {currentTime}").format(currentTime=currentTime))

    # Assignable shortcut command via Input Gestures
    def script_announceCurrentTime(self, gesture):
        self.announceTime()
    script_announceCurrentTime.__doc__ = _("Announces the current time manually.")

    def onSettings(self, evt): # on_settings -> onSettings
        """Opens the settings dialog."""
        dlg = ClockSettingsDialog(gui.mainFrame, self)
        dlg.ShowModal()

    def terminate(self):
        """Stop loop and clean menu when add-on is disabled."""
        self.isRunning = False
        try:
            gui.mainFrame.sysTrayIcon.menu.Remove(self.menuItem)
        except:
            pass

class ClockSettingsDialog(wx.Dialog):
    """Interface for add-on settings."""
    def __init__(self, parent, plugin):
        super(ClockSettingsDialog, self).__init__(parent, title=_("Continuous Clock Settings"))
        self.plugin = plugin
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Interval Setting
        mainSizer.Add(wx.StaticText(self, label=_("Announcement interval (1-60 minutes):")), 0, wx.ALL, 5)
        self.intervalSpin = wx.SpinCtrl(self, value=str(self.plugin.interval), min=1, max=60)
        mainSizer.Add(self.intervalSpin, 0, wx.EXPAND | wx.ALL, 5)
        
        # Ticking Sound Checkbox
        self.tickCheck = wx.CheckBox(self, label=_("Play ticking sound every minute"))
        self.tickCheck.SetValue(self.plugin.enableTicking)
        mainSizer.Add(self.tickCheck, 0, wx.ALL, 5)

        # Button Row (Website and Donate)
        btnSizerRow = wx.BoxSizer(wx.HORIZONTAL)
        
        self.webBtn = wx.Button(self, label=_("Website"))
        self.webBtn.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open("https://www.volkan-ozdemir.com.tr"))
        btnSizerRow.Add(self.webBtn, 1, wx.ALL, 5)

        self.donateBtn = wx.Button(self, label=_("Donate (PayTR)"))
        self.donateBtn.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open("https://www.paytr.com/link/N2IAQKm"))
        btnSizerRow.Add(self.donateBtn, 1, wx.ALL, 5)
        
        mainSizer.Add(btnSizerRow, 0, wx.EXPAND)
        
        # Standard OK / Cancel Buttons
        buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK) # on_ok -> onOk

    def onOk(self, evt): # camelCase
        # Save settings and close
        self.plugin.interval = self.intervalSpin.GetValue()
        self.plugin.enableTicking = self.tickCheck.GetValue()
        ui.message(_("Clock settings updated."))
        self.Destroy()