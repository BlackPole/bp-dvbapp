# Black Pole usb format utility coded by meo.

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists
from os import system, listdir


class Bp_UsbFormat(Screen):
	skin = """
	<screen position="center,center" size="580,350" title="Black Pole Usb Format Wizard">
		<widget name="lab1" position="10,10" size="560,280" font="Regular;20" valign="top" transparent="1"/>
		<ePixmap pixmap="skin_default/buttons/red.png" position="100,300" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="340,300" size="140,40" alphatest="on" />
		<widget name="key_red" position="100,300" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="340,300" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
	</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		
		msg = """This wizard will help you to format Usb mass storages for Linux.
Please be sure that your usb drive is not connected to your Vu+ box before to continue.
If your usb drive is connected and mounted you have to poweroff your box, remove the usb device and reboot.
Push red button to continue when you are ready and your usb is disconnected.
"""
		self["key_red"] = Label(_("Continue ->"))
		self["key_green"] = Label(_("Cancel"))
		self["lab1"] = Label(msg)

		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"back": self.close,
			"red": self.step_Bump,
			"green": self.close
		})
		self.step = 1
		self.devices = []
		self.device = None
	
	
	def stepOne(self):
		msg = """Connect your usb storage to your Vu+ box
Press red button to continue when ready.
"""
		self.devices = self.get_Devicelist()
		self["lab1"].setText(msg)
		self.step = 2
		
	def stepTwo(self):
		msg = """The wizard will now try to identify your connected usb storage.
Press red button to continue.
"""				
		self["lab1"].setText(msg)
		self.step = 3
	
	def stepThree(self):
		newdevices = self.get_Devicelist()
		for d in newdevices:
			if d not in self.devices:
				self.device = d
		if self.device is None:
			self.wizClose("Sorry, no new usb storage detected.\nBe sure to follow wizard instructions.")
		else:
			msg = self.get_Deviceinfo(self.device)
			msg +="\nWarning: all the data will be lost.\nAre you sure you want to format this device?\n"
			self["lab1"].setText(msg)
			self.step = 4
			
	def stepFour(self):
		device = "/dev/" + self.device
		partition = device + "1"
		cmd = "umount %s" % (partition)
		rc = system(cmd)
		cmd = "umount %s" % (device)
		rc = system(cmd)
		if fileExists(partition):
			self.do_Format()
		else:
			self.do_Part()
					

	def do_Part(self):
		device = "/dev/%s" % (self.device)
		cmd = "echo -e 'Partitioning: %s \n\n'" % (device)
		cmd2 = 'printf "0,\n;\n;\n;\ny\n" | sfdisk -f %s' % (device)
		self.session.open(Console, title="Partitioning...", cmdlist=[cmd, cmd2], finishedCallback = self.do_Format)
		
	def do_Format(self):
		device = "/dev/%s1" % (self.device)
		cmd = "echo -e 'Formatting: %s \n\n'" % (device)
		cmd2 = "/sbin/mkfs.ext4 %s" % (device)
		self.session.open(Console, title="Formatting...", cmdlist=[cmd, cmd2], finishedCallback = self.succesS)
	
	def step_Bump(self):
		if self.step == 1:
			self.stepOne()
		elif self.step == 2:
			self.stepTwo()
		elif self.step == 3:
			self.stepThree()
		elif self.step == 4:
			self.stepFour()
			
	def get_Devicelist(self):
		devices = []
		folder = listdir("/sys/block")
		for f in folder:
			if f.find('sd') != -1:
				devices.append(f)
		return devices
			
	def get_Deviceinfo(self, device):
		info = vendor = model = size = ""
		filename = "/sys/block/%s/device/vendor" % (device)
		if fileExists(filename):
			vendor = file(filename).read().strip()
			filename = "/sys/block/%s/device/model" % (device)
			model = file(filename).read().strip()
			filename = "/sys/block/%s/size" % (device)
			size = int(file(filename).read().strip())
			cap = size / 1000 * 512 / 1000
			size = "%d.%03d GB" % (cap/1000, cap%1000)
		info = "Model: %s %s\nSize: %s\nDevice: /dev/%s" % (vendor, model, size, device)
		return info
	
	
	
	def succesS(self):
		self.wizClose("Usb storage formatted.\nYou can now use the Black Pole Devices Manager to assign your preferred mount point.")

	def wizClose(self, msg):
		self.session.openWithCallback(self.close, MessageBox, msg, MessageBox.TYPE_INFO)




