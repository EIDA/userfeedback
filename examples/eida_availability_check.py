from obspy import Inventory, UTCDateTime
import json, urllib.request
from obspy.clients.fdsn import Client
import xml.etree.ElementTree as ET

debug = False
channel = 'HHZ'
location = '*'
years = ['2018']
include_restricted = True

token = '/home/fuchs/.eidatoken'

nodes = [{'name': 'ODC', 'stationurl': 'http://www.orfeus-eu.org/fdsnws/station/1/query?', 'dataurl': 'http://www.orfeus-eu.org/fdsnws/dataselect/1/query?', 'wfcurl': 'http://www.orfeus-eu.org/eidaws/wfcatalog/1/query?'},
		 {'name': 'ETH', 'stationurl': 'http://eida.ethz.ch/fdsnws/station/1/query?', 'dataurl': 'http://eida.ethz.ch/fdsnws/dataselect/1/query?', 'wfcurl': 'http://eida.ethz.ch/eidaws/wfcatalog/1/query?'},
		 {'name': 'LMU', 'stationurl': 'http://erde.geophysik.uni-muenchen.de/fdsnws/station/1/query?', 'dataurl': 'http://erde.geophysik.uni-muenchen.de/fdsnws/dataselect/1/query?', 'wfcurl': 'http://erde.geophysik.uni-muenchen.de/eidaws/wfcatalog/1/query?'},
		 {'name': 'BGR', 'stationurl': 'http://eida.bgr.de/fdsnws/station/1/query?', 'dataurl': 'http://eida.bgr.de/fdsnws/dataselect/1/query?', 'wfcurl': 'http://eida.bgr.de/eidaws/wfcatalog/1/query?'},
		 {'name': 'GFZ', 'stationurl': 'http://geofon.gfz-potsdam.de/fdsnws/station/1/query?', 'dataurl': 'http://geofon.gfz-potsdam.de/fdsnws/dataselect/1/query?', 'wfcurl': 'http://geofon.gfz-potsdam.de/eidaws/wfcatalog/1/query?'},
		 {'name': 'RESIF', 'stationurl': 'http://ws.resif.fr/fdsnws/station/1/query?', 'dataurl': '	http://ws.resif.fr/fdsnws/dataselect/1/query?', 'wfcurl': 'http://ws.resif.fr/eidaws/wfcatalog/1/query?'},
		 {'name': 'INGV', 'stationurl': 'http://webservices.ingv.it/fdsnws/station/1/query?', 'dataurl': 'http://webservices.ingv.it/fdsnws/dataselect/1/query?', 'wfcurl': 'http://webservices.ingv.it/eidaws/wfcatalog/1/query?'},
		 {'name': 'NOA', 'stationurl': 'http://eida.gein.noa.gr/fdsnws/station/1/query?', 'dataurl': 'http://eida.gein.noa.gr/fdsnws/dataselect/1/query?', 'wfcurl': 'http://eida.gein.noa.gr/eidaws/wfcatalog/1/query?'},
		 {'name': 'NIEP', 'stationurl': 'http://eida-sc3.infp.ro/fdsnws/station/1/query?', 'dataurl': 'http://eida-sc3.infp.ro/fdsnws/dataselect/1/query?', 'wfcurl': 'http://geofon.gfz-potsdam.de/eidaws/wfcatalog/1/query?'},
		 {'name': 'KOERI', 'stationurl': 'http://eida-service.koeri.boun.edu.tr/fdsnws/station/1/query?', 'dataurl': 'http://eida-service.koeri.boun.edu.tr/fdsnws/dataselect/1/query?', 'wfcurl': 'http://eida-service.koeri.boun.edu.tr/eidaws/wfcatalog/1/query?'}]




print('-----------------------------------------------------')
for year in years :
	resultlist = []
	nowfc_list = []
	start = UTCDateTime(year + '01-01')
	end = UTCDateTime(year + '12-31')
	y1 = str(start.year)
	m1 = str(start.month).rjust(2, '0')
	d1 = str(start.day).rjust(2, '0')

	y2 = str(end.year)
	m2 = str(end.month).rjust(2, '0')
	d2 = str(end.day).rjust(2, '0')
	for node in nodes :
		print('-----------------------------------------------------')
		print('Retrieving stations for node:', node['name'], '...')
		url = node['wfcurl']
		direct = Client(node['name'], debug=debug) #eida_token=token, 
		inv = Inventory()
		inv += direct.get_stations(network='*', station='*', location='*', channel=channel, starttime=start, endtime=end, level='station', includerestricted=include_restricted)
		number_of_stations = 0
		for net in inv :
			number_of_stations += len(net)
		print(node['name'], 'node,', channel, 'channel:', len(inv), 'networks,',  number_of_stations, 'stations')
		print('-----------------------------------------------------')

		for network in inv :
			for station in network :
				try :
					metrics = json.loads(urllib.request.urlopen(url + 'network=' + network.code + '&station=' + station.code + '&channel=' + channel + '&location=' + location + '&include=sample&start=' + y1 + '-' + m1 + '-' + d1 + 'T00:00:00.0000&end=' + y2 + '-' + m2 + '-' + d2 + 'T23:59:59.9999&longestonly=false&minimumlength=0.0').read())
					success = 'yes'
					#print 'Retrieved metrics for', network.code, station.code
				except Exception as e :
					success = 'no'
					print('! NO ! metrics for', year, network.code, station.code)
					resultlist.append([year, node['name'], network.code, station.code, -1])
					nowfc_list.append([year, node['name'], network.code, station.code])
				if success == 'yes' :
					temp = 0
					for entry in metrics :
						temp += entry['percent_availability']
					if station.end_date == None and station.termination_date == None :
						availability = temp / 365.0
					else :
						availability = temp / (station.end_date.julday)
					print(year, node['name'], network.code, station.code, availability)
					resultlist.append([year, node['name'], network.code, station.code, availability])
	print('-----------------------------------------------------')

	f = open('eida_availability_results_' + year + '_' + channel + '.txt','w+')
	for line in resultlist :
		to_write = line[0] + '    ' + line[1] + '    ' + line[2].rjust(5, ' ') + '    ' + line[3].rjust(5, ' ') + '    ' + str(line[4])
		f.write(to_write + '\n')
	f.close()

	fn = open('eida_nowfc_' + year + '_' + channel + '.txt','w+')
	for line in nowfc_list :
		to_write = line[0] + '    ' + line[1] + '    ' + line[2].rjust(5, ' ') + '    ' + line[3].rjust(5, ' ')
		fn.write(to_write + '\n')
	fn.close()
