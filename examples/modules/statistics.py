# import sys
# from obspy import Stream
# from numpy import arange
from .format_inventory import *

def statistics(output, requests, waveforms, node_url, inventory):
  _, inventory = format_inventory(inventory)
  for request in requests:
    network = request[0]
    station = request[1]
    key = (network, station)
    if (key) not in output:
      output[key] = {
        'longitude'       : inventory[network][station]['longitude'],
        'latitude'        : inventory[network][station]['latitude'],
        'downloaded_frac' : 0,
        'processed_frac'  : 0,
        'requested_count' : 0,
        'downloaded_count': 0,
        'processed_count' : 0,
        'url'             : node_url
      }
    output[key]['requested_count'] += 1
    if key in [(waveform.stats.network, waveform.stats.station) for waveform in waveforms]:
      output[key]['downloaded_count'] += 1
    for waveform in waveforms:
      if key == (waveform.stats.network, waveform.stats.station) and waveform.data[0] == waveform.data[0]:
        output[key]['processed_count'] += 1
        break
    output[key]['downloaded_frac'] = \
      output[key]['downloaded_count'] \
      / output[key]['requested_count']
    output[key]['processed_frac'] = \
      output[key]['processed_count'] \
      / output[key]['requested_count']
  return output
