from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.config import config, ConfigText, configfile
from Components.Sources.List import List
from Components.Label import Label
from Components.PluginComponent import plugins
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE, fileExists, pathExists, createDir
from Tools.LoadPixmap import LoadPixmap
from Plugins.Plugin import PluginDescriptor
from Plugins.SystemPlugins.SoftwareManager.plugin import PacketManager, PluginManager, UpdatePlugin
from os import system, listdir, chdir, getcwd, remove as os_remove
from enigma import eDVBDB

config.misc.fast_plugin_button = ConfigText(default="")

class DeliteGreenPanel(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		self["list"] = List(self.list)
		self.updateList()
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.runPlug,
			"back": self.close,
			"red": self.keyRed,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.keyBlue
		}, -1)
			
	def runPlug(self):
		mysel = self["list"].getCurrent()
		if mysel:
			plugin = mysel[3]
			plugin(session=self.session)
		
	def updateList(self):
		self.list = [ ]
		self.pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
		for plugin in self.pluginlist:
			if plugin.icon is None:
				png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/icons/plugin.png"))
			else:
				png = plugin.icon
			res = (plugin.name, plugin.description, png, plugin)
			self.list.append(res)
		
		self["list"].list = self.list	
	
	def keyYellow(self):
		self.session.open(DeliteAddons)
	
	def keyRed(self):
		self.session.open(DeliteSetupFp)
		
	def keyGreen(self):
		runplug = None
		for plugin in self.list:
			if  plugin[3].name == config.misc.fast_plugin_button.value:
				runplug = plugin[3]
				break
		
		if runplug is not None:
			runplug(session=self.session)
		else:
			self.session.open(MessageBox, "Fast Plugin not found. You have to setup Fast Plugin before to use this shortcut.", MessageBox.TYPE_INFO)

	def keyBlue(self):
		self.session.open(DeliteScript)

class DeliteSetupFp(Screen):
	skin = """
	<screen position="160,115" size="390,370" title="Black Hole Fast Plugin Setup">
		<widget source="list" render="Listbox" position="10,10" size="370,300" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
		<ePixmap pixmap="skin_default/buttons/red.png" position="115,320" size="140,40" alphatest="on" />
		<widget name="key_red" position="115,320" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["key_red"] = Label(_("Set Favourite"))
		self.list = []
		self["list"] = List(self.list)
		self.updateList()
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.save,
			"back": self.close,
			"red": self.save
		}, -1)
			
	def updateList(self):
		self.list = [ ]
		self.pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
		for plugin in self.pluginlist:
			if plugin.icon is None:
				png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/icons/plugin.png"))
			else:
				png = plugin.icon
			res = (plugin.name, plugin.description, png)
			self.list.append(res)
		
		self["list"].list = self.list
		
	def save(self):
		mysel = self["list"].getCurrent()
		if mysel:
			message = "Fast plugin set to: " + mysel[0] + "\nKey: 2x Green"
			mybox = self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO)
			mybox.setTitle(_("Configuration Saved"))
			config.misc.fast_plugin_button.value = mysel[0]
			config.misc.fast_plugin_button.save()
			configfile.save()

class DeliteAddons(Screen):
	skin = """
	<screen position="160,115" size="390,330" title="Black Pole E2 Addons Manager">
		<widget source="list" render="Listbox" position="10,16" size="370,300" scrollbarMode="showOnDemand" >
			<convert type="TemplatedMultiContent">
                	{"template": [
                    	MultiContentEntryText(pos = (50, 1), size = (320, 36), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),
                 	MultiContentEntryPixmapAlphaTest(pos = (4, 2), size = (36, 36), png = 1),
                    	],
                    	"fonts": [gFont("Regular", 22)],
                    	"itemHeight": 36
                	}
            		</convert>
		</widget>
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)

		self.list = []
		self["list"] = List(self.list)
		self.updateList()
		
		if (not pathExists("/usr/uninstall")):
			createDir("/usr/uninstall")
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close,

		})
		
	def updateList(self):
		self.list = [ ]
		mypath = resolveFilename(SCOPE_CURRENT_SKIN, "")
		if mypath == "/usr/share/enigma2/":
			mypath = "/usr/share/enigma2/skin_default/"
		
		mypixmap = mypath + "icons/addons_manager.png"
		png = LoadPixmap(mypixmap)
		name = "Online Feeds Extensions"
		idx = 0
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/addons_manager.png"
		png = LoadPixmap(mypixmap)
		name = "Online Feeds all Packages"
		idx = 1
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/addons_manager.png"
		png = LoadPixmap(mypixmap)
		name = "Online Black Pole image update"
		idx = 2
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/nabpackpanel.png"
		png = LoadPixmap(mypixmap)
		name = "Manual Install Bh packges"
		idx = 3
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/ipkpackpanel.png"
		png = LoadPixmap(mypixmap)
		name = "Manual Install Ipk packges"
		idx = 4
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/uninstpanel.png"
		png = LoadPixmap(mypixmap)
		name = "Addons Uninstall Panel"
		idx = 5
		res = (name, png, idx)
		self.list.append(res)
		
		self["list"].list = self.list
		
	def KeyOk(self):
		
		self.sel = self["list"].getCurrent()
		if self.sel:
			self.sel = self.sel[2]
			
		if self.sel == 0:
			self.session.open(PluginManager, "/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager")
		elif self.sel == 1:	
			self.session.open(PacketManager, "/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager")
		elif self.sel == 2:
			self.session.openWithCallback(self.runUpgrade, MessageBox, _("Do you want to update your Black Pole image?")+"\n"+_("\nAfter pressing OK, please wait!"))
		elif self.sel == 3:
			self.checkPanel()
		elif self.sel == 4:
			self.checkPanel2()
		elif self.sel == 5:
			self.session.open(Nab_uninstPanel)
	
	
	def checkPanel(self):
		check = 0
		pkgs = listdir("/tmp")
		for fil in pkgs:
			if fil.find('.tgz') != -1:
				check = 1
		if check == 1:
			self.session.open(Nab_downPanel)
		else:
			mybox = self.session.open(MessageBox, "Nothing to install.\nYou have to Upload a bh.tgz package in the /tmp directory before to install Addons", MessageBox.TYPE_INFO)
			mybox.setTitle(_("Info"))
			
	def checkPanel2(self):
		check = 0
		pkgs = listdir("/tmp")
		for fil in pkgs:
			if fil.find('.ipk') != -1:
				check = 1
		if check == 1:
			self.session.open(Nab_downPanelIPK)
		else:
			mybox = self.session.open(MessageBox, "Nothing to install.\nYou have to Upload an ipk package in the /tmp directory before to install Addons", MessageBox.TYPE_INFO)
			mybox.setTitle(_("Info"))
			
			
	def runUpgrade(self, result):
		if result:
			self.session.open(UpdatePlugin, "/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager")

