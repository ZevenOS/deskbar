#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
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
import HTMLParser
import re
import fileinput
import pango
# dynamic menu 
import gmenu, sys, gtk, pygtk
from xml.sax.saxutils import escape

locale.setlocale(locale.LC_ALL, '')
for module in (gettext, gtk.glade):
    module.bindtextdomain('deskbar','i18n' )
    module.textdomain('deskbar')
    _ = gettext.gettext

pathname = os.path.dirname(argv[0])
fullpath = os.path.abspath(pathname)

screen = wnck.screen_get_default()
# We do not support "javascript:" URL bookmarks.
global_unsupported_url_pattern = re.compile("^javascript:", re.IGNORECASE)
# We mark with an icon those URL bookmarks that contain a "%s"
global_query_url_pattern = re.compile("%s")

while gtk.events_pending():
  gtk.main_iteration()
  
# Encapsulated code to read the Mozilla/Firefox bookmarks file format.
# This class is based on GPL code taken from bookmarks-applet.py
# as found in gnome-python version 1.4.4 (author unknown).
class MozillaFormatBookmarksParser(HTMLParser.HTMLParser):
	def __init__(self, bookmarks_file_name):
		HTMLParser.HTMLParser.__init__(self)
		self.chars = ""
		self.root_menu = []
		self.tree_stack = []
		self.item_title = None
		self.item_href = None
		
		if bookmarks_file_name and os.path.exists(bookmarks_file_name):
			self.feed(file(bookmarks_file_name, 'r').read())

	def handle_starttag(self, tag, attrs):
		tag = tag.lower()
		if tag == "a":
			self.chars = ""
			for tag, value in attrs:
				if tag.lower() == 'href':
					self.item_href = value
		elif tag == "dl":
			new_menu = []
			self.tree_stack.append(new_menu)
			if len(self.tree_stack) > 1:
				self.tree_stack[-2].append((self.item_title, new_menu))
			else:
				self.root_menu = new_menu
		elif tag == "h1" or tag == "h3":
			self.chars = ""
		elif tag == "hr":
			self.tree_stack[-1].append((None, None))

	def handle_endtag(self, tag):
		tag = tag.lower()
		if tag == "a":
			self.tree_stack[-1].append((self.chars, self.item_href))
		elif tag == "dl":
			del self.tree_stack[-1]
		elif tag == "h1" or tag == "h3":
			self.item_title = self.chars

	def handle_data(self, chars):
		self.chars = self.chars + chars
# end class MozillaFormatBookmarksParser
  
