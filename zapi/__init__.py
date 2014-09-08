from pyzabbix import ZabbixAPI, ZabbixAPIException
import json
import getpass
import sys


class Cache:
    def __init__(self, cachefile):
        self.cachefile = cachefile

    def get(self, host):
        try:
            with open(self.cachefile,'r') as f:
                token_data = json.loads(f.read())
                try:
                    token = token_data.get(host, None)
                except AttributeError:
                    token = None
                return token
        except IOError:
            return None
    def write(self, host, token):
        with open(self.cachefile,'w') as f:
            token_data = f.read()
            try:
                token_data[host] = token
            except TypeError: 
                token_data = { host: token }
            f.write(json.dumps(token_data))

def authenticate(zapi):
    # Prompt for username and password
    username = raw_input('Username[{0}]:'.format(getpass.getuser())) or getpass.getuser()
    password = getpass.getpass()

    # Login to the Zabbix API
    try:
        zapi.login(username, password)
    except Exception as e:
        if e.__class__.__name__ == 'HTTPError' and e.response.status_code == 404:
            try:
                zapi = ZabbixAPI(c.url + '/zabbix')
                zapi.session.verify = False
                zapi.login(username, password)
            except Exception as e:
                if e.__class__.__name__ == 'HTTPError' and e.response.status_code == 404:
                    print("Invalid API url")
                    exit(1)
                raise
        else:
            raise
    return zapi.auth

def main():

    zapi = ZabbixAPI('https://zabbix.dev.ord1.us.ci.rackspace.net/zabbix')
    zapi.session.verify = False

    c = Cache('/tmp/zabbix.cache')
    token = c.get(sys.argv[1])
    if token:
        zapi.auth = token
        try:
            test = zapi.apiinfo.version()
        except ZabbixAPIException as e:
            if 'Not authorized' in str(e):
                token = authenticate(zapi)
                c.write(sys.argv[1],token)
            else:
                print e
    else:
        token = authenticate(zapi)
        c.write(sys.argv[1], token)

if __name__ == '__main__':
    main()