class Nab_downPanel(Screen):
	skin = """
	<screen position="80,95" size="560,405" title="Black Pole E2 Manual Install BH Packages">
		<widget source="list" render="Listbox" position="10,16" size="540,380" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)

		self.flist = []
		idx = 0
		pkgs = listdir("/tmp")
		for fil in pkgs:
			if fil.find('.tgz') != -1:
				res = (fil, idx)
				self.flist.append(res)
				idx = idx + 1
		
		self["list"] = List(self.flist)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close

		})

	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		if self.sel:
			self.sel = self.sel[0]
			message = "Do you want to install the Addon:\n " + self.sel + " ?"
			ybox = self.session.openWithCallback(self.installadd2, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle("Installation Confirm")

	def installadd2(self, answer):
		if answer is True:
			dest = "/tmp/" + self.sel
			mydir = getcwd()
			chdir("/")
			cmd = "tar -xzf " + dest
			rc = system(cmd)
			chdir(mydir)
			cmd = "rm -f " + dest
			rc = system(cmd)
			if fileExists("/usr/sbin/nab_e2_restart.sh"):
				rc = system("rm -f /usr/sbin/nab_e2_restart.sh")
				mybox = self.session.openWithCallback(self.hrestEn, MessageBox, "Gui will be now hard restarted to complete package installation.\nPress ok to continue", MessageBox.TYPE_INFO)
				mybox.setTitle("Info")
			else:
				mybox = self.session.open(MessageBox, "Addon Succesfully Installed.", MessageBox.TYPE_INFO)
				mybox.setTitle("Info")
				self.close()

	def hrestEn(self, answer):
		self.eDVBDB = eDVBDB.getInstance()
		self.eDVBDB.reloadServicelist()
		self.eDVBDB.reloadBouquets()
		self.session.open(TryQuitMainloop, 3)


class Nab_downPanelIPK(Screen):
	skin = """
	<screen position="80,95" size="560,405" title="Black Pole E2 Manual Install Ipk Packages">
		<widget source="list" render="Listbox" position="10,10" size="540,290" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
		<widget name="warntext" position="0,305" size="560,100" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)			

		self.flist = []
		idx = 0
		pkgs = listdir("/tmp")
		for fil in pkgs:
			if fil.find('.ipk') != -1:
				res = (fil, idx)
				self.flist.append(res)
				idx = idx + 1
		
		self["warntext"] = Label("Here you can install any kind of ipk packages.")
		self["list"] = List(self.flist)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close

		})

	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		if self.sel:
			self.sel = self.sel[0]
			message = "Do you want to install the Addon:\n " + self.sel + " ?"
			ybox = self.session.openWithCallback(self.installadd2, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle("Installation Confirm")

	def installadd2(self, answer):
		if answer is True:
			dest = "/tmp/" + self.sel
			mydir = getcwd()
			chdir("/")
			cmd = "opkg install " + dest
			cmd2 = "rm -f " + dest
			self.session.open(Console, title="Ipk Package Installation", cmdlist=[cmd, cmd2])
			chdir(mydir)

class Nab_uninstPanel(Screen):
	skin = """
	<screen position="80,95" size="560,405" title="Black Pole E2 Uninstall Panel">
		<widget source="list" render="Listbox" position="10,16" size="540,380" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)			

		self.flist = []
		idx = 0
		pkgs = listdir("/usr/uninstall")
		for fil in pkgs:
			if fil.find('.nab') != -1 or fil.find('.del') != -1:
				res = (fil, idx)
				self.flist.append(res)
				idx = idx + 1
		
		self["list"] = List(self.flist)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close

		})
		
	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		if self.sel:
			self.sel = self.sel[0]
			message = "Are you sure you want to Remove Package:\n " + self.sel + "?"
			ybox = self.session.openWithCallback(self.uninstPack, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle("Uninstall Confirmation")
		
	
	def uninstPack(self, answer):
		if answer is True:
			orig = "/usr/uninstall/" + self.sel
			cmd = "sh " + orig
			rc = system(cmd)
			mybox = self.session.open(MessageBox, "Addon Succesfully Removed.", MessageBox.TYPE_INFO)
			mybox.setTitle("Info")
			self.close()

class DeliteScript(Screen):
	skin = """
	<screen position="80,100" size="560,410" title="Black Hole Script Panel">
		<widget source="list" render="Listbox" position="10,10" size="540,300" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
		<widget name="statuslab" position="10,320" size="540,30" font="Regular;16" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="210,360" size="140,40" alphatest="on" />
		<widget name="key_red" position="210,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["statuslab"] = Label("N/A")
		self["key_red"] = Label("Execute")
		self.mlist = []
		self.populateSL()
		self["list"] = List(self.mlist)
		self["list"].onSelectionChanged.append(self.schanged)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.myGo,
			"back": self.close,
			"red": self.myGo
		})
		self.onLayoutFinish.append(self.refr_sel)
		
	def refr_sel(self):
		self["list"].index = 1
		self["list"].index = 0
		
	def populateSL(self):
		myscripts = listdir("/usr/script")
		for fil in myscripts:
			if fil.find('.sh') != -1:
				fil2 = fil[:-3]
				desc = "N/A"
				f = open("/usr/script/" + fil,'r')
				for line in f.readlines():
					if line.find('#DESCRIPTION=') != -1:
						line = line.strip()
						desc = line[13:]
				f.close()
				res = (fil2, desc)
				self.mlist.append(res)			

	def schanged(self):
		mysel = self["list"].getCurrent()
		if mysel:
			mytext = " " + mysel[1]
			self["statuslab"].setText(mytext)

			
	def myGo(self):
		mysel = self["list"].getCurrent()
		if mysel:
			mysel = mysel[0]
			mysel2 = "/usr/script/" + mysel + ".sh"
			mytitle = "Black Hole E2 Script: " + mysel
			self.session.open(Console, title=mytitle, cmdlist=[mysel2])

class DeliteGp:
	def __init__(self):
		self["DeliteGp"] = ActionMap( [ "InfobarSubserviceSelectionActions" ],
			{
				"DeliteGpshow": (self.showDeliteGp),
			})

	def showDeliteGp(self):
		self.session.openWithCallback(self.callNabAction, DeliteGreenPanel)

	def callNabAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)