class Deskbar():
      
      #  Meta-info
     __name__ = 'Deskbar'
     __version__ = '1.99'
     __author__ = 'Leszek Lesner'
     __license__ = 'GPLv3'
     __desc__ = 'A BeOS Deskbar Clone'
     global tooltip
     tooltip = gtk.Tooltips()
     global m
     m = gtk.Menu()
     global d
     d = {}
     
     
      
     def __init__(self):
       # 	Loading the MainWindow glade file and connecting
      archiglade = gtk.glade.XML(fullpath + '/deskbar.glade')
      archiglade.signal_autoconnect(self)
      self.window = archiglade.get_widget("MainWindow")
      self.lbl = archiglade.get_widget("tdate")
      self.box = archiglade.get_widget("vbox1")
      self.snd = archiglade.get_widget("Sound")
      self.rdate = archiglade.get_widget("rdate")
      self.soundmenu = archiglade.get_widget("soundmenu")
      global toolbar
      toolbar = archiglade.get_widget("hbox2")
      self.zcontext_menu = archiglade.get_widget("menu1")
      self.ZevenBtn = archiglade.get_widget("ZevenBtn")
      m.attach_to_widget(self.ZevenBtn, dynamic_detach)
      refresh_dynamic_menu()
      
      
      # 	Position the Deskbar
      if os.path.exists(os.getenv("HOME") + '/.deskbar_position_left'):
          self.window.move(0, 0)
      else:
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
      self.timer_id = None
      self.timer_id = gobject.timeout_add(1000, self.updTime)
     
      
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
         if os.path.exists(os.getenv("HOME") + '/.deskbar_position_left'):
             self.window.move(0, 0)
         else:
             width, height = self.window.get_size()
             self.window.move(gtk.gdk.screen_width() - width, 0)
         self.timer_id = gobject.timeout_add(1000, self.updTime)
     
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

     def filemanageropen(self,widget, path):
        os.popen("$(magi-kit.py --show filemanager) " + path + " &")

     def setquicklaunchlink(self, widget, module):
        os.popen("magi2 -setlink " + module)

     def on_Tracker_button_press_event(self, widget, event):
        if event.button == 1:
           print "Left Click"
           if os.path.exists(os.getenv("HOME") + '/.deskbar_tracker'):  
              os.popen("/bin/sh " + os.getenv("HOME") + "/.deskbar_tracker &")
           else:
              os.popen("$(magi-kit.py --show filemanager) " + os.getenv("HOME") + " &")
        elif event.button == 3:
           print "Right Click"
           bookmarkmenu = gtk.Menu()
           BOOKMARKS = '~/.gtk-bookmarks'
           items = [('~', 'Home')]
           menuitem = gtk.MenuItem(_("Home")) 
           menuitem.connect("activate", self.filemanageropen, "~")
           bookmarkmenu.append(menuitem)
           bookmarkmenu.show_all()
           with open(os.path.expanduser(BOOKMARKS)) as bookmarkfile:
               for line in bookmarkfile:
                   path, label = line.strip().partition(' ')[::2]
                   if not label:
                       label = os.path.basename(os.path.normpath(path))
                   item = (path,label)
                   items.extend(item)
                   menuitem = gtk.MenuItem(label)
                   menuitem.connect("activate", self.filemanageropen, path)
                   bookmarkmenu.append(menuitem)
                   bookmarkmenu.show_all()
               separator = gtk.SeparatorMenuItem()
               bookmarkmenu.append(separator)
               menuitem = gtk.MenuItem(_("Edit Link"))
               menuitem.connect("activate", self.setquicklaunchlink, "filemanager")
               bookmarkmenu.append(menuitem)
               bookmarkmenu.show_all()
               bookmarkmenu.popup( None, None, None, event.button, event.time)

     def on_Browser_button_press_event(self, widget, event):
        if event.button == 1:
            if os.path.exists(os.getenv("HOME") + '/.deskbar_netp'):  
               os.popen("/bin/sh " + os.getenv("HOME") + "/.deskbar_netp &")
            else:
               os.popen("/usr/bin/magi-kit.py browser &")
        elif event.button == 3:
            (bookmarks_tree, bookmarks_editor_text, bookmarks_editor_cmd, favicons) = get_bookmarks()
            print "Browser right click" # Debug
            bookmark_menu = gtk.Menu()
            bookmark_tooltips = gtk.Tooltips()
            bookmark_tooltips.enable()
            fill_menu(bookmark_menu, bookmark_tooltips, bookmarks_tree, favicons)
            separator = gtk.SeparatorMenuItem()
            bookmark_menu.append(separator)
            menuitem = gtk.MenuItem(_("Edit Link"))
            menuitem.connect("activate", self.setquicklaunchlink, "browser")
            bookmark_menu.append(menuitem)
            bookmark_menu.show_all()
            bookmark_menu.popup( None, None, None, event.button, event.time)
            

     def on_Network1_button_press_event(self, widget, event):
        if event.button == 1:
            os.popen("/usr/bin/magi-kit.py network &")      

     def on_ZevenBtn_button_press_event(self, widget, event):
	 if event.button == 1: 
	    if os.path.exists(os.getenv("HOME")+ '/.deskbar_newmenu'):
               #os.system("/usr/bin/Deskbar/m")
               show_dynamic_menu(m) 
	    elif os.path.exists(os.getenv("HOME")+ '/.deskbar_menustatic'):
               self.zcontext_menu.popup( None, None, None, event.button, event.time)
            else:
               os.system("xfdesktop -menu") 
	 if event.button == 3:
	    #print "Right Click"
            self.context_menu.popup( None, None, None, event.button, event.time)
	     
     def on_ZevenBtn_enter_notify_event(self,widget, event):
        self.window.present()         

     def musicplayer(self, widget, cmd):
        os.popen("$(magi-kit.py --show music) --"+ cmd + " &") 

     def on_Music_button_press_event(self, widget, event):
        if event.button == 1:
            if os.path.exists(os.getenv("HOME") + '/.deskbar_cd'):  
               os.popen("/bin/sh " + os.getenv("HOME") + "/.deskbar_cd &")
            else:
               os.popen("/usr/bin/magi-kit.py music &")
        elif event.button == 3:
            #print "Right Click" 
            musicmenu = gtk.Menu()
            menuitem = gtk.MenuItem(_("Play/Pause"))
            menuitem.connect("activate", self.musicplayer, "pause")
            musicmenu.append(menuitem)
            menuitem = gtk.MenuItem(_("Stop"))
            menuitem.connect("activate", self.musicplayer, "stop")
            musicmenu.append(menuitem)
            menuitem = gtk.MenuItem(_("Prev"))
            menuitem.connect("activate", self.musicplayer, "prev")
            musicmenu.append(menuitem)
            menuitem = gtk.MenuItem(_("Next"))
            menuitem.connect("activate", self.musicplayer, "next")
            musicmenu.append(menuitem)
            menuitem = gtk.MenuItem(_("Randomize"))
            menuitem.connect("activate", self.musicplayer, "random")
            musicmenu.append(menuitem)
            separator = gtk.SeparatorMenuItem()
            musicmenu.append(separator)
            menuitem = gtk.MenuItem(_("Edit Link"))
            menuitem.connect("activate", self.setquicklaunchlink, "music")
            musicmenu.append(menuitem)
            musicmenu.show_all()
            musicmenu.popup( None, None, None, event.button, event.time)
            

     def newmail(self, widget):
          os.popen("$(magi-kit.py --show mail) --compose &")

     def on_Mail_button_press_event(self, widget, event):
       if event.button == 1:
           if os.path.exists(os.getenv("HOME") + '/.deskbar_bemail'):  
              os.popen("/bin/sh " + os.getenv("HOME") + "/.deskbar_bemail &")
           else:
              os.popen("/usr/bin/magi-kit.py mail &")
       elif event.button == 3:
           print "Right Click" # Debug
           mailmenu = gtk.Menu()
           menuitem = gtk.MenuItem(_("New mail"))
           menuitem.connect("activate", self.newmail)
           mailmenu.append(menuitem)
           separator = gtk.SeparatorMenuItem()
           mailmenu.append(separator)
           menuitem = gtk.MenuItem(_("Edit Link"))
           menuitem.connect("activate", self.setquicklaunchlink, "mail")
           mailmenu.append(menuitem)
           mailmenu.show_all()
           mailmenu.popup( None, None, None, event.button, event.time)
           

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
      elif event.button == 3:
	    self.soundmenu.popup( None, None, None, event.button, event.time)
     
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
          try:
              toolbar.show()
          except:
              print "Toolbar was not hidden so do not show"
          self.window.reshow_with_initial_size()

     def on_setTime_activate(self, widget):
          os.popen("magi-kit.py time &")
     
     def on_muteSound_toggled(self,widget):
          os.popen("amixer set Master toggle &")
     
     def on_beenden_activate(self, widget):
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

