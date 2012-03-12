# Original By Pli
# Hacked by meo for BP

import os

ECM_INFO = '/tmp/ecm.info'

old_ecm_mtime = None
data = None

class GetEcmInfo:
	def getEcmData(self):
		global old_ecm_mtime
		global data
		try:
			ecm_mtime = os.stat(ECM_INFO).st_mtime
		except:
			ecm_mtime = None
		if ecm_mtime != old_ecm_mtime:
			old_ecm_mtime = ecm_mtime
			data = self.getText()
		if data == None:
			return '','0','0','0','',''
		return data

	def getText(self):
		try:
			ecm = open(ECM_INFO, 'rb').readlines()
			bp_inuse_info = "Fta"
			info = {}
			for line in ecm:
				d = line.split(':', 1)
				if len(d) > 1:
					info[d[0].strip()] = d[1].strip()
			# info is dictionary
			using = info.get('using', '')
			decode = info.get('decode', '')
			source = info.get('source', '')
			reader = info.get('reader', '')
			
			if using:
				# CCcam
				hops = info.get('hops', '0')
				self.textvalue = "Address:" + info.get('address', 'Unknown') + "   Hops:" + hops + "   Ecm time:" + " %ss" % info.get('ecm time', '?')
				if using == 'fta':
					self.textvalue = ""
					bp_inuse_info = "Fta"
				elif using == 'emu':
					bp_inuse_info = "Emulator"
				else:
					bp_inuse_info = "Network"
				if using == 'sci':
					bp_inuse_info = "Card"
		

			elif decode:
				# gbox (untested)
				if info['decode'].find('Internal') != -1:
					bp_inuse_info = "Emulator"
				if info['decode'].find('slot') != -1:
					bp_inuse_info = "Card"
				if info['decode'] == 'Network':
					bp_inuse_info = "Network"
					cardid = 'id:' + info.get('prov', '')
					try:
						share = open('/tmp/share.info', 'rb').readlines()
						for line in share:
							if cardid in line:
								self.textvalue = line.strip()
								break
							else:
								self.textvalue = cardid
					except:
						self.textvalue = decode
				else:
						self.textvalue = decode
						
			elif source:
				# MGcam
				if info['source'].find('emu') != -1:
					bp_inuse_info = "Emulator"
				elif info['source'].find('sci') != -1:
					bp_inuse_info ="Card"
				elif info['source'].find('fta') != -1:
					bp_inuse_info ="Fta"
				else:
					bp_inuse_info ="Network"
				eEnc  = ""
				eCaid = ""
				eSrc = ""
				eTime = ""
				for line in ecm:
					line = line.strip() 
					if line.find('ECM') != -1:
						line = line.split(' ')
						eEnc = line[1]
						eCaid = line[5][2:-1]
						continue
					if line.find('source') != -1:
						line = line.split(' ')
						eSrc = line[4][:-1]
						continue
					if line.find('msec') != -1:
						line = line.split(' ')
						eTime = line[0]
						continue
							
				self.textvalue = "(%s %s %.3f @ %s)" % (eEnc,eCaid,(float(eTime)/1000),eSrc)
				
			elif reader:
				bp_inuse_info ="Card"
				hops = info.get('hops', '0')
				address = info.get('from', 'unknown')
				pos = address.find('.')
				if pos > 1:
					bp_inuse_info = "Network"
				self.textvalue = "Address:" + address + "   Hops:" + hops + "   Ecm time:" + " %ss" % info.get('ecm time', '?')
			else:
				self.textvalue = ""
					
			decCI = info.get('caid', '0')
			provid = info.get('provid', '0')
			if provid == '0':
				provid = info.get('prov', '0')
			ecmpid = info.get('pid', '0')
			provider = info.get('provider', ' ')
			if provider == " ":
				provider = info.get('prov', ' ')
			bp_ecminfo = "CaId: " + decCI + "    Provider: " + provider
			if decCI == "0x000" or decCI == "0":
				bp_ecminfo = ""
		except:
			ecm = None
			self.textvalue = ""
			decCI='0'
			provid='0'
			ecmpid='0'
			bp_ecminfo = ""
			bp_inuse_info = ""
		return self.textvalue,decCI,provid,ecmpid,bp_ecminfo,bp_inuse_info
