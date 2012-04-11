from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.About import about
from Tools.Directories import fileExists
from ServiceReference import ServiceReference
from os import system, listdir, remove as os_remove
from enigma import iServiceInformation, eTimer
import socket


class DeliteBluePanel(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["lab1"] = Label()
		self["lab2"] = Label(_("Set Default CAM"))
		self["lab3"] = Label()
		self["Ilab1"] = Label()
		self["Ilab2"] = Label()
		self["Ilab3"] = Label()
		self["Ilab4"] = Label()
		self["activecam"] = Label()
		self["Ecmtext"] = ScrollLabel()
		
		self["actions"] = ActionMap(["ColorActions", "OkCancelActions", "DirectionActions"],
		{
			"ok": self.keyOk,
			"cancel": self.close,
			"green": self.keyGreen,
			"red": self.keyRed,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
			"up": self["Ecmtext"].pageUp,
			"down": self["Ecmtext"].pageDown
		}, -1)
		
		self.emlist = []
		self.populate_List()
		self["list"] = MenuList(self.emlist)
		self["lab1"].setText("%d  CAMs Installed" % (len(self.emlist)))
		self.onShow.append(self.updateBP)

	def populate_List(self):
		self.camnames = {}
		cams = listdir("/usr/camscript")
		for fil in cams:
			if fil.find('Ncam_') != -1:
				f = open("/usr/camscript/" + fil,'r')
				for line in f.readlines():
					line = line.strip()
					if line.find('CAMNAME=') != -1:
						name = line[9:-1]
						self.emlist.append(name)
						self.camnames[name] = "/usr/camscript/" + fil
				f.close()

	def updateBP(self):
		try:
			name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			sinfo = self.session.nav.getCurrentService().info()
			provider = self.getServiceInfoValue(iServiceInformation.sProvider, sinfo)
			wide = self.getServiceInfoValue(iServiceInformation.sAspect, sinfo)
			width = sinfo and sinfo.getInfo(iServiceInformation.sVideoWidth) or -1
			height = sinfo and sinfo.getInfo(iServiceInformation.sVideoHeight) or -1	
			videosize = "%dx%d" %(width, height)
			aspect = "16:9" 
			if aspect in ( 1, 2, 5, 6, 9, 0xA, 0xD, 0xE ):
				aspect = "4:3"
		except:
			name = "N/A"; provider = "N/A"; aspect = "N/A"; videosize  = "N/A"	
		
		self["Ilab1"].setText("Name: " + name)
		self["Ilab2"].setText("Provider: " + provider)
		self["Ilab3"].setText("Aspect Ratio: " + aspect)
		self["Ilab4"].setText("Videosize: " + videosize)
	
		self.defaultcam = "/usr/camscript/Ncam_Ci.sh"
		if fileExists("/etc/BhCamConf"):
			f = open("/etc/BhCamConf",'r')
			for line in f.readlines():
   				parts = line.strip().split("|")
				if parts[0] == "deldefault":
					self.defaultcam = parts[1]
			f.close()
			
		self.defCamname =  "Common Interface"	
		for c in self.camnames.keys():
			if self.camnames[c] == self.defaultcam:
				self.defCamname = c
		pos = 0
		for x in self.emlist:
			if x == self.defCamname:
				self["list"].moveToIndex(pos)
				break
			pos += 1

		mytext = "";
		if fileExists("/tmp/ecm.info"):
			f = open("/tmp/ecm.info",'r')
 			for line in f.readlines():
				mytext = mytext + line.strip() + "\n"
 			f.close()
		if len(mytext) < 5:
			mytext = "\n\n    Ecm Info not available."
				
		self["activecam"].setText(self.defCamname)
		self["Ecmtext"].setText(mytext)


	def getServiceInfoValue(self, what, myserviceinfo):
		v = myserviceinfo.getInfo(what)
		if v == -2:
			v = myserviceinfo.getInfoString(what)
		elif v == -1:
			v = "N/A"
		return v


	def keyOk(self):
		self.sel = self["list"].getCurrent()
		self.newcam = self.camnames[self.sel]
		
		out = open("/etc/BhCamConf",'w')
		out.write("deldefault|" + self.newcam + "\n")
		out.close()
		
		out = open("/etc/CurrentBhCamName", "w")
		out.write(self.sel)
		out.close()
		cmd = "cp -f " + self.newcam + " /usr/bin/StartBhCam"
		system (cmd)
		cmd = "STOP_CAMD," + self.defaultcam
		self.sendtoBh_sock(cmd)
		self.session.openWithCallback(self.keyOk2, startstopCam, self.defCamname, "stopping")
		
	def keyOk2(self):
		cmd = "NEW_CAMD," + self.newcam
		self.sendtoBh_sock(cmd)
		oldcam = self.camnames[self.sel]
		self.session.openWithCallback(self.myclose, startstopCam, self.sel, "starting")
		
		
	def sendtoBh_sock(self, data):
		client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		client_socket.connect("/tmp/Blackhole.socket")
		client_socket.send(data)
            	client_socket.close()
				
	def keyYellow(self):
		if fileExists("/proc/blackhole/version"):
			self.session.open(MessageBox, "Wrong kernel version. Please install Black Pole image in Flash.", MessageBox.TYPE_INFO)
		else:
			self.session.open(BhsysInfo)

	def keyBlue(self):
		from Screens.BpSet import DeliteSettings
		self.session.open(DeliteSettings)
		
	def keyGreen(self):
		self.session.open(MessageBox, "Sorry, function not available in Black Pole", MessageBox.TYPE_INFO)
		
	def keyRed(self):
		from Plugins.SystemPlugins.CrossEPG.crossepg_main import crossepg_main
		crossepg_main.setup(self.session)

	def myclose(self):
		self.close()
	

class startstopCam(Screen):
	skin = """
	<screen position="center,center" size="360,200" title="Black Pole" flags="wfNoBorder">
		<widget name="lab1" position="10,10" halign="center" size="340,180" zPosition="1" font="Regular;20" valign="center" transparent="1" />
	</screen>"""
	
	def __init__(self, session, name, what):
		Screen.__init__(self, session)
		
		msg = "Please wait while %s\n %s ..." % (what, name)
		self["lab1"] = Label(msg)
		self.delay = 800
		if what == "starting":
			self.delay= 3000
		
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.end)
		self.onShow.append(self.startShow)
		
	def startShow(self):
		self.activityTimer.start(self.delay)

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
		memTotal = memFree = swapTotal = swapFree = 0
		for line in open("/proc/meminfo",'r'):
			parts = line.split(':')
			key = parts[0].strip()
			if key == "MemTotal":
				memTotal = parts[1].strip()
			elif key in ("MemFree", "Buffers", "Cached"):
				memFree += int(parts[1].strip().split(' ',1)[0])
			elif key == "SwapTotal":
				swapTotal = parts[1].strip()
			elif key == "SwapFree":
				swapFree = parts[1].strip()
		text += "Total memory:\t%s\n" % memTotal
		text += "Free memory:\t%s kB\n"  % memFree
		text += "Swap total:\t%s \n"  % swapTotal
		text += "Swap free:\t%s \n"  % swapFree
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
				if len(parts) == 6:
					text += parts[5] + "\t" + parts[1].strip() + "  " + parts[2].strip() + "  " + parts[3].strip() + "  " + parts[4] + "\n"
		f.close()
		os_remove("/tmp/syinfo.tmp")
		
		text += "\nSOFTWARE\n"
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