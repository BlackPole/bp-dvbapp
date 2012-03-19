# Based on PliExtraInfo
# Recoded for Black Pole by meo.

from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll


class BpExtraInfo(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)

		self.type = type
		self.poll_interval = 1000
		self.poll_enabled = True
		self.caid_data = (
			( "0x100",  "0x1ff", "Seca",    "S" ),
			( "0x500",  "0x5ff", "Via",     "V" ),
			( "0x600",  "0x6ff", "Irdeto",  "I" ),
			( "0x900",  "0x9ff", "NDS",     "Nd"),
			( "0xb00",  "0xbff", "Conax",   "Co"),
			( "0xd00",  "0xdff", "CryptoW", "Cw"),
			("0x1700", "0x17ff", "Beta",    "B" ),
			("0x1800", "0x18ff", "Nagra",   "N" ),
			("0x2600", "0x2600", "Biss",    "Bi"),
			("0x4ae0", "0x4ae1", "Dre",     "D" )
		)

	def GetEcmInfo(self):
		try:
			ecm = open('/tmp/ecm.info', 'rb').readlines()
			bp_inuse_info = "Fta"
			info = {}
			for line in ecm:
				d = line.split(':', 1)
				if len(d) > 1:
					info[d[0].strip()] = d[1].strip()
			# info is dictionary
			decCI = info.get('caid', '0')
			provider = info.get('provider', ' ')
			if provider == " ":
				provider = info.get('prov', ' ')
			#2
			using = info.get('using', '')
			decode = info.get('decode', '')
			source = info.get('source', '')
			reader = info.get('reader', '')
			#6
			address = info.get('address', 'Unknown')
			addressO = info.get('from', 'Unknown')
			hops = info.get('hops', '0')
			ecm_time = info.get('ecm time', '?')
			
			
		except:
			ecm = None
			decCI = '0'
			provider = ''
			using = ''
			decode = ''
			source = ''
			reader = ''
			address = ''
			addressO = ''
			hops = '0'
			ecm_time = '0'
			
		return decCI, provider, using, decode, source, reader, address, addressO, hops, ecm_time
	
	def get_caName(self):
		try:
			f = open("/etc/CurrentBhCamName",'r')
 			name = f.readline().strip()
 			f.close()
		except:
			name = "Common Interface"
		return name
		
	@cached
	def getText(self):
		service = self.source.service
		if service is None:
			return ""
		info = service and service.info()
		
		if self.type == "NetInfo":
			text = ''
			data = self.GetEcmInfo()
			if data[2]:
				if data[2] != 'fta':
					text = "Address: %s   Hops: %s   Ecm time: %ss" % (data[6], data[8], data[9])
			elif data[5]:
				text = "Address: %s   Hops: %s   Ecm time: %ss" % (data[7], data[8], data[9])
			return text
				
		elif self.type == "EcmInfo":
			text = ''
			data = self.GetEcmInfo()
			text = "CaId: %s     Provider: %s" % (data[0], data[1])
			if data[0] == "0x000" or data[0] == "0":
				text = ""
			return text
		
		elif self.type == "E-C-N":
			text = 'Fta'
			data = self.GetEcmInfo()
			if data[2]:
				if data[2] == "fta":
					text = 'Fta'
				elif data[2] == 'emu':
					text = "Emulator"
				elif data[2] == 'sci':
					text = "Card"
				else:
					text = "Network"
			elif data[5]:
				text = "Card"
				pos = data[7].find('.')
				if pos > 1:
					text = "Network"
					
			return text
				
		elif self.type == "CamName":
			return self.get_caName()
		
		elif self.type == "CryptoBar":
			data = self.GetEcmInfo()
			self.current_caid= data[0]
			res = ""
			available_caids = info.getInfoObject(iServiceInformation.sCAIDs)	
			for caid_entry in self.caid_data:
				if int(self.current_caid, 16) >= int(caid_entry[0], 16) and int(self.current_caid, 16) <= int(caid_entry[1], 16):
					color="\c0000??00"
				else:
					color = "\c007?7?7?"
					try:
						for caid in available_caids:
							if caid >= int(caid_entry[0], 16) and caid <= int(caid_entry[1], 16):
								color="\c00????00"
					except:
						pass

				if res: res += " "
				res += color + caid_entry[3]
		
			res += "\c00??????"
			return res
		return ""	
			
	text = property(getText)

	@cached
	def getBool(self):
		service = self.source.service
		info = service and service.info()

		if not info:
			return False

		if self.type == "CryptoCaidSecaAvailable":
			request_caid = "S"
			request_selected = False
		elif self.type == "CryptoCaidViaAvailable":
			request_caid = "V"
			request_selected = False
		elif self.type == "CryptoCaidIrdetoAvailable":
			request_caid = "I"
			request_selected = False
		elif self.type == "CryptoCaidNDSAvailable":
			request_caid = "Nd"
			request_selected = False
		elif self.type == "CryptoCaidConaxAvailable":
			request_caid = "Co"
			request_selected = False
		elif self.type == "CryptoCaidCryptoWAvailable":
			request_caid = "Cw"
			request_selected = False
		elif self.type == "CryptoCaidBetaAvailable":
			request_caid = "B"
			request_selected = False
		elif self.type == "CryptoCaidNagraAvailable":
			request_caid = "N"
			request_selected = False
		elif self.type == "CryptoCaidBissAvailable":
			request_caid = "Bi"
			request_selected = False
		elif self.type == "CryptoCaidDreAvailable":
			request_caid = "D"
			request_selected = False
		elif self.type == "CryptoCaidSecaSelected":
			request_caid = "S"
			request_selected = True
		elif self.type == "CryptoCaidViaSelected":
			request_caid = "V"
			request_selected = True
		elif self.type == "CryptoCaidIrdetoSelected":
			request_caid = "I"
			request_selected = True
		elif self.type == "CryptoCaidNDSSelected":
			request_caid = "Nd"
			request_selected = True
		elif self.type == "CryptoCaidConaxSelected":
			request_caid = "Co"
			request_selected = True
		elif self.type == "CryptoCaidCryptoWSelected":
			request_caid = "Cw"
			request_selected = True
		elif self.type == "CryptoCaidBetaSelected":
			request_caid = "B"
			request_selected = True
		elif self.type == "CryptoCaidNagraSelected":
			request_caid = "N"
			request_selected = True
		elif self.type == "CryptoCaidBissSelected":
			request_caid = "Bi"
			request_selected = True
		elif self.type == "CryptoCaidDreSelected":
			request_caid = "D"
			request_selected = True
		else:
			return False

		if info.getInfo(iServiceInformation.sIsCrypted) != 1:
			return False

		data = self.GetEcmInfo()

		if data is None:
			return False

		current_caid	= data[0]

		available_caids = info.getInfoObject(iServiceInformation.sCAIDs)

		for caid_entry in self.caid_data:
			if caid_entry[3] == request_caid:
				if(request_selected):
					if int(current_caid, 16) >= int(caid_entry[0], 16) and int(current_caid, 16) <= int(caid_entry[1], 16):
						return True
				else: # request available
					try:
						for caid in available_caids:
							if caid >= int(caid_entry[0], 16) and caid <= int(caid_entry[1], 16):
								return True
					except:
						pass

		return False

	boolean = property(getBool)
	
	