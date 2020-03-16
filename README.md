# XpertDNS Python API
This is a python3 interface into XpertDNS's web admin interface.  You can use this api to add, update, delete domains and records.

## Synopsis
```python
from xpertdns import XpertDNS, Domain, Record, XpertDNSEncoder
import json

x = XpertDNS(email={email}, password={password})

# example: dump json
print(json.dumps(x, cls=XpertDNSEncoder))

# example: list just the domain names
for name in x.names():
    print(f'{name}')
    
# example: get a domain
d = x.get('domain.you.own')

# example: iterate over all domains you own, and add python.{domain} to each one
for d in x.domains:
    d.add_record(Record(
        name=f'python.{d.domain}',
        address='10.0.2.2',
        type='A', # this is the default and can be omitted
        ttl=3600, # this is the default and can be omitted
    ))
    
# example: add a single record
x.get('specific.domain').add_record(Record(
    name='python.specific.domain',
    address='10.0.2.3',
))

# example: edit record
d = x.get('specific.domain')

# get record that has 'python' in the name, assumes that at least one record exists
record = [r for r in d.records if 'python' in r.name][0]

# change the address
record.address = '10.0.3.1'

d.update_record(record)

# example: delete records
d = x.get('specific.domain')
records = [r for r in d.records if 'python' in r.name]

d.delete_record(records[0]) # to delete a single record
d.delete_records(records)   # to delete an array of records

```

## Installation
    python3 setup.py install
    python3 setup.py sdist  # for package

## Documentation
### XpertDNS
#### property: domains
The *domains* property is an array of XpertDNS::Domain objects that are associated with your account.
#### method: names()
The *names()* method will give you an array ref of domain names associated with your account.
#### method: get(name)
The *get()* method returns an XpertDNS::Domain object of the domain name associated with your account.  Returns *undef* otherwise.
#### method: hash()
The *hash()* method returns a pure perl hash ref of the domains and their associated records that are associated with your account.

### XpertDNS::Domain
#### property: domain
The *domain* property is the name of the domain.
#### property: slave
The *slave* property is a boolean if the domain is a slave or not.
#### property: status
The *status* property denotes whether the domain/zone is active or not.
#### property: owner
The *owner* property denotes the user that owns the domain.
#### property: group_owner
The *group_owner* property denotes the group that owns the domain.
#### property: domain_id
The *domain_id* is the unique id for this domain according to XpertDNS.
#### property: records
The *records* property is an array of XpertDNS::Record objects that denotes that records for _this_ domain.

#### method: activate()
The *activate()* method activates _this_ domain.  Only works if the domain is deactivated.
#### method: deactivate()
The *deactivate()* method deactivates _this_ domain.  Only works if the domain is activated.
#### method: delete()
The *delete()* method deletes _this_ domain/zone.
#### method: add_record(record)
The *add_record()* method adds an XpertDNS::Record to the domain/zone.
#### method: update_record(record)
The *update_record()* method updates a record via an XpertDNS::Record object.
#### method: delete_record(record)
The *delete_record()* method deletes a record from the domain/zone.

### XpertDNS::Record
#### property: name
#### property: type
#### property: address
#### property: weight
#### property: port
#### property: caa_flag
#### property: caa_tag
#### property: ttl
#### property: dyndns
#### property: record_id


