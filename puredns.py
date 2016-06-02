import os
import re
from optparse import OptionParser
from urllib import request
from urllib.error import URLError


def parse_host_to_dict():
    TAG_START = 'Modified hosts start'
    TAG_START_EACH = 'Start'
    TAG_END_EACH = 'End'
    HOST_URL = 'https://raw.githubusercontent.com/racaljk/hosts/master/hosts'

    filename = 'hosts'

    try:
        print('Downloading Hosts...')
        response = request.urlopen(HOST_URL)
        file = response.read().decode('utf8')
        with open(filename, 'w+') as hosts:
            hosts.write(file)
        print('Cached to ' + os.getcwd() + os.sep + filename)
    except URLError as e:
        print('Cannot Access Internet, Using Cached Hosts')

    hosts_dict = {}

    with open(filename, 'r') as hosts:
        hosts = hosts.readlines()
        start = False
        new_host = False
        host_set = ''
        host_dict = {}
        for host in hosts:
            if not start and TAG_START.upper() in host.upper():
                start = True
            elif start:
                if host.strip().startswith('#') and TAG_START_EACH.upper() in host.upper():
                    new_host = True
                    host_set = host[host.index('#') + 2: host.rindex('a') - 2]
                    hosts_dict[host_set] = {}
                elif host.strip().startswith('#') and TAG_END_EACH.upper() in host.upper():
                    new_host = False
                elif new_host and not host.strip().startswith('#'):
                    host_map = host[:-1].split('\t')
                    if len(host_map) == 2:
                        host_dict[host_map[1]] = host_map[0]
                        hosts_dict[host_set].update(host_dict)
                    elif len(host_map[0]) != 0:
                        address_p = re.compile(r'\d{1,4}.\d{1,4}.\d{1,4}.\d{1,4}')
                        address_out = address_p.findall(host[:-1])
                        if len(address_out) == 1:
                            address = address_out[0]
                        name_p = re.compile(r'\S*')
                        name_out = name_p.findall(host[:-1])
                        for n in name_out:
                            if n == address or len(n) == 0:
                                pass
                            else:
                                name = n
                                break
                        host_dict[name] = address
                    else:
                        print(host)
                else:
                    if start and not host.strip().startswith('#'):
                        host_set = 'Other'
                        host_dict = {}
                        address_p = re.compile(r'\d{1,4}.\d{1,4}.\d{1,4}.\d{1,4}')
                        address_out = address_p.findall(host[:-1])
                        address = None
                        name = None
                        if len(address_out) == 1:
                            address = address_out[0]
                        name_p = re.compile(r'\S*')
                        name_out = name_p.findall(host[:-1])
                        for n in name_out:
                            if address is not None and n == address or len(n) == 0:
                                pass
                            else:
                                name = n
                                break
                        if name is not None and address is not None:
                            host_dict[name] = address
                            if host_set not in hosts_dict.keys():
                                hosts_dict[host_set] = {}
                            else:
                                hosts_dict[host_set].update(host_dict)
                        else:
                            pass
                    else:
                        pass
            else:
                pass
            host_dict = {}

    return hosts_dict


class DNSWriter(object):
    def __init__(self):
        self.prefix = 'write_to_'

    def write(self, dns_dict, option_type):
        if hasattr(self, self.prefix + option_type):
            writer = getattr(self, self.prefix + option_type)
            writer(dns_dict)
        else:
            print(option_type, 'not implemented yet')

    def write_to_dnsmasq(self, dns_dict):
        file_name = 'dnsmasq.conf'
        with open(file_name, 'w+') as file:
            for hosts in dns_dict.keys():
                hostd = dns_dict[hosts]
                start = False
                for name in hostd.keys():
                    address = hostd[name]
                    if not start:
                        file.write('# ' + hosts + ' Start\n')
                        start = True
                    file.write('address=/' + name + '/' + address + '\n')
                file.write('# ' + hosts + ' End\n')
                file.write('\n')
                file.write('\n')


def main(option_type):
    hosts_dict = parse_host_to_dict()
    writer = DNSWriter()
    writer.write(hosts_dict, option_type)


if __name__ == '__main__':
    type_set = ['dnsmasq']
    type_default = type_set[0]
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-t", "--type",
                      help="choose type of dns configure(default is " + type_default + "): " + str(type_set) + "")
    (options, args) = parser.parse_args()
    option_type = options.type
    if option_type is not None and option_type in type_set:
        main(option_type)
    elif option_type is None:
        main(type_default)
    else:
        parser.print_help()
