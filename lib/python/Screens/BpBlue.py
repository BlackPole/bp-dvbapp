from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.BpSet import DeliteSettings
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.config import config, ConfigSubsection, ConfigText
from Components.About import about
from Tools.Directories import fileExists
from ServiceReference import ServiceReference
from os import system, listdir, chdir, getcwd, rename as os_rename, remove as os_remove
from enigma import iServiceInformation, eTimer
import socket

config.delite = ConfigSubsection()
config.delite.fp = ConfigText(default="")

class DeliteBluePanel(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["lab1"] = Label(_("xx CAMs Installed"))
		self["lab2"] = Label(_("Set Default CAM"))
		self["lab3"] = Label(_("Active CAM"))
		self["Ilab1"] = Label()
		self["Ilab2"] = Label()
		self["Ilab3"] = Label()
		self["Ilab4"] = Label()
		self["activecam"] = Label()
		self["Ecmtext"] = ScrollLabel()
		
		self.emlist = []
		self.populate_List()
		self["list"] = MenuList(self.emlist)
		totcam = str(len(self.emlist))
		self["lab1"].setText(totcam + "   CAMs Installed")
		
		self.onShow.append(self.updateBP)
		#self.onClose.append(self.delTimer)
		
		self["myactions"] = ActionMap(["ColorActions", "OkCancelActions", "DirectionActions"],
		{
			"ok": self.keyOk,
			"cancel": self.close,
			"green": self.autoCam,
			"red": self.keyRed,
			"yellow": self.nInfo,
			"blue": self.Settings,
			"up": self["Ecmtext"].pageUp,
			"down": self["Ecmtext"].pageDown
		}, -1)
		
	def nInfo(self):
		self.session.open(BhsysInfo)

	def Settings(self):
		self.session.open(DeliteSettings)
		
	def autoCam(self):
		self.noImpl()
		
	def keyRed(self):
		self.bhCrossepgPanel()

	def populate_List(self):
		self.camnames = {}
		cams = listdir("/usr/camscript")
		for fil in cams:
			if fil.find('Ncam_') != -1:
				f = open("/usr/camscript/" + fil,'r')
				for line in f.readlines():
					if line.find('CAMNAME=') != -1:
						line = line.strip()
						cn = line[9:-1]
						self.emlist.append(cn)
						self.camnames[cn] = "/usr/camscript/" + fil
						
						
				f.close()
		if fileExists("/etc/BhCamConf") == False:
			out = open("/etc/BhCamConf", "w")
			out.write("delcurrent|/usr/camscript/Ncam_Ci.sh\n")
			out.write("deldefault|/usr/camscript/Ncam_Ci.sh\n")
			out.close()

	def updateBP(self):
		name = "N/A"; provider = "N/A"; aspect = "N/A"; videosize  = "N/A"
		myserviceinfo = ""
		myservice = self.session.nav.getCurrentService()
		if myservice is not None:
			myserviceinfo = myservice.info()
			if self.session.nav.getCurrentlyPlayingServiceReference():
				name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()

			provider = self.getServiceInfoValue(iServiceInformation.sProvider, myserviceinfo)
			aspect = self.getServiceInfoValue(iServiceInformation.sAspect, myserviceinfo)
			if aspect in ( 1, 2, 5, 6, 9, 0xA, 0xD, 0xE ):
				aspect = "4:3"
			else:
				aspect = "16:9"
				
			if myserviceinfo:	
				width = myserviceinfo and myserviceinfo.getInfo(iServiceInformation.sVideoWidth) or -1
				height = myserviceinfo and myserviceinfo.getInfo(iServiceInformation.sVideoHeight) or -1
				if width != -1 and height != -1:
					videosize = "%dx%d" %(width, height)
		
		self["Ilab1"].setText("Name: " + name)
		self["Ilab2"].setText("Provider: " + provider)
		self["Ilab3"].setText("Aspect Ratio: " + aspect)
		self["Ilab4"].setText("Videosize: " + videosize)
		
		self.currentcam = "/usr/camscript/Ncam_Ci.sh"
		self.defaultcam = "/usr/camscript/Ncam_Ci.sh"
		f = open("/etc/BhCamConf",'r')
		for line in f.readlines():
   			parts = line.strip().split("|")
			if parts[0] == "delcurrent":
				self.currentcam = parts[1]
			elif parts[0] == "deldefault":
				self.defaultcam = parts[1]
		f.close()
			
		defCamname = "Common Interface"
		curCamname = "Common Interface"	
			
		for c in self.camnames.keys():
			if self.camnames[c] == self.defaultcam:
				defCamname = c
			if  self.camnames[c] == self.currentcam:
				curCamname = c	
		
		pos = 0
		for x in self.emlist:
			if x == defCamname:
				self["list"].moveToIndex(pos)
				break
			pos += 1

		mytext = "";
		if fileExists("/tmp/ecm.info"):
			f = open("/tmp/ecm.info",'r')
 			for line in f.readlines():
     				line = line.replace('\n', '')
				line = line.strip()
				if len(line) > 3:
					mytext = mytext + line + "\n"
 			f.close()
		if len(mytext) < 5:
			mytext = "\n\n    Ecm Info not available."
		
		
		self["activecam"].setText(curCamname)
		self["Ecmtext"].setText(mytext)


	def getServiceInfoValue(self, what, myserviceinfo):
		if myserviceinfo is None:
			return ""
		v = myserviceinfo.getInfo(what)
		if v == -2:
			v = myserviceinfo.getInfoString(what)
		elif v == -1:
			v = "N/A"
		return v


	def keyOk(self):
		self.sel = self["list"].getCurrent()
		self.newcam = self.camnames[self.sel]
		
		inme = open("/etc/BhCamConf",'r')
		out = open("/etc/BhCamConf.tmp",'w')
		for line in inme.readlines():
			if line.find("delcurrent") == 0:
				line = "delcurrent|" + self.newcam + "\n"
			elif line.find("deldefault") == 0:
				line = "deldefault|" + self.newcam + "\n"	
			out.write(line)
		out.close()
		inme.close()
		os_rename("/etc/BhCamConf.tmp", "/etc/BhCamConf")

		out = open("/etc/CurrentBhCamName", "w")
		out.write(self.sel)
		out.close()
		cmd = "cp -f " + self.newcam + " /usr/bin/StartBhCam"
		system (cmd)
		
		mydata = "STOP_CAMD," + self.currentcam
		client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		client_socket.connect("/tmp/Blackhole.socket")
		client_socket.send(mydata)
            	client_socket.close()
		mydata = "NEW_CAMD," + self.newcam
		client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		client_socket.connect("/tmp/Blackhole.socket")
		client_socket.send(mydata)
            	client_socket.close()
		
		self.session.openWithCallback(self.myclose, Nab_DoStartCam2, self.sel)
				

	def myclose(self):
		self.close()
	
	def noImpl(self):
		self.session.open(MessageBox, "Sorry, function not available in Black Pole", MessageBox.TYPE_INFO)
		
	def bhCrossepgPanel(self):
		from Plugins.SystemPlugins.CrossEPG.crossepg_main import crossepg_main
		crossepg_main.setup(self.session)

class Nab_DoStartCam2(Screen):
	skin = """
	<screen position="center,center" size="300,200" title="Black Pole" flags="wfNoBorder">
		<widget name="lab1" position="10,10" halign="center" size="280,180" zPosition="1" font="Regular;20" valign="center" transparent="1" />
	</screen>"""
	
	def __init__(self, session, title):
		Screen.__init__(self, session)
		
		msg = "Please wait while starting\n" + title + "..."
		self["lab1"] = Label(msg)

		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.end)
		self.onShow.append(self.startShow)
		
	def startShow(self):
		self.activityTimer.start(1500)

	def end(self):
		self.activityTimer.stop()
		del self.activityTimer
		self.close()

