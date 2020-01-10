#!/usr/local/bin/python
def format_inventory(inventory, services=None):
  networks, stations = {}, {}
  for network in inventory.networks:
    if network.code not in networks:
      networks[network.code] = {
        'description': network.description,
        'status': network.restricted_status,
        'active': {
          'start': {} if network.start_date is None else {
            'year': network.start_date.year,
            'month': network.start_date.month,
            'day': network.start_date.day
          },
          'end': {} if network.end_date is None else {
            'year': network.end_date.year,
            'month': network.end_date.month,
            'day': network.end_date.day
          }
        },
        'services': [] if services is None else list(set([url for urls in services[network.code].values() for url in urls]))
      }
    if network.code not in stations:
      stations[network.code] = {}
    for station in network.stations:
      channels = list(set(map(lambda channel: channel.code, station.channels)))
      if station.code not in stations[network.code]:
        stations[network.code][station.code] = {
          'description': station.site.name,
          'status': station.restricted_status,
          'active': {
            'start': {} if station.start_date is None else {
              'year': station.start_date.year,
              'month': station.start_date.month,
              'day': station.start_date.day
            },
            'end': {} if station.end_date is None else {
              'year': station.end_date.year,
              'month': station.end_date.month,
              'day': station.end_date.day
            }
          },
          'services': [] if services is None else services[network.code][station.code],
          'channels': channels,
          'latitude': station.latitude,
          'longitude': station.longitude,
          'elevation': station.elevation
        }
      else:
        for channel in channels:
          if channel not in stations[network.code][station.code]['channels']:
            stations[network.code][station.code]['channels'].append(channel)
  for code in stations:
    networks[code]['count'] = len(stations[code].keys())
  return networks, stations

