import requests
import json


class WGDC:
    def __init__(self, prom_url, prom_query, geo_api_url):
        self.result = []
        self.prometheus_url = prom_url
        self.prometheus_query = prom_query
        self.geo_api_url = geo_api_url

    def fetch(self):
        j = json.loads(requests.get(self.prometheus_url + "/api/v1/query", 
                                    params=self.prometheus_query).text)

        result = []

        for d in j['data']['result']:
            if int(d['value'][1]) == 0:
                d['metric']['endpoint'] = '0.0.0.0'
                d['ext_metric'] = {'lat': 0, 'long': '0', 'isp': 'none'}
            else:
                d['ext_metric'] = self._lookup_geodata(str(d['metric']['endpoint']).split(':')[0])
            result.append(
                {
                    'endpoint': str(d['metric']['endpoint']).split(':')[0], # we only need the IP, not the source port
                    'public_key': d['metric']['public_key'],
                    'online_state': d['value'][1],
                    'lat': str(d['ext_metric']['lat']),
                    'long': str(d['ext_metric']['long']),
                    'isp': str(d['ext_metric']['isp'])
                }
            )
        self.result = result

    def _lookup_geodata(self, endpoint):
        j = json.loads(requests.get(self.geo_api_url + '/' + endpoint).text)
        result = {'lat': j['latitude'], 'long': j['longitude'], 'isp': j['isp']}
        return(result)