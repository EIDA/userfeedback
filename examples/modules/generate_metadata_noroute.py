#generate metadata module
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.core.inventory import Inventory

def generate_metadata(
      client,
      starttime,
      endtime,
      station_region = None,
      min_magnitude  = None,
      channel        = 'BH',
      component      = '*',
      level          = 'response',
      catalog_serv   = 'ISC'
    ):
  #download catalog
  catalog = Client(catalog_serv).get_events(
              starttime    = starttime,
              endtime      = endtime,
              minmagnitude = min_magnitude
            )
  #download inventory
  inventory = Inventory()
  try:
    result = client.get_stations(
      starttime         = starttime,
      endtime           = endtime,
      latitude          = station_region[0],
      longitude         = station_region[1],
      maxradius         = station_region[2],
      channel           = channel+component,
      level             = level,
      includerestricted = True
    )
    inventory += result
  except:
    pass
  return catalog, inventory, channel, component
