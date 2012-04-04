from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigYesNo, ConfigText, ConfigSelection, ConfigClock
from Components.Sources.List import List
from Components.Network import iNetwork
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_CURRENT_SKIN
from os import system, remove as os_remove, rename as os_rename, popen, getcwd, chdir




class DeliteSettings(Screen):
	skin = """
	<screen position="160,110" size="390,360" title="Black Pole Extra Settings">
		<widget source="list" render="Listbox" position="10,10" size="370,330" scrollbarMode="showOnDemand" >
			<convert type="TemplatedMultiContent">
                		{"template": [
                		MultiContentEntryText(pos = (60, 1), size = (300, 36), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),
                		MultiContentEntryPixmapAlphaTest(pos = (4, 2), size = (36, 36), png = 1),
                		],
                		"fonts": [gFont("Regular", 24)],
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
		
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close

		})
		
	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		self.sel = self.sel[2]
		
		if self.sel == 0:
			from Screens.BpDevice import DeliteDevicesPanel
			self.session.open(DeliteDevicesPanel)
		elif self.sel == 1:
			from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
			self.session.open(BhNetBrowser)
		elif self.sel == 2:
			from Screens.BpFormat import Bp_UsbFormat
			self.session.open(Bp_UsbFormat)
		elif self.sel == 3:
			self.session.open(BhSetupOSD3)
		elif self.sel == 4:
			from Plugins.SystemPlugins.UIPositionSetup.plugin import UIPositionSetup
			self.session.open(UIPositionSetup)
		elif self.sel == 5:
			from Plugins.SystemPlugins.UI3DSetup.plugin import UI3DSetupScreen
			self.session.open(UI3DSetupScreen)
		elif self.sel == 6:
			self.session.open(BhSetupIntEpg)
		elif self.sel == 7:
			self.session.open(BhSetupRecord)
		elif self.sel == 8:
			from Screens.RecordPaths import RecordPathsSettings
			self.session.open(RecordPathsSettings)
		elif self.sel == 9:
			self.session.open(BhSetupSubtitle)
		elif self.sel == 10:
			self.session.open(BhSetupAutolanguage)
		elif self.sel == 11:
			self.session.open(BhSetupHttpStream)
		else:
			self.noYet()
		
	def noYet(self):
		nobox = self.session.open(MessageBox, "Function Not Yet Available", MessageBox.TYPE_INFO)
		nobox.setTitle(_("Info"))
	
		
	def updateList(self):
		self.list = [ ]
		mypath = resolveFilename(SCOPE_CURRENT_SKIN, "")
		if mypath == "/usr/share/enigma2/":
			mypath = "/usr/share/enigma2/skin_default/"
		
		mypixmap = mypath + "icons/infopanel_space.png"
		png = LoadPixmap(mypixmap)
		name = "Devices Manager & Mountpoints"
		idx = 0
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/mountwizard.png"
		png = LoadPixmap(mypixmap)
		name = "Network Browse & Mountpoints"
		idx = 1
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/infopanel_space.png"
		png = LoadPixmap(mypixmap)
		name = "Usb Format Wizard"
		idx = 2
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/infopanel_osd.png"
		png = LoadPixmap(mypixmap)
		name = "Osd settings"
		idx = 3
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/infopanel_osd.png"
		png = LoadPixmap(mypixmap)
		name = "Osd Position setup"
		idx = 4
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/infopanel_osd.png"
		png = LoadPixmap(mypixmap)
		name = "Osd 3D setup"
		idx = 5
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/infopanel_samba.png"
		png = LoadPixmap(mypixmap)
		name = "Internal Epg settings"
		idx = 6
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/infopanel_cron.png"
		png = LoadPixmap(mypixmap)
		name = "Record settings"
		idx = 7
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/infopanel_space.png"
		png = LoadPixmap(mypixmap)
		name = "Recording paths"
		idx = 8
		res = (name, png, idx)
		self.list.append(res)
				
		mypixmap = mypath + "icons/infopanel_kmod.png"
		png = LoadPixmap(mypixmap)
		name = "Subtitle settings"
		idx = 9
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/inadynsettings.png"
		png = LoadPixmap(mypixmap)
		name = "Auto language settings"
		idx = 10
		res = (name, png, idx)
		self.list.append(res)
		
		mypixmap = mypath + "icons/infopanel_samba.png"
		png = LoadPixmap(mypixmap)
		name = "Http stream settings"
		idx = 11
		res = (name, png, idx)
		self.list.append(res)
		
		self["list"].list = self.list
		


class BhSetupOSD3(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="Osd Settings">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="140,450" size="140,40" alphatest="on" />
		<widget name="key_red" position="140,450" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,450" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
				
		self.list.append(getConfigListEntry(_("Infobar timeout"), config.usage.infobar_timeout))
		self.list.append(getConfigListEntry(_("Show second infobar"), config.usage.show_second_infobar))
		self.list.append(getConfigListEntry(_("Show event-progress in channel selection"), config.usage.show_event_progress_in_servicelist))
		self.list.append(getConfigListEntry(_("Show channel numbers in channel selection"), config.usage.show_channel_numbers_in_servicelist))
		self.list.append(getConfigListEntry(_("Show infobar on channel change"), config.usage.show_infobar_on_zap))
		self.list.append(getConfigListEntry(_("Show infobar on skip forward/backward"), config.usage.show_infobar_on_skip))
		self.list.append(getConfigListEntry(_("Show infobar on event change"), config.usage.show_infobar_on_event_change))
		self.list.append(getConfigListEntry(_("Hide zap errors"), config.usage.hide_zap_errors))
		self.list.append(getConfigListEntry(_("Hide CI messages"), config.usage.hide_ci_messages))
		self.list.append(getConfigListEntry(_("Show crypto info in infobar"), config.usage.show_cryptoinfo))
		self.list.append(getConfigListEntry(_("Swap SNR in db with SNR in percentage on OSD"), config.usage.swap_snr_on_osd))
		self.list.append(getConfigListEntry(_("Show EIT now/next in infobar"), config.usage.show_eit_nownext))
		
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()

class BhSetupRecord(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="Record Settings">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="140,450" size="140,40" alphatest="on" />
		<widget name="key_red" position="140,450" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,450" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
		
		self.list.append(getConfigListEntry(_("Recordings always have priority"), config.recording.asktozap))
		self.list.append(getConfigListEntry(_("Margin before record (minutes)"), config.recording.margin_before))
		self.list.append(getConfigListEntry(_("Margin after record"), config.recording.margin_after))
		self.list.append(getConfigListEntry(_("Show Message when Recording starts"), config.usage.show_message_when_recording_starts))
		self.list.append(getConfigListEntry(_("Load Length of Movies in Movielist"), config.usage.load_length_of_movies_in_moviellist))
		self.list.append(getConfigListEntry(_("Show status icons in Movielist"), config.usage.show_icons_in_movielist))
		
		self.list.append(getConfigListEntry(_("Behavior when a movie is started"), config.usage.on_movie_start))
		self.list.append(getConfigListEntry(_("Behavior when a movie is stopped"), config.usage.on_movie_stop))
		self.list.append(getConfigListEntry(_("Behavior when a movie reaches the end"), config.usage.on_movie_eof))
		self.list.append(getConfigListEntry(_("Behavior of 'pause' when paused"), config.seek.on_pause))
		self.list.append(getConfigListEntry(_("Custom skip time for '1'/'3'-keys"), config.seek.selfdefined_13))
		self.list.append(getConfigListEntry(_("Custom skip time for '4'/'6'-keys"), config.seek.selfdefined_46))
		self.list.append(getConfigListEntry(_("Custom skip time for '7'/'9'-keys"), config.seek.selfdefined_79))
		self.list.append(getConfigListEntry(_("Fast Forward speeds"), config.seek.speeds_forward))
		self.list.append(getConfigListEntry(_("Rewind speeds"), config.seek.speeds_backward))
		self.list.append(getConfigListEntry(_("Slow Motion speeds"), config.seek.speeds_slowmotion))
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()

class BhSetupIntEpg(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="Internal Epg settings">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="140,450" size="140,40" alphatest="on" />
		<widget name="key_red" position="140,450" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,450" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
						
		self.list.append(getConfigListEntry(_("Enable EIT EPG"), config.epg.eit))
		self.list.append(getConfigListEntry(_("Enable MHW EPG"), config.epg.mhw))
		self.list.append(getConfigListEntry(_("Enable freesat EPG"), config.epg.freesat))
		self.list.append(getConfigListEntry(_("Enable ViaSat EPG"), config.epg.viasat))
		self.list.append(getConfigListEntry(_("Enable Netmed EPG"), config.epg.netmed))
		self.list.append(getConfigListEntry(_("Maintain old EPG data for"), config.epg.histminutes))
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()

class BhSetupSubtitle(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="Subtitle settings">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="140,450" size="140,40" alphatest="on" />
		<widget name="key_red" position="140,450" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,450" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)

		self.list.append(getConfigListEntry(_("Teletext subtitle color"), config.subtitles.ttx_subtitle_colors))
		self.list.append(getConfigListEntry(_("Use original teletext position"), config.subtitles.ttx_subtitle_original_position))
		self.list.append(getConfigListEntry(_("Rewrap teletext subtitles"), config.subtitles.subtitle_rewrap))
		self.list.append(getConfigListEntry(_("Custom text position"), config.subtitles.subtitle_position))
		self.list.append(getConfigListEntry(_("Custom text alignment"), config.subtitles.subtitle_alignment))
		self.list.append(getConfigListEntry(_("Text border width"), config.subtitles.subtitle_borderwidth))		
		self.list.append(getConfigListEntry(_("Text font size"), config.subtitles.subtitle_fontsize))
		self.list.append(getConfigListEntry(_("Subtitle delay when timing lacks"), config.subtitles.subtitle_noPTSrecordingdelay))
		self.list.append(getConfigListEntry(_("Yellow DVB subtitles"), config.subtitles.dvb_subtitles_yellow))
		self.list.append(getConfigListEntry(_("Use DVB subtitles position"), config.subtitles.dvb_subtitles_original_position))
		self.list.append(getConfigListEntry(_("Centered DVB subtitles"), config.subtitles.dvb_subtitles_centered))
		self.list.append(getConfigListEntry(_("DVB subtitle black transparency"), config.subtitles.dvb_subtitles_backtrans))
		self.list.append(getConfigListEntry(_("Yellow pango subtitles"), config.subtitles.pango_subtitles_yellow))
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()		
	
class BhSetupAutolanguage(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="Auto language settings">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="140,450" size="140,40" alphatest="on" />
		<widget name="key_red" position="140,450" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,450" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
						
		self.list.append(getConfigListEntry(_("Audio language selection 1"), config.autolanguage.audio_autoselect1))
		self.list.append(getConfigListEntry(_("Audio language selection 2"), config.autolanguage.audio_autoselect2))
		self.list.append(getConfigListEntry(_("Audio language selection 3"), config.autolanguage.audio_autoselect3))
		self.list.append(getConfigListEntry(_("Audio language selection 4"), config.autolanguage.audio_autoselect4))
		self.list.append(getConfigListEntry(_("Prefer AC3"), config.autolanguage.audio_defaultac3))
		self.list.append(getConfigListEntry(_("Prefer audio stream stored by service"), config.autolanguage.audio_usecache))
		self.list.append(getConfigListEntry(_("Subtitle language selection 1"), config.autolanguage.subtitle_autoselect1))
		self.list.append(getConfigListEntry(_("Subtitle language selection 2"), config.autolanguage.subtitle_autoselect2))
		self.list.append(getConfigListEntry(_("Subtitle language selection 3"), config.autolanguage.subtitle_autoselect3))
		self.list.append(getConfigListEntry(_("Subtitle language selection 4"), config.autolanguage.subtitle_autoselect4))
		self.list.append(getConfigListEntry(_("Allow Subtitle equals Audio mask"), config.autolanguage.equal_languages))
		self.list.append(getConfigListEntry(_("Allow hearing impaired subtitles"), config.autolanguage.subtitle_hearingimpaired))
		self.list.append(getConfigListEntry(_("Prefer hearing impaired subtitles"), config.autolanguage.subtitle_defaultimpaired))
		self.list.append(getConfigListEntry(_("Prefer DVB-grafical subtitles"), config.autolanguage.subtitle_defaultdvb))
		self.list.append(getConfigListEntry(_("Prefer subtitle stored by service"), config.autolanguage.subtitle_usecache))
		self.list.append(getConfigListEntry(_("EPG language selection 1"), config.autolanguage.audio_epglanguage))
		self.list.append(getConfigListEntry(_("EPG language selection 2"), config.autolanguage.audio_epglanguage_alternative))
		
		
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()
		
class BhSetupHttpStream(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,500" title="Http stream settings">
		<widget name="config" position="10,10" size="680,430" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="140,450" size="140,40" alphatest="on" />
		<widget name="key_red" position="140,450" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,450" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,450" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
						
		self.list.append(getConfigListEntry(_("Include EIT in http streams"), config.streaming.stream_eit))
		self.list.append(getConfigListEntry(_("Include AIT in http streams"), config.streaming.stream_ait))
		self.list.append(getConfigListEntry(_("Include ECM in http streams"), config.streaming.stream_ecm))
		self.list.append(getConfigListEntry(_("Descramble http streams"), config.streaming.descramble))
		
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()
		

class BhNetBrowser(Screen):
	skin = """
	<screen position="center,center" size="800,520" title="Select Network Interface">
		<widget source="list" render="Listbox" position="10,10" size="780,460" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
    		<ePixmap pixmap="skin_default/buttons/red.png" position="200,480" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="440,480" size="140,40" alphatest="on" />
		<widget name="key_red" position="200,480" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_yellow" position="440,480" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
    	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["key_red"] = Label(_("Select"))
		self["key_yellow"] = Label(_("Close"))
		
		self.list = []
		self["list"] = List(self.list)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.selectInte,
			"back": self.close,
			"red": self.selectInte,
			"yellow": self.close
		})
		
		self.list = [ ]
		self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getAdapterList()]
		for x in self.adapters:
			res = (x[0], x[1])
			self.list.append(res)

		self["list"].list = self.list
		
	def selectInte(self):
		mysel = self["list"].getCurrent()
		if mysel:
			inter = mysel[1]
			self.session.open(NetworkBrowser, inter, "/usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser")

