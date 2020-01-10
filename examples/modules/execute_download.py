# execute download

import sys
from obspy import Stream
from numpy import arange

def execute_download(client,request):
  waveforms = Stream()
  len_request = len(request)
  max_request = 200
  ind_request = list(zip(list(arange(0,len_request,max_request)),list(arange(max_request,len_request,max_request))+[len_request]))
  for ind in ind_request:
    try:
      # FIXME Do not allow bulk requests! Change for something else
      waveforms += client.get_waveforms_bulk(request[ind[0]:ind[1]])
    except:
      print(sys.exc_info())
      continue
  return waveforms
