#generate request module
import re
from os.path import isdir,exists
from obspy.taup.tau import TauPyModel as TPM
from obspy.geodetics.base import locations2degrees as L2D
from modules.base_fun import directory_names, read_json

def generate_request(
      path,
      event,
      inventory,
      semiwindow = 300,
      phaselabel = 'S',
      channel    = 'BH',
      component  = '*'
    ):
  #set up folder names to load the checklist if it exists
  year_dir,event_dir = directory_names(event)
  if exists(path+year_dir+event_dir+'/checklist.json'):
    checklist = read_json(path+year_dir+event_dir+'/checklist.json')
  else:
    checklist = []
  #filter the station list with the checklist
  if component == '*':
    components = ['Z','E','N']
  else:
    components = component
  if not checklist:
    stations_temp = [
      [network.code,
       station.code,
       station.latitude,
       station.longitude] \
      for network in inventory for station in network
    ]
  else:
    stations_temp = [
      [network.code,
       station.code,
       station.latitude,
       station.longitude] \
      for  network in inventory for station in network \
      if not all([[network.code,station.code,comp] in checklist for comp in components])
    ]
  #build the station list
  stations = []
  for station in stations_temp:
    if station not in stations:
      stations.append(station)
  #estimate the arrival times at the stations with TauPy
  theo_travel_times = estimate_tt(stations,event,phaselabel)
  #build the request
  bulk = assemble_bulk(
    stations,
    event.origins[0].time,
    theo_travel_times,
    semiwindow,
    channel,
    components)
  return bulk, semiwindow

def assemble_bulk(stations,source_time,theo_travel_times,semiwindow,channel,components):
  bulk = []
  i = 0
  for station in stations:
    if theo_travel_times[i] != theo_travel_times[i]:
      continue
    phase_arrival = source_time + theo_travel_times[i]
    for component in components:
      bulk.append((
        station[0],
        station[1],
        '*',
        channel+component,
        phase_arrival-semiwindow,
        phase_arrival+semiwindow
      ))
    i += 1
  return bulk

def estimate_tt(stations,event,phaselabel):
  model = TPM(model='ak135')
  theo_travel_times = []
  for station in stations:
    tt = model.get_travel_times(
           source_depth_in_km = \
             event.origins[0].depth/1000 if event.origins[0].depth else 0,
           distance_in_degree = \
             L2D(
               event.origins[0].latitude,
               event.origins[0].longitude,
               station[2],
               station[3]
             ),
           phase_list = phaselabel
         )
    theo_travel_times.append(
      tt[0].time if tt else float('NaN')
    )
  return theo_travel_times