# begin browser-specific file location methods
def get_firefox_bookmarks_file_name():
 try:
     firefox_dir = os.path.expanduser("~/.mozilla/firefox/")
     path_pattern = re.compile("^Path=(.*)")
     for line in fileinput.input(firefox_dir + "profiles.ini"):
	 if line == "":
	    break
	 match_obj = path_pattern.search(line)
	 if match_obj:
	    if match_obj.group(1).startswith("/"):
		return match_obj.group(1) + "/bookmarks.html"
	    else:
		return firefox_dir + match_obj.group(1) + "/bookmarks.html"
 finally:
     fileinput.close()
 return None

def get_http_handler():
 return os.popen("magi-kit.py --show browser").read()

def get_bookmarks():
 hh = get_http_handler()
 if hh.find("firefox") != -1:
     return (MozillaFormatBookmarksParser(get_firefox_bookmarks_file_name()).root_menu,\
     "Manage Bookmarks...", None, None)
 else:
     return ([], None, None, None)

def fill_menu(menu, tooltips, contents, favicons):
 for (name, href_or_folder) in contents:
     if name == None:
	 menu_item = gtk.SeparatorMenuItem()
     else:
	 menu_item = gtk.ImageMenuItem(name)
	 menu_item.get_child().set_ellipsize(pango.ELLIPSIZE_END)
	 menu_item.get_child().set_max_width_chars(32)
	 if href_or_folder.__class__ == [].__class__:
	     folder = href_or_folder
	     sub_menu = gtk.Menu()
	     menu_item.set_submenu(sub_menu)
	     fill_menu(sub_menu, tooltips, folder, favicons)
	 else:
	     href = href_or_folder
	     tooltips.set_tip(menu_item, href)
	     if global_unsupported_url_pattern.search(href):
		 menu_item.set_sensitive(False)
	     else:
		 menu_item.connect("activate", url_show, (name, href))
     menu.append(menu_item)

def url_show(menu_item, (name,href)):
 if global_query_url_pattern.search(href):
     href = query_dialog(name, href)

 if href <> None:
     os.system("$(magi-kit.py --show browser) " + "\"" + href + "\"" + " &")
     
