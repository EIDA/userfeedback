#data archiving module
import time,datetime,re
from os import makedirs
from os.path import isdir, exists
from scipy.io import savemat
from obspy.geodetics.base import gps2dist_azimuth as DAB
from .base_fun import directory_names, read_json, write_json, format_date

def archive_data(
      event,
      request,
      path,
      semiwindow      = 300,
      sampling_rate   = None,
      inventory       = None,
      waveforms       = None,
    ):
  #set up directory names and save paths
  year_dir,event_dir = directory_names(event)
  save_path = path+year_dir+event_dir+'/'
  if not isdir(save_path):
    makedirs(save_path)
  #archive the request with a timestamp
  tim = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
  write_request(request,save_path+'request'+tim+'.txt')
  if waveforms==None:
    return
  #write event info file
  write_event_info(path,save_path,event)
  #load/set-up and fill up checklist
  if exists(save_path+'checklist.json'):
    checklist = read_json(save_path+'checklist.json')
  else:
    checklist = []
  checklist.append(tim)
  if exists(save_path+'fails.json'):
    fails = read_json(save_path+'fails.json')
  else:
    fails = []
  fails.append(tim)
  #archive waveform data
  i = -1
  for waveform in waveforms:
    i += 1
    if waveform.data[0] != waveform.data[0]:
      fails.append([waveform.stats['network'],waveform.stats['station'],waveform.stats.channel[-1],'response'])
      continue
    elif waveform.stats.npts < sampling_rate*semiwindow*2*0.9:
      fails.append([waveform.stats['network'],waveform.stats['station'],waveform.stats.channel[-1],'short'])
      continue
    write_station_info(inventory,waveform,save_path,event)
    write_data(waveform,save_path)
    checklist.append([waveform.stats['network'],waveform.stats['station'],waveform.stats.channel[-1]])
  #write completed checklist
  write_json(checklist,save_path+'checklist.json')
  write_json(fails,save_path+'fails.json')
  return

def get_station_coordinates(inventory,waveform):
  latitude, longitude, elevation = [
    inventory.get_coordinates(
      waveform.stats.network+'.'
      +waveform.stats.station+'.'
      +waveform.stats.location+'.'
      +waveform.stats.channel
    )[key] for key in ['latitude','longitude','elevation']
  ]
  return latitude, longitude, elevation

def write_data(wf,save_path):
  WF = {
    'network'       : wf.stats.network,
    'mseed'         : str(wf.stats.mseed),
    'npts'          : str(wf.stats.npts),
    'station'       : wf.stats.station ,
    'location'      : wf.stats.location ,
    'starttime'     : str(wf.stats.starttime),
    'delta'         : str(wf.stats.delta),
    'calib'         : str(wf.stats.calib),
    'sampling_rate' : str(wf.stats.sampling_rate),
    'endtime'       : str(wf.stats.endtime),
    'data'          : wf.data,
    'response'      : '',
    'channel'       : wf.stats.channel
  }
  filename = (
    wf.stats.network+'.'
    +wf.stats.station+'.'
    +wf.stats.channel+'_VEL_'
    +re.sub('\.\d{4,8}Z','',str(wf.stats.starttime).replace('T','.').replace(':','-'))+'_'
    +re.sub('\.\d{1,5}','',str(wf.stats.npts/wf.stats.sampling_rate))
    +'.mat'
  )
  savemat(save_path+'/'+filename,WF)
  return

def write_event_info(main_dir,save_path,event):
  line = (
    str(event.origins[0].latitude)+'\t'
    +str(event.origins[0].longitude)+'\t'
    +str(event.origins[0].depth)+'\t'
    +str(event.magnitudes[0].mag)+'\t'
    +re.sub('\d{2}\.\d{4,8}','',format_date(event.origins[0].time))+'\t'
    +re.sub('\d{8}T','',format_date(event.origins[0].time))+'\n'
  )
  filename = (
    save_path
    +'/event_infos_'
    +re.sub('\d{2}\.\d{4,8}','',format_date(event.origins[0].time))
    +'.txt'
  )
  with open(filename,'w+') as file:
    file.write(line)
  line = re.sub('\d{2}\.\d{4,8}','',format_date(event.origins[0].time))+'\n'
  with open(main_dir+'/eventlist.txt','a+') as file:
    file.write(line)
  return

def write_station_info(inventory,waveform,save_path,event):
  latitude, longitude, elevation = get_station_coordinates(inventory,waveform)
  dist_meters, azimuth, backazimuth = \
    DAB(
      event.origins[0].latitude,
      event.origins[0].longitude,
      latitude,
      longitude
    )
  line = (
    waveform.stats.station+'\t'
    +str(latitude)+'\t'
    +str(longitude)+'\t'
    +str(dist_meters)+'\t'
    +str(azimuth)+'\t'
    +str(backazimuth)+'\t'
    +waveform.stats.channel[-1]+'\t'
    +re.sub('\d{2}\.\d{4,8}Z','',format_date(event.origins[0].time))+'\t'
    +str(waveform.stats.starttime - event.origins[0].time)+'\n'
  )
  filename = (
    save_path
    +'/station_infos_'
    +re.sub('\d{2}\.\d{4,8}','',format_date(event.origins[0].time))
    +'.txt'
  )
  with open(filename,'a+') as file:
    file.write(line)
  return

def write_request(request,filename):
  lines = ''
  for req in request:
    lines += '\n'
    for r in req:
      lines += str(r)+' '
  with open(filename,'w') as file:
    file.write(lines[1:-1])
  return
