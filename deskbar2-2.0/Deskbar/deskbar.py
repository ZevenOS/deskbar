#!/usr/bin/python
import pygtk
pygtk.require('2.0')
import os
from sys import argv
#import gtk
import gtk.glade 
import gtk.gdk
import time
import gobject
import wnck
import locale
import gettext

locale.setlocale(locale.LC_ALL, '')
for module in (gettext, gtk.glade):
    module.bindtextdomain('deskbar','i18n' )
    module.textdomain('deskbar')
    _ = gettext.gettext

pathname = os.path.dirname(argv[0])
fullpath = os.path.abspath(pathname)

screen = wnck.screen_get_default()

while gtk.events_pending():
  gtk.main_iteration()
  
class Deskbar():
      
      #  Meta-info
     __name__ = 'Deskbar'
     __version__ = '1.99'
     __author__ = 'Leszek Lesner'
     __license__ = 'GPLv3'
     __desc__ = 'A BeOS Deskbar Clone'
     global tooltip
     tooltip = gtk.Tooltips()
     
      
     def __init__(self):
       # 	Loading the MainWindow glade file and connecting
      archiglade = gtk.glade.XML(fullpath + '/deskbar.glade')
      archiglade.signal_autoconnect(self)
      self.window = archiglade.get_widget("MainWindow")
      self.lbl = archiglade.get_widget("tdate")
      self.box = archiglade.get_widget("vbox1")
      self.traybox = archiglade.get_widget("hbox1")
      self.snd = archiglade.get_widget("Sound")
      self.rdate = archiglade.get_widget("rdate")
      global toolbar
      toolbar = archiglade.get_widget("toolbar3")
      self.zcontext_menu = archiglade.get_widget("menu1")
      
      
      # 	Position the Deskbar
      width, height = self.window.get_size()
      self.window.move(gtk.gdk.screen_width() - width, 0)
      self.window.stick()

      #     Set Tooltip on Sound Button
      vol1 = os.popen("amixer sget Master | sed '/^ *Mono: /{s/^.*\[\(.*\)%\].*/\\1/;p;};d;'")
      vol1 = vol1.readline()
      vol1 = vol1.strip()
      tooltip.set_tip(self.snd, 'Volume:' + vol1)

      #    	Loading the PopUp 
      self.context_menu = archiglade.get_widget("rclick")
      tb = wnck.Tasklist(screen)
      tb.set_minimum_width(115)
      tb.set_grouping('auto-group')
      tb.set_vertical_mode(True)
      tb.show()
      self.box.pack_start(tb, False, False)

	  
      # 	Swallow in stalonetray
      os.popen("killall -9 stalonetray")
      self.astate = 0
      self.update() 

     def update(self):
         if self.astate == 0:
             global tray
             self.astate = 1
             tray = gtk.Socket()
             tray.connect("plug-added", self.onPlugAdded)
             tray.connect("plug-removed", self.onPlugRemoved)
             self.box.pack_start(tray, True, True)
             self.box.reorder_child(tray, 3)
             os.popen("stalonetray -p &")

             self.timer_id = None
             self.timer_id = gobject.timeout_add(1000, self.updTime)

      
     def onPlugAdded(self, a):
         print "Stalonetray swallowed"
         self.astate = 3
         global tray
         tray.show()
         self.update()
       

     def onPlugRemoved(self, a):
         print "Stalonetray is lost"
         self.astate = 0
         self.update()

     def checkForSize(self):
         global tray
         tray.set_size_request(115,22)
         return(True)

     #		Set Time
     def updTime(self):
         dt = list(time.localtime())
         hour = dt[3]
         minute = dt[4]
         self.lbl.set_label(time.strftime("%H:%M"))
         t2 = gtk.Tooltips()
         t2.set_tip(self.lbl, time.strftime("%d.%m.%Y")) # Setting Tooltip 
         #print(time.strftime("%H:%M:%S"))  DEBUG Output
         # Position the Deskbar rightly every 10000msec, necessary for resolution change
         width, height = self.window.get_size()
         self.window.move(gtk.gdk.screen_width() - width, 0)
         self.timer_id = gobject.timeout_add(1000, self.updTime)
         #    Try to swallow stalonetray
         root = gtk.gdk.get_default_root_window()
         prop = root.property_get("_NET_CLIENT_LIST")
         for wid in prop[2]:
            fw = gtk.gdk.window_foreign_new(wid)
            name = fw.property_get("WM_NAME")[2]
            if name == "stalonetray":
                print ("Found stalonetray with window id %02x. Swallowing window.." % (wid))
                global tray
                tray.add_id(wid)
                self.checkForSize()
                self.astate = 2
         if self.astate == 1:
            return(True)
         return(False)
     
     def on_tdatum_button_press_event(self, widget, event):
      if event.button == 1:
        print("--Datum zeigen--")
        if os.path.exists(os.getenv("HOME") + '/.deskbar_eu_on'):
         self.lbl.set_label(time.strftime("%d.%m.%y"))
        else:
         self.lbl.set_label(time.strftime("%y/%m/%d"))
        self.timer_id = gobject.timeout_add(3000, self.updTime)
      if event.button == 3:
         self.rdate.popup( None, None, None, event.button, event.time)

     def on_Tracker_clicked(self, widget):
        if os.path.exists(os.getenv("HOME") + '/.deskbar_tracker'):  
           os.popen("/bin/sh " + os.getenv("HOME") + "/.deskbar_tracker &")
        else:
           os.popen("/usr/bin/magi-kit.py filemanager &")
          
     def on_Browser_clicked(self, widget):
      if os.path.exists(os.getenv("HOME") + '/.deskbar_netp'):  
           os.popen("/bin/sh " + os.getenv("HOME") + "/.deskbar_netp &")
      else:
           os.popen("/usr/bin/magi-kit.py browser &")

     def on_Network1_button_press_event(self, widget, event):
        if event.button == 1:
            os.popen("/usr/bin/magi-kit.py network &")      

     def on_ZevenBtn_button_press_event(self, widget, event):
	 if event.button == 1: 
	    if os.path.exists(os.getenv("HOME")+ '/.deskbar_newmenu'):
               os.system("/usr/bin/Deskbar/m") 
	    elif os.path.exists(os.getenv("HOME")+ '/.deskbar_menustatic'):
               self.zcontext_menu.popup( None, None, None, event.button, event.time)
            else:
               os.system("xfdesktop -menu") 
	 if event.button == 3:
	    print "Right Click"
            self.context_menu.popup( None, None, None, event.button, event.time)
	     
     def on_ZevenBtn_enter_notify_event(self,widget, event):
        self.window.present()         

     def on_Music_clicked(self, widget):
        if os.path.exists(os.getenv("HOME") + '/.deskbar_cd'):  
           os.popen("/bin/sh " + os.getenv("HOME") + "/.deskbar_cd &")
        else:
           os.popen("/usr/bin/magi-kit.py music &")

     def on_Mail_clicked(self, widget):
       if os.path.exists(os.getenv("HOME") + '/.deskbar_bemail'):  
           os.popen("/bin/sh " + os.getenv("HOME") + "/.deskbar_bemail &")
       else:
           os.popen("/usr/bin/magi-kit.py mail &")

     def on_Terminal_clicked(self, widget):
	   if os.path.exists(os.getenv("HOME") + '/.deskbar_terminal'):  
            os.popen("/bin/sh " + os.getenv("HOME") + "/.deskbar_terminal &")
           else:
            os.popen("/usr/bin/magi-kit.py konsole &")

     def on_Notes_clicked(self, widget):
	  #print("---QuickNotes---")
	  os.system("xpad -n &")

     def on_Sound_button_press_event(self, widget,  event):
      if event.button == 1:
	    os.system("/usr/bin/magi-kit.py sound &")
     
     def on_Sound_scroll_event(self, widget, event):
      if event.direction == gtk.gdk.SCROLL_UP: 
        print "Volume UP"
        os.system("amixer set Master 3+")
        vol1 = os.popen("amixer sget Master | sed '/^ *Mono: /{s/^.*\[\(.*\)%\].*/\\1/;p;};d;'")
        vol1 = vol1.readline()
        vol1 = vol1.strip()
        tooltip.set_tip(self.snd, 'Volume:' + vol1)
      if event.direction == gtk.gdk.SCROLL_DOWN: 
        print "Volume DOWN"
        os.system("amixer set Master 3-")
        vol1 = os.popen("amixer sget Master | sed '/^ *Mono: /{s/^.*\[\(.*\)%\].*/\\1/;p;};d;'")
        vol1 = vol1.readline()
        vol1 = vol1.strip()
        tooltip.set_tip(self.snd, 'Volume:' + vol1)

      # Pop-Up Menue Aktionen 
     def on_editM_activate(self, widget):
	  os.system("alacarte &")

     def on_showCal_activate(self, widget):
	  os.system("orage &")

     def on_desktopchooser_activate(self, widget):
	  os.system("theme-manager &")

     def on_people_activate(self, widget):
	  os.system("people &")

     def on_minM_activate(self, widget):
	  print("---MinMode---")
          #os.system("deskbarv2-mini &") # old stuff why the heck did I made this stupid workaround ??
          toolbar.hide()

     def on_panelI_activate(self, widget):
	  print("---PanelIntegration---")
	  os.system("cp /usr/share/deskbar/* ~/.config/xfce4/panel &")
          os.system("killall xfce4-panel &")
          os.system("killall stalonetray &")
	  time.sleep(2)
          os.system("xfce4-panel &")

     def on_sticky_activate(self, widget):
          print("---Sticky---")
          #os.system("killall stalonetray &")
          #os.system("/usr/bin/Deskbar/deskbar-sticky.py &")
          #gtk.main_quit()
          self.window.hide()
          self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
          self.window.reshow_with_initial_size()


     def on_normal_activate(self, widget):
          print("---Normal---")
          #os.system("/usr/bin/deskbarv2 &")
          #gtk.main_quit()
          self.window.hide()
          self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
          toolbar.show()
          self.window.reshow_with_initial_size()

     
     
     def on_beenden_activate(self, widget):
          os.popen("killall stalonetray &")
	  gtk.main_quit()	


     def on_About_activate(self, widget):
          os.system("about &")


     def on_Search_activate(self, widget):
          os.system("catfish &")


     def on_Run_activate(self, widget):
          os.system("xfrun4 &")

	
     def on_Settings_activate(self, widget):
          os.system("magi2 -settings &")


     def on_Close_activate(self, widget):
          os.system("/usr/bin/xfce4-session-logout &")
          #os.system("/usr/bin/lxsession-logout  --banner=/usr/share/icons/BeOS/banner.png --side=left --prompt='ZevenOS beenden' &")
    	    

     def on_Abiword_activate(self, widget):
          os.system("magi-kit.py word &")


     def on_Gnumeric_activate(self, widget):
          os.system("magi-kit.py spreadsheet &")
	

     def on_Orage_activate(self, widget):
          os.system("orage &")


     def on_GDM_activate(self, widget):
          os.system("gksu gdmsetup &")


     def on_Screensaver_activate(self, widget):
          os.system("gnome-screensaver-preferences &")


     def on_DeskbarLinks_activate(self, widget):
          os.system("deskbar-links.py &")


     def on_PowerManager_activate(self, widget):
          os.system("gnome-power-manager &")


     def on_Seahorse_activate(self, widget):
          os.system("seahorse &")


     def on_Geany_activate(self, widget):
          os.system("geany &")


     def on_Gimp_activate(self, widget):
          os.system("magi-kit.py imageeditor &")


     def on_gpic_activate(self, widget):
          os.system("gpicview &")


     def on_Gthumb_activate(self, widget):
          os.system("magi-kit.py pictures &")


     def on_Xsane_activate(self, widget):
          os.system("xsane &")


     def on_Audacious_activate(self, widget):
          os.system("audacious &")


     def on_Audacity_activate(self, widget):
          os.system("audacity &")


     def on_Avidemux_activate(self, widget):
          os.system("avidemux &")


     def on_Brasero_activate(self, widget):
          os.system("brasero &")


     def on_Encode_activate(self, widget):
          os.system("encode &")


     def on_Recordmydesktop_activate(self, widget):
          os.system("gtk-recordMyDesktop &")


     def on_Rhythmbox_activate(self, widget):
          os.system("magi-kit.py music &")


     def on_Totem_activate(self, widget):
          os.system("magi-kit.py video &")
 

     def on_Vinagre_activate(self, widget):
          os.system("vinagre &")


     def on_Claws_activate(self, widget):
          os.system("magi-kit.py mail &")  
 

     def on_Firefox_activate(self, widget):
          os.system("magi-kit.py browser &")


     def on_Gftp_activate(self, widget):
          os.system("gftp &")
  

     def on_Giver_activate(self, widget):
          os.system("giver &")


     def on_GPPP_activate(self, widget):
          os.system("gnome-ppp &")


     def on_Liferea_activate(self, widget):
          os.system("liferea &")


     def on_Pidgin_activate(self, widget):
          os.system("magi-kit.py im &")


     def on_PyNeighborhood_activate(self, widget):
          os.system("magi-kit.py nfs &")


     def on_Transmission_activate(self, widget):
          os.system("transmission &")


     def on_Xchat_activate(self, widget):
          os.system("xchat &")


     def on_Gamerbar_activate(self, widget):
          os.system("gamerbar &")


     def on_Update_activate(self, widget):
          os.system("update-manager &")


     def on_DeviceManager_activate(self, widget):
          os.system("gnome-device-manager &")


     def on_Services_activate(self, widget):
          os.system("gksu bum &")


     def on_Usbcreator_activate(self, widget):
          os.system("usb-creator-gtk &")


     def on_Fwizard_activate(self, widget):
          os.system("fwizard &")

 
     def on_Diskmanager_activate(self, widget):
          os.system("disk-manager-root &")


     def on_Jockey_activate(self, widget):
          os.system("jockey-gtk &")


     def on_MAGI2_activate(self, widget):
          os.system("magi2 &")


     def on_Gparted_activate(self, widget):
          os.system("gksu gparted &")


     def on_Pulse_activate(self, widget):
          os.system("pulse &")


     def on_StartUp_activate(self, widget):
          os.system("gksu startupmanager &")


     def on_Synaptic_activate(self, widget):
          os.system("magi-kit.py package &")


     def on_Taskmanager_activate(self, widget):
          os.system("xfce4-taskmanager &")


     def on_Zeebar_activate(self, widget):
          os.system("zeebar -above-desk -nanim 5 -bpress &")


     def on_Appfinder_activate(self, widget):
          os.system("xfce4-appfinder &")


     def on_Mousepad_activate(self, widget):
          os.system("mousepad &")


     def on_Screenlets_activate(self, widget):
          os.system("screenlets &")


     def on_Calc_activate(self, widget):
          os.system("gcalctool &")

     def on_Terminal_activate(self, widget):
          os.system("magi-kit.py konsole &")


     def on_Xpad_activate(self, widget):
          os.system("xpad &")

	  	
if __name__ == "__main__":
	hwg = Deskbar()
	gtk.main()
