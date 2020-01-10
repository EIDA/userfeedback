# example download application
import sys
import os
import time
from obspy                             import UTCDateTime
from obspy.clients.fdsn                import Client
from .modules.processing                import processing
from .modules.statistics                import statistics
# from .modules.archive_data              import archive_data
from .modules.generate_request          import generate_request
from .modules.execute_download          import execute_download
from .modules.generate_metadata_noroute import generate_metadata

main_data_directory = './data_test/'                         # path to directory where the data shall be saved
node_urls = [
    'http://ws.ipgp.fr',
    'http://ws.resif.fr',
    'http://eida.ethz.ch',
    'http://webservices.ingv.it',
    'http://rdsa.knmi.nl',
    'http://www.seismicportal.eu',
    'http://eida.koeri.boun.edu.tr',
    'http://erde.geophysik.uni-muenchen.de',
    'http://geofon.gfz-potsdam.de',
    'http://eida.bgr.de',
    'http://eida.gein.noa.gr',
    'http://eida-sc3.infp.ro',
    'http://www.orfeus-eu.org',
    'http://ws.icgc.cat'
]
output = {}
for node_url in node_urls:
    try:
        # path to personal eida token here
        client = Client(
                   node_url,
                   eida_token=os.path.expanduser('~/.eidatoken')
                 )
    except Exception:
        client = Client(node_url)

    catalog, inventory, channel, component = \
        generate_metadata(
            starttime      = UTCDateTime(2018, 4,  2,  0,  0,  0),
            endtime        = UTCDateTime(2018, 4,  2, 23, 59, 59),
            station_region = [45, 10, 30],                         # this defines a circular region of interest, stations outside will not be downloaded
            min_magnitude  = 6,
            channel        = 'HH',                                 # if you want HH and BH data (both or either), you will need to run this script twice
            component      = '*',                                  # component can be 'Z', 'E', 'N' or '*' for all three
            level          = 'response',
            catalog_serv   = 'ISC',                                # service provider for the event catalog
            client         = client
        )
    tim = time.time()
    for event in catalog:
        print(node_url)
        print(time.time() - tim)
        tim = time.time()
        print(event)
        request, semiwindow = \
            generate_request(
                path       = main_data_directory,
                event      = event,
                inventory  = inventory,
                semiwindow = 300,                                    # the total window is twice this, and it is centered on the TauPy-Arrival of the chosen phase
                phaselabel = 'S',
                channel    = channel,
                component  = component
            )
        if request:
            waveforms = execute_download(client, request)
            if waveforms:
                sampling_rate = \
                    processing(
                        waveforms     = waveforms,
                        inventory     = inventory,
                        taper         = 0.1,                               # length of the taper as a fraction of the total waveform length
                        sampling_rate = 20,                                # target sampling rate
                        filtering     = {'type': 'lowpass',                # filtering type (see https://docs.obspy.org/packages/autogen/obspy.core.stream.Stream.filter.html)
                                         'freq': 5         }               # corner frequency for filtering
                    )
            output = statistics(
                output = output,
                requests = request,
                waveforms = waveforms,
                node_url = node_url,
                inventory = inventory
            )
        else:
            print('No Request.')

output_formatted = []
for (key, value) in output.items():
    values = list(map(str, value.values()))
    output_formatted.append(values + list(key))
with open('statistics.txt', 'w') as file:
    file.write('\n'.join(map(lambda line: ' '.join(line), output_formatted)))
