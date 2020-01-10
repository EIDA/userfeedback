#data processing module

def processing(
      waveforms,
      inventory,
      semiwindow    = 300,
      taper         = 0.1,
      sampling_rate = 20,
      filtering     = {'type':'lowpass','freq':5}
    ):
  #check if there is data
#  processing_info = []
  #loop over all waveforms
  i = -1
  print('length waveforms, proc:',len(waveforms))
  for waveform in waveforms:
    try:
      i += 1
      if (waveform.stats.npts >= sampling_rate*semiwindow*2*0.9) and waveform.data[0] == waveform.data[0]:
        #basic processing steps
        waveform \
          .remove_sensitivity(inventory=inventory) \
          .detrend('linear') \
          .remove_response(inventory=inventory) \
          .taper(taper) \
          .filter(**filtering)

        #resampling
        if waveform.stats.sampling_rate != sampling_rate:
          if (waveform.stats.sampling_rate % sampling_rate) == 0:
            waveform.decimate(
              int(waveform.stats.sampling_rate/sampling_rate),
              no_filter=True
            )
          else:
            waveform.resample(
              sampling_rate,
              no_filter=True
            )
    except:
      print('Processing failed!')
      continue
  return sampling_rate