def menuitem_response(self,entry_name):
	cmd = d[entry_name]
	os.popen(cmd + " &")
	print "os.popen(%s)" % cmd
	#gtk.main_quit()

def menuitembuildin_response(self,cmd):
	os.popen(cmd + " &")
	#gtk.main_quit()

def walk_menu(entry):
	if entry.get_type() == gmenu.TYPE_DIRECTORY:
		print 'id="%s" label="%s" icon="%s"'  % (entry.menu_id, entry.get_name(), entry.get_icon())
		submenu = gtk.Menu()
		folder = gtk.ImageMenuItem(entry.get_name())
		try:
			j = gtk.Image()
			j.set_from_icon_name(entry.get_icon(), gtk.ICON_SIZE_MENU)
			folder.set_image(j)
		except:
			try:
				k = gtk.gdk.pixbuf_new_from_file_at_size(entry.get_icon(), 16, 16)
				j = gtk.Image()
				j.set_from_pixbuf(k)
				folder.set_image(j)
			except:	
				print "Fehler Menu Icon von Dateiname"
			print "Fehler Menu Icon"
		m.append(folder)
		map(walk_menu, entry.get_contents())
		folder.set_submenu(submenu)
	elif entry.get_type() == gmenu.TYPE_ENTRY and not entry.is_excluded:
		desktopfile = gtk.ImageMenuItem(None)
		print '	item label="%s" icon="%s"' % (entry.get_name(), entry.get_icon())
		command = re.sub(' [^ ]*%[fFuUdDnNickvm]', '', entry.get_exec())
		if entry.launch_in_terminal:
			command = 'xterm -title "%s" -e %s' %  (entry.get_name(), command)
		print '	command="%s"' % command
		d[entry.get_name()] = command
       		desktopfile = gtk.ImageMenuItem(entry.get_name())
		try:
			i = gtk.Image()
			if str(entry.get_icon()).startswith('/'):
				#print "Hier ist ein Icon, dass nicht aus dem Icon-Theme gelesen wird" ## DEBUG ##
				k = gtk.gdk.pixbuf_new_from_file_at_size(entry.get_icon(), 16, 16)
				i.set_from_pixbuf(k)
			elif str(entry.get_icon()).endswith('.png') or str(entry.get_icon()).endswith('.xpm'):
				try:
					k = gtk.gdk.pixbuf_new_from_file_at_size("/usr/share/pixmaps/" + entry.get_icon(), 16, 16)
					i.set_from_pixbuf(k)
				except:
					ico=str(entry.get_icon()).rstrip(".png")
					i.set_from_icon_name(ico, gtk.ICON_SIZE_MENU)
			else:
				i.set_from_icon_name(entry.get_icon(), gtk.ICON_SIZE_MENU)
			desktopfile.set_image(i)
		except:
			print "Fehler Icon Item: ", sys.exc_info()
       		desktopfile.connect("activate", menuitem_response,entry.get_name())
		global submenu
       		submenu.append(desktopfile)
       	
def refresh_dynamic_menu():
	menu = 'applications.menu'
	#m = gtk.Menu()
	folder = gtk.MenuItem(None)
	global submenu   # Fixes crash on Natty
	submenu = gtk.Menu()
	map(walk_menu, gmenu.lookup_tree(menu).root.get_contents())
	
	# create menu
	item = gtk.ImageMenuItem(gtk.STOCK_DIALOG_INFO)
	item.get_children()[0].set_label("About")
	item.connect("activate",menuitembuildin_response,"about")
	m.insert(item,0)
	item = gtk.ImageMenuItem(gtk.STOCK_FIND)
	item.connect("activate",menuitembuildin_response,"/usr/bin/magi-kit.py search")
	m.insert(item,1)
	item = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
	item.connect("activate",menuitembuildin_response,"xfrun4")
	m.insert(item,2)
	item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
	item.connect("activate",menuitembuildin_response,"magi2 -settings")
	m.insert(item,3)
	item=gtk.SeparatorMenuItem()
	m.insert(item,4)
	item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
	item.connect("activate", menuitembuildin_response,"xfce4-session-logout")
	m.insert(item,5)
	item=gtk.SeparatorMenuItem()
	m.insert(item,6)
	
	#m.connect("deactivate", menuitem_quit)
	
	m.show_all()

def show_dynamic_menu(m):
	m.popup(None,None,None,1,0)
	
def dynamic_detach():
	refresh_dynamic_menu()       	
	
if __name__ == "__main__":
	hwg = Deskbar()
	gtk.main()