class BhsysInfo(Screen):
	skin = """
	<screen position="center,center" size="800,600" title="Black Pole Info" flags="wfNoBorder">
		<widget name="lab1" position="50,25" halign="left" size="700,550" zPosition="1" font="Regular;20" valign="top" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		self["lab1"] =  Label()

		self.onShow.append(self.updateInfo)
		
		self["myactions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.close,
			"cancel": self.close,
		}, -1)
		
	def updateInfo(self):
		rc = system("df -h > /tmp/syinfo.tmp")
		text = "BOX\n"
		text += "Brand:\tVuplus\n"
		f = open("/proc/stb/info/vumodel",'r')
 		text += "Model:\t" + f.readline()
 		f.close()
		f = open("/proc/stb/info/chipset",'r')
 		text += "Chipset:\t" + f.readline() +"\n"
 		f.close()
		text += "MEMORY\n"
		f = open("/proc/meminfo",'r')
		text += f.readline()
		text += f.readline()
		text += f.readline()
		text += f.readline()
		f.close()
		text += "\nSTORAGE\n"
		f = open("/tmp/syinfo.tmp",'r')
		line = f.readline()
		parts = line.split()
		text += parts[0] + "\t" + parts[1].strip() + "      " + parts[2].strip() + "    " + parts[3].strip() + "    " + parts[4] + "\n"
		line = f.readline()
		parts = line.split()
		text += "Flash" + "\t" + parts[1].strip() + "  " + parts[2].strip()  + "  " +  parts[3].strip()  + "  " +  parts[4] + "\n"
 		for line in f.readlines():
			if line.find('/media/') != -1:
				line = line.replace('/media/', '   ')
				parts = line.split()
				text += parts[5] + "\t" + parts[1].strip() + "  " + parts[2].strip() + "  " + parts[3].strip() + "  " + parts[4] + "\n"
		f.close()
		os_remove("/tmp/syinfo.tmp")
		
		text += "\nSoftware\n"
		f = open("/etc/bpversion",'r')
		text += "Firmware v.:\t" + f.readline()
		f.close()
		text += "DvbApp v.: \t" +  about.getEnigmaVersionString() + "\n"
		text += "Kernel v.: \t" +  about.getKernelVersionString() + "\n"
		
		self["lab1"].setText(text)
		



class DeliteBp:
	def __init__(self):
		self["DeliteBp"] = ActionMap( [ "InfobarExtensions" ],
			{
				"DeliteBpshow": (self.showDeliteBp),
			})

	def showDeliteBp(self):
		self.session.openWithCallback(self.callNabAction, DeliteBluePanel)

	def callNabAction(self, *args):
		if len(args):
			(actionmap, context, action) = args
			actionmap.action(context, action)