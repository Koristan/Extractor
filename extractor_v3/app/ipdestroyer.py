import requests
import json
import os
from bs4 import BeautifulSoup
import logging


executes = ( #Исключения для айпишников
    'ip'
)
# Логер
stream_handler = logging.StreamHandler()
logging.basicConfig(format='%(asctime)s, %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.WARNING,
    filemode='a'
    )
loger = logging.getLogger(__name__)
loger.addHandler(stream_handler)


class IpDestroyer():
    def __init__(self, apikey='key', url='url') -> None:
        self.apikey = apikey
        self.url = url

    def parse(self):
        r = requests.get(self.url, verify=False)
        banned_domains = list()
        soup = self.getSoup(r.text)

        for row in soup.find_all('tr'):

            ok = False

            try:
                ip = row.prettify().split('<td>')[12]
                ok = True
            except Exception as e:
                ok = False

            
            if ok:
                ip = ip.replace(' ', '')
                ip = ip.split('\n')
                true_ip = ''
                for ip_row in ip:
                    try:
                        if ip_row[0].isnumeric():
                            true_ip = ip_row

                            url = 'https://api.abuseipdb.com/api/v2/check'

                            querystring = {
                                'ipAddress': true_ip,
                                'maxAgeInDays': '90'
                            }

                            headers = {
                                'Accept': 'application/json',
                                'Key': self.apikey
                            }

                            response = requests.request(method='GET', url=url, headers=headers, params=querystring)

                            # Formatted output
                            decodedResponse = json.loads(response.text)

                            if(decodedResponse['data']['abuseConfidenceScore'] > 30 and decodedResponse['data']['isp'] != 'Yandex LLC'):
                                
                                isour = False
                                for i in executes:
                                    if decodedResponse['data']['ipAddress'] == i:
                                        isour = True
                                
                                if isour == False:
                                    os.system(f'f2b-remote --subnet --ip {decodedResponse["data"]["ipAddress"]}')
                                    loger.warning(f'{decodedResponse["data"]["ipAddress"]} DESTROYED!')
                                    banned_domains.append(decodedResponse['data']['ipAddress'])
                                    with open('/srv/extractor_v3/logs/txt2.json', 'w') as f:   
                                        print(decodedResponse, file=f)

                            break
                    except Exception as e:
                        pass

    def getSoup(self, html):
        soup = BeautifulSoup (html, 'html.parser')
        return soup
