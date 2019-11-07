import json
import os
from configparser import ConfigParser

import cchardet
import zerorpc


class API():
    def __init__(self):
        self.config = ConfigParser()

    def save(self, items):
        for value in items.values():
            if value is None or value == '':
                raise ValueError('遺失參數')
            setting = {
                'engine': items['engine'],
                'converter': items['converter'],
                'format': items['format'],
                'loglevel': items['loglevel'],
                'syslevel': items['syslevel']
            }
            other = {
                'file_check': items['file_check'],
                'enable_pause': items['enable_pause']
            }
            try:
                # path = os.path.abspath(os.path.dirname(os.getcwd()))
                with open('config.ini', 'w', encoding='utf-8') as fw:
                    fw.write(f'[setting]\n')
                    for key in setting.keys():
                        fw.write(f'{key}={setting[key]}\n')
                    fw.write(f'[other]\n')
                    for key in other.keys():
                        fw.write(f'{key}={other[key]}\n')
            except Exception as e:
                raise e

    def load(self):
        # path = os.path.abspath(os.path.dirname(os.getcwd()))
        if os.path.exists('config.ini'):
            self.config.read('config.ini', encoding=coding('config.ini'))
            items = json.loads('{"engine": "%(engine)s", "converter": "%(converter)s","format": "%(format)s","loglevel": "%(loglevel)s","syslevel": "%(syslevel)s"}' % self.config['setting'])
            items.update(json.loads('{"file_check": "%(file_check)s", "enable_pause": "%(enable_pause)s"}' % self.config['other']))
            return items
        else:
            return None
            
    def status(self):
        return 'zerorpc running.'

def coding(file):
    if os.path.exists(file):
        with open(file, 'rb') as _f:
            result = cchardet.detect(_f.read())
            return result['encoding']
    return None


if __name__ == '__main__':
    server = zerorpc.Server(API())
    server.bind("tcp://0.0.0.0:4242")
    server.run()
