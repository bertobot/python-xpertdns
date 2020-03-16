from bs4 import BeautifulSoup

import json
import re
import requests


class Record(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = kwargs.get('type', 'A')
        self.address = kwargs.get('address')
        self.distance = kwargs.get('distance')
        self.weight = kwargs.get('weight')
        self.port = kwargs.get('port')
        self.caa_flag = kwargs.get('caa_flag')
        self.caa_tag = kwargs.get('caa_tag')
        self.dyndns = kwargs.get('dyndns')
        self.ttl = kwargs.get('ttl', 3600)
        self.record_id = kwargs.get('record_id')

    def __str__(self):
        return f'record_id: {self.record_id}, name: {self.name}, type: {self.type}, ttl: {self.ttl}, address: {self.address}, distance: {self.distance}, weight: {self.weight}, port: {self.port}, caa_flag: {self.caa_flag}, caa_tag: {self.caa_tag}, dyndns: {self.dyndns}'

    def as_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'address': self.address,
            'distance': self.distance,
            'weight': self.weight,
            'port': self.port,
            'caa_flag': self.caa_flag,
            'caa_tag': self.caa_tag,
            'dyndns': self.dyndns,
            'ttl': self.ttl,
            'record_id': self.record_id,
        }


class Domain(object):
        def __init__(self, **kwargs):
            self.domain = kwargs.get('domain')
            self.slave = kwargs.get('slave')
            self.status = kwargs.get('status')
            self.owner = kwargs.get('owner')
            self.group_owner = kwargs.get('group_owner')
            self.domain_id = kwargs.get('domain_id')
            self.records = []

            self.__baseurl = kwargs.get('baseurl', 'https://www.xpertdns.com/admin/index.php')
            self.__session = kwargs.get('session')

            self.__parse_records(self.domain)

        def __parse_records(self, domain: str):
            r = self.__session.get(self.__baseurl, params={
                'state': 'logged_in',
                'mode': 'records',
                'domain': domain,
            })
            r.raise_for_status()

            first = True
            soup = BeautifulSoup(r.text, 'html.parser')
            for tr in soup.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) != 11:
                    continue

                if first:
                    first = False
                    continue

                self.records.append(Record(
                    name=tds[0].text,
                    type=tds[1].text.strip(),
                    address=tds[2].text.strip(),
                    distance=tds[3].text.strip(),
                    weight=tds[4].text.strip(),
                    port=tds[5].text.strip(),
                    caa_flag=tds[6].text.strip(),
                    caa_tag=tds[7].text.strip(),
                    ttl=tds[8].text.strip(),
                    dyndns=tds[9].text.strip(),
                    record_id=tds[10].find_all('input')[0].get('value'),
                ))

        def activate(self):
            r = self.__session.post(self.__baseurl, data={
                'state': 'logged_in',
                'mode': 'domains',
                'domain': self.domain,
                'domain_id': self.domain_id,
                'domain_mode': 'activate_domain',
            })
            r.raise_for_status()

        def deactivate(self):
            r = self.__session.post(self.__baseurl, data={
                'state': 'logged_in',
                'mode': 'domains',
                'domain': self.domain,
                'domain_id': self.domain_id,
                'domain_mode': 'deactivate_domain',
            })
            r.raise_for_status()

        def delete(self):
            r = self.__session.post(self.__baseurl, data={
                'state': 'logged_in',
                'mode': 'domains',
                'domain': self.domain,
                'domain_id': self.domain_id,
                'domain_mode': 'delete',
            })
            r.raise_for_status()

        def add_record(self, record: Record):
            data = {**{
                'state': 'logged_in',
                'mode': 'records',
                'record_mode': 'add_record_now',
                'domain': self.domain,
            }, **record.as_dict()}
            r = self.__session.post(self.__baseurl, data=data)
            r.raise_for_status()

        def update_record(self, record: Record):
            data = {**{
                'state': 'logged_in',
                'mode': 'records',
                'record_mode': 'edit_record_now',
                'domain': self.domain,
            }, **record.as_dict()}
            r = self.__session.post(self.__baseurl, data=data)
            r.raise_for_status()

        def delete_record(self, record: Record):
            r = self.__session.post(self.__baseurl, data={
                'state': 'logged_in',
                'mode': 'records',
                'record_mode': 'delete_recs_now',
                'domain': self.domain,
                'del_id': record.record_id,
            })
            r.raise_for_status()

        def delete_records(self, records: [Record]):
            r = self.__session.post(self.__baseurl, data={
                'state': 'logged_in',
                'mode': 'records',
                'record_mode': 'delete_recs_now',
                'domain': self.domain,
                'del_id': ','.join([r.record_id for r in records]),
            })
            r.raise_for_status()

        def __str__(self):
            return f'domain_id: {self.domain_id}, domain: {self.domain}, slave: {self.slave}, status: {self.status}, owner: {self.owner} group_owner: {self.group_owner}, records: {self.records}'

        def as_dict(self):
            return {
                'domain_id': self.domain_id,
                'domain': self.domain,
                'slave': self.slave,
                'status': self.status,
                'owner': self.owner,
                'group_owner': self.group_owner,
                'records': self.records,
            }


class XpertDNS(object):
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'

    def __init__(self, **kwargs):
        if 'email' not in kwargs:
            raise MissingParameterException('email')

        if 'password' not in kwargs:
            raise MissingParameterException('password')

        self.domains = []

        self.__baseurl = 'https://www.xpertdns.com/admin/index.php'
        self.__session = kwargs.get('session', requests.Session())

        self.__login(kwargs.get('email'), kwargs.get('password'))
        self.__parse_domains()

    def __login(self, email: str, password: str):
        r = self.__session.post(self.__baseurl, data={
            'state': 'login',
            'email': email,
            'password': password,
        })
        r.raise_for_status()

    def __parse_domains(self):
        r = self.__session.get(self.__baseurl, params={
            'state': 'logged_in',
            'mode': 'domains',
        })
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        for tr in soup.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) != 8:
                continue

            domain_id = None
            m = re.search(r'domain_id=(\d+)', tds[7].find_all('a')[0].get('href'))
            if m:
                domain_id = int(m.group(1))

            self.domains.append(Domain(
                domain=tds[0].text,
                slave=False if tds[1].text.strip() == 'No' else True,
                status=tds[2].text.strip(),
                owner=tds[4].text.strip(),
                group_owner=tds[5].text.strip(),
                domain_id=domain_id,

                baseurl=self.__baseurl,
                session=self.__session,
            ))

    def names(self):
        return [d.domain for d in self.domains]

    def get(self, name: str) -> Domain:
        for d in self.domains:
            if d.domain == name:
                return d

    def __str__(self):
        return 'domains: {0}'.format([str(d) for d in self.domains])


class XpertDNSEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Record):
            return o.as_dict()

        elif isinstance(o, Domain):
            return o.as_dict()

        elif isinstance(o, XpertDNS):
            return o.domains

        return json.JSONEncoder.default(self, o)


class XpertDNSException(Exception):
    """
    basic exception for PCF
    """
    def __init__(self, msg=None):
        if msg is None:
            msg = 'An error occurred with XpertDNS API'
        super(XpertDNSException, self).__init__(msg)


class MissingParameterException(XpertDNSException):
    """"missing parameter exception (email or password)"""
    def __init__(self, parameter_name: str, msg=None):
        if msg is None:
            msg = f'{parameter_name} missing'
        super(XpertDNSException, self).__init__(msg)
