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

# Çeviri desteğini başlat
addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    # Girdi hareketleri (Kısayollar) için kategori adı
    scriptCategory = _("Continuous Clock")

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        # Varsayılan Değerler
        self.interval = 10
        self.enable_ticking = True
        self.is_running = True
        
        # NVDA Araçlar menüsüne öğe ekle
        self.menu_item = gui.mainFrame.sysTrayIcon.menu.Append(wx.ID_ANY, _("Continuous Clock Settings..."))
        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.on_settings, self.menu_item)
        
        # Zamanlayıcıyı arka planda (Thread) başlat
        self._timer_thread = threading.Thread(target=self._clock_loop)
        self._timer_thread.daemon = True
        self._timer_thread.start()

    def _clock_loop(self):
        """Arka planda saniyeyi izleyen ana döngü."""
        last_minute = -1
        while self.is_running:
            now = time.localtime()
            # Her dakikanın tam başında (0. saniyede) tetiklenir
            if now.tm_min != last_minute and now.tm_sec == 0:
                last_minute = now.tm_min
                # Belirlenen periyotta saati söyle
                if last_minute % self.interval == 0:
                    self.announce_time()
                # Her dakika başında 'tık' sesi ver
                if self.enable_ticking:
                    tones.beep(880, 40)
            time.sleep(1)

    def announce_time(self):
        """Saati duyuran fonksiyon."""
        current_time = time.strftime("%H:%M")
        ui.message(_("Time: {current_time}").format(current_time=current_time))

    # Girdi Hareketleri üzerinden atanabilir kısayol komutu
    def script_announceCurrentTime(self, gesture):
        self.announce_time()
    script_announceCurrentTime.__doc__ = _("Announces the current time manually.")

    def on_settings(self, evt):
        """Ayarlar diyaloğunu açar."""
        dlg = ClockSettingsDialog(gui.mainFrame, self)
        dlg.ShowModal()

    def terminate(self):
        """Eklenti devre dışı kaldığında döngüyü durdur ve menüyü temizle."""
        self.is_running = False
        try:
            gui.mainFrame.sysTrayIcon.menu.Remove(self.menu_item)
        except:
            pass

class ClockSettingsDialog(wx.Dialog):
    """Eklenti ayarlarının yapıldığı görsel arayüz."""
    def __init__(self, parent, plugin):
        super(ClockSettingsDialog, self).__init__(parent, title=_("Continuous Clock Settings"))
        self.plugin = plugin
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Periyot Ayarı
        mainSizer.Add(wx.StaticText(self, label=_("Announcement interval (1-60 minutes):")), 0, wx.ALL, 5)
        self.intervalSpin = wx.SpinCtrl(self, value=str(self.plugin.interval), min=1, max=60)
        mainSizer.Add(self.intervalSpin, 0, wx.EXPAND | wx.ALL, 5)
        
        # Tıklama Sesi Onayı
        self.tickCheck = wx.CheckBox(self, label=_("Play ticking sound every minute"))
        self.tickCheck.SetValue(self.plugin.enable_ticking)
        mainSizer.Add(self.tickCheck, 0, wx.ALL, 5)

        # Buton Satırı (Web sitesi ve Bağış)
        btnSizerRow = wx.BoxSizer(wx.HORIZONTAL)
        
        self.webBtn = wx.Button(self, label=_("Website"))
        self.webBtn.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open("https://www.volkan-ozdemir.com.tr"))
        btnSizerRow.Add(self.webBtn, 1, wx.ALL, 5)

        self.donateBtn = wx.Button(self, label=_("Donate (PayTR)"))
        self.donateBtn.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open("https://www.paytr.com/link/N2IAQKm_"))
        btnSizerRow.Add(self.donateBtn, 1, wx.ALL, 5)
        
        mainSizer.Add(btnSizerRow, 0, wx.EXPAND)
        
        # Standart Tamam / İptal Butonları
        buttonSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    def on_ok(self, evt):
        # Ayarları kaydet ve kapat
        self.plugin.interval = self.intervalSpin.GetValue()
        self.plugin.enable_ticking = self.tickCheck.GetValue()
        ui.message(_("Clock settings updated."))
        self.Destroy()