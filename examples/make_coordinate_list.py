from obspy.clients.fdsn import Client
from obspy import UTCDateTime

def extract_station_coordinates(station_dictionary, save_path):
  output = open(save_path,'w')
  for network in station_dictionary:
    for station in station_dictionary[network]:
      output.write("%s %s %s %s\n" % (
        station_dictionary[network][station]["longitude"],
        station_dictionary[network][station]["latitude"],
        station_dictionary[network][station]["elevation"],
        station
        )
      )

def append_dictionary(station_dictionary, inv, service):
  for network in inv:
    if network.code not in station_dictionary:
      station_dictionary[network.code] = {}
    for station in network:
      if station.code not in station_dictionary[network.code]:
        station_dictionary[network.code][station.code] = {
          "latitude" : station.latitude,
          "longitude" : station.longitude,
          "elevation" : station.elevation,
        }

EIDA_nodes = [ "ODC", "GFZ", "RESIF", "INGV", "ETH", "BGR", "NIEP", "KOERI", "LMU", "NOA", "ICGC" ]
station_dictionary = {}
output_text = []
start_year = UTCDateTime(2020,1,1)
end_year = UTCDateTime(2020,12,31)
for node in EIDA_nodes:
  inv = Client(node).get_stations(
    channel = '*HZ',
    starttime = start_year,
    endtime = end_year,
    level = 'station',
  )
  append_dictionary(station_dictionary,inv, node)
extract_station_coordinates(station_dictionary, 'new_coordinates.xy')

