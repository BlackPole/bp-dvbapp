# Black Pole Devices Manager coded by meo.

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigSelection, NoSave
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_CURRENT_SKIN
from os import system, listdir, remove as os_remove, rename as os_rename
from enigma import eTimer


class DeliteDevicesPanel(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["key_red"] = Label(_("Mountpoints"))
		self["key_yellow"] = Label(_("Cancel"))
		self["lab1"] = Label("Wait please while scanning your devices...")
		
		self.list = []
		self["list"] = List(self.list)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"back": self.close,
			"red": self.mapSetup,
			"yellow": self.close
		})
		
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.updateList)
		self.gO()
	
	def gO(self):
# hack !
		self.activityTimer.start(1)
		
	def updateList(self):
		self.activityTimer.stop()
		self.list = [ ]
		self.conflist = [ ]
		rc = system("blkid > /tmp/blkid.log")
		
		f = open("/tmp/blkid.log",'r')
		for line in f.readlines():
			parts = line.strip().split(':')
			device = parts[0][5:-1]
			partition = parts[0][5:]
			uuid = parts[1].strip().replace('UUID="', '').replace('"', '')
			dtype = self.get_Dtype(device)
			category = dtype[0]
			png = LoadPixmap(dtype[1])
			size = self.get_Dsize(device, partition)
			model = self.get_Dmodel(device)
			mountpoint = self.get_Dpoint(uuid)
			name = "%s: %s" % (category, model)
			description = " device: %s  size: %s\n mountpoint: %s" % (parts[0], size, mountpoint)
			self.list.append((name, description, png))
			description = "%s  %s  %s" % (name, size, partition)
			self.conflist.append((description, uuid))
			
		self["list"].list = self.list
		self["lab1"].hide()
		os_remove("/tmp/blkid.log")
		
		
	def get_Dpoint(self, uuid):
		point = "NOT MAPPED"
		f = open("/etc/fstab",'r')
		for line in f.readlines():
			if line.find(uuid) != -1:
				parts = line.strip().split()
				point = parts[1]
				break
		f.close()
		return point
		
	def get_Dmodel(self, device):
		model = "Generic"
		filename = "/sys/block/%s/device/vendor" % (device)
		if fileExists(filename):
			vendor = file(filename).read().strip()
			filename = "/sys/block/%s/device/model" % (device)
			mod = file(filename).read().strip()
			model = "%s %s" % (vendor, mod)
		return model
		
	def get_Dsize(self, device, partition):
		size = "0"
		filename = "/sys/block/%s/%s/size" % (device, partition)
		if fileExists(filename):
			size = int(file(filename).read().strip())
			cap = size / 1000 * 512 / 1000
			size = "%d.%03d GB" % (cap/1000, cap%1000)
		return size
		
		
	def get_Dtype(self, device):
		pixpath = resolveFilename(SCOPE_CURRENT_SKIN, "")
		if pixpath == "/usr/share/enigma2/":
			pixpath = "/usr/share/enigma2/skin_default/"
		
		name = "USB"
		pix = pixpath + "icons/dev_usb.png"
		filename = "/sys/block/%s/removable" % (device)
		if fileExists(filename):
			if file(filename).read().strip() == "0":
				name = "HARD DISK"
				pix = pixpath + "icons/dev_hdd.png"
				
		return name, pix
		
		
	def mapSetup(self):
		self.session.openWithCallback(self.close, DeliteSetupDevicePanelConf, self.conflist)
						

class DeliteSetupDevicePanelConf(Screen, ConfigListScreen):
	def __init__(self, session, devices):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Save"))
		self["key_green"] = Label(_("Cancel"))
		self["Linconn"] = Label("Wait please while scanning your box devices...")
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.savePoints,
			"green": self.close,
			"back": self.close

		})
		
		self.devices = devices
		self.updateList()
	
	
	def updateList(self):
		self.list = []
		for device in self.devices:
			item = NoSave(ConfigSelection(default = "Not mapped", choices = self.get_Choices()))
			item.value = self.get_currentPoint(device[1])
			res = getConfigListEntry(device[0], item, device[1])
			self.list.append(res)
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		self["Linconn"].hide()



	def get_currentPoint(self, uuid):
		point = "Not mapped"
		f = open("/etc/fstab",'r')
		for line in f.readlines():
			if line.find(uuid) != -1:
				parts = line.strip().split()
				point = parts[1].strip()
				break
		f.close()
		return point

	def get_Choices(self):
		choices = [("Not mapped", "Not mapped")]
		folders = listdir("/media")
		for f in folders:
			if f == "net":
				continue
			c = "/media/" + f
			choices.append((c,c))
		return choices
			
		

	def savePoints(self):
		f = open("/etc/fstab",'r')
		out = open("/etc/fstab.tmp", "w")
		for line in f.readlines():
			if line.find("UUID") != -1 or len(line) < 6:
				continue
			out.write(line)
		for x in self["config"].list:
			if x[1].value != "Not mapped":
				line = "UUID=%s    %s    auto   defaults    0  0\n" % (x[2], x[1].value)
				out.write(line)

		out.write("\n")
		f.close()
		out.close()
		os_rename("/etc/fstab.tmp", "/etc/fstab")
		message = "Devices changes need a system restart to take effects.\nRestart your Box now?"
		self.session.openWithCallback(self.restBo, MessageBox, message, MessageBox.TYPE_YESNO)
			
	def restBo(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)
		else:
			self.close()
	
	

