from obspy import UTCDateTime, Stream
from obspy.clients.fdsn import Client, RoutingClient
import random
import os
import numpy as np
from tqdm import tqdm

token = os.path.expanduser('~/.eidatoken') # path to personal eida token here

# the purpose of a hacked-in node list is to avoid any potential routing issues
nodes = [{'name': 'ODC', 'stationurl': 'http://www.orfeus-eu.org/fdsnws/station/1/query?', 'dataurl': 'http://www.orfeus-eu.org/fdsnws/dataselect/1/query?', 'wfcurl': 'http://www.orfeus-eu.org/eidaws/wfcatalog/1/query?'},
		 {'name': 'ETH', 'stationurl': 'http://eida.ethz.ch/fdsnws/station/1/query?', 'dataurl': 'http://eida.ethz.ch/fdsnws/dataselect/1/query?', 'wfcurl': 'http://eida.ethz.ch/eidaws/wfcatalog/1/query?'},
		 {'name': 'LMU', 'stationurl': 'http://erde.geophysik.uni-muenchen.de/fdsnws/station/1/query?', 'dataurl': 'http://erde.geophysik.uni-muenchen.de/fdsnws/dataselect/1/query?', 'wfcurl': 'http://erde.geophysik.uni-muenchen.de/eidaws/wfcatalog/1/query?'},
		 {'name': 'BGR', 'stationurl': 'http://eida.bgr.de/fdsnws/station/1/query?', 'dataurl': 'http://eida.bgr.de/fdsnws/dataselect/1/query?', 'wfcurl': 'http://eida.bgr.de/eidaws/wfcatalog/1/query?'},
		 {'name': 'GFZ', 'stationurl': 'http://geofon.gfz-potsdam.de/fdsnws/station/1/query?', 'dataurl': 'http://geofon.gfz-potsdam.de/fdsnws/dataselect/1/query?', 'wfcurl': 'http://geofon.gfz-potsdam.de/eidaws/wfcatalog/1/query?'},
		 {'name': 'RESIF', 'stationurl': 'http://ws.resif.fr/fdsnws/station/1/query?', 'dataurl': '	http://ws.resif.fr/fdsnws/dataselect/1/query?', 'wfcurl': 'http://ws.resif.fr/eidaws/wfcatalog/1/query?'},
		 {'name': 'INGV', 'stationurl': 'http://webservices.ingv.it/fdsnws/station/1/query?', 'dataurl': 'http://webservices.ingv.it/fdsnws/dataselect/1/query?', 'wfcurl': 'http://webservices.ingv.it/eidaws/wfcatalog/1/query?'},
		 {'name': 'NOA', 'stationurl': 'http://eida.gein.noa.gr/fdsnws/station/1/query?', 'dataurl': 'http://eida.gein.noa.gr/fdsnws/dataselect/1/query?', 'wfcurl': 'http://eida.gein.noa.gr/eidaws/wfcatalog/1/query?'},
		 {'name': 'NIEP', 'stationurl': 'http://eida-sc3.infp.ro/fdsnws/station/1/query?', 'dataurl': 'http://eida-sc3.infp.ro/fdsnws/dataselect/1/query?', 'wfcurl': 'http://eida-sc3.infp.ro/eidaws/wfcatalog/alpha/'},
		 {'name': 'KOERI', 'stationurl': 'http://eida-service.koeri.boun.edu.tr/fdsnws/station/1/query?', 'dataurl': 'http://eida-service.koeri.boun.edu.tr/fdsnws/dataselect/1/query?', 'wfcurl': 'http://eida-service.koeri.boun.edu.tr/eidaws/wfcatalog/1/query?'}]

path = '.' # where to look for stationlist file and where to store results file

years = ['2017'] # put as many years here as wanted
channels = ['BHZ'] # list here the channels wanted

days_to_sample = 2 # < 366; how many days to pick random samples from
hours_to_sample = 5 # < 24; how many hours to randomly sample in each day
sample_length = 10 # in minutes!; length of each individual download request in minutes
runs = 1 # repeat the procedure X times

for year in years :
	for channel in channels :
		downloaded = []
		
		# read stationlist file
		stationfile =  open(os.path.join(path, 'stationlist_downloadtest_' + year + '_' + channel + '.txt'), 'r')
		stationfile_output_raw = stationfile.readlines()
		stationfile.close()
		stationfile_output = [(entry.rstrip('\n')).split() for entry in stationfile_output_raw] # make it look nice

		nodename = nodes[0]['name'] # initiate first fdsnws connection
		fdsn = Client(nodename, debug=False, eida_token=token)

		for entry in stationfile_output : # loop trough all stations in stationlist
			new_nodename = entry[1]
			if nodename != new_nodename : # check if new fdsnws connection needs to be established
				nodename = new_nodename
				print('Initiating new FDSNWS connection to node:', nodename)
				try :
					fdsn = RoutingClient('eida-routing', timeout=15, credentials={'EIDA_TOKEN': token})
				except Exception as e:
					fdsn = Client(nodename, timeout=15, debug=False, eida_token=token)
			network = entry[2]
			station = entry[3]
			print(year, channel, nodename, network, station)

			completeness = []

			data = Stream()
			for i in np.arange(runs) :
				days = random.sample(range(1, 366), days_to_sample)
				hours = random.sample(range(0, 24), hours_to_sample) # create random set of hours and days for download test
				hours_with_data = 0

				for day in tqdm(days) : #  loop through all the random days
					for hour in hours : # loop through all the random hours (same for each day)
						start = UTCDateTime(year + '-' + str(day).rjust(3, '0') + 'T' + str(hour).rjust(2, '0') + '-:00:00.00')
						end = start + (sample_length * 60)
						try :
							data_temp = fdsn.get_waveforms(network=network, station=station, location='*', channel=channel, starttime=start, endtime=end) # get the data
							data_temp.trim(starttime=start, endtime=end)
							data += data_temp
							
							data_exists = 'yes'
							hours_with_data += 1
						except Exception as e :
							#print(year, channel, nodename, network, station, day, hour, e)
							#print('----------------------------')
							data_exists = 'no'

			full_time = runs * days_to_sample * hours_to_sample * sample_length * 60

			if hours_with_data > 0 : # check how much data was downloaded
				#print(data)

				locs = []
				for tr in data :
					locs.append(tr.stats.location)

				locs = list(set(locs))
				if len(locs) > 1 :
					completeness_by_loc =[[], [], []]
					for loc in locs :
						data_temp = data.copy().select(location=loc)
						total_time_covered = 0
						for tr in data_temp :
							time_covered = tr.stats.endtime - tr.stats.starttime
							total_time_covered += time_covered

						percentage_covered = total_time_covered / full_time
						completeness_by_loc[0].append(loc)
						completeness_by_loc[1].append(total_time_covered)
						completeness_by_loc[2].append(percentage_covered)
					percentage_covered = max(completeness_by_loc[2])
					total_time_covered = max(completeness_by_loc[1])

				else :
					total_time_covered = 0
					for tr in data :
						time_covered = tr.stats.endtime - tr.stats.starttime
						total_time_covered += time_covered

					percentage_covered = total_time_covered / full_time

			else :
				total_time_covered = 0.0
				percentage_covered = 0.0

			print('Minutes received:', int(total_time_covered/60.0), ' - Minutes requested:', int(full_time/60.0), ' - Percent received:', str(percentage_covered * 100)[:5])
			downloaded.append([year, nodename, network, station, percentage_covered * 100])

		f = open('eida_downloadtest_results_' + year + '_' + channel + '.txt','w+')
		for line in downloaded :
			to_write = line[0] + '    ' + line[1] + '    ' + line[2].rjust(5, ' ') + '    ' + line[3].rjust(5, ' ') + '    ' + str(line[4])
			f.write(to_write + '\n')
		f.close()
