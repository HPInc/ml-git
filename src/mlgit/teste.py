"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import random
import re


files_mock = {'zdj7Wm99FQsJ7a4udnx36ZQNTy7h4Pao3XmRSfjo4sAbt9g74': {'1.jpg'},
			  'zdj7WnVtg7ZgwzNxwmmDatnEoM3vbuszr3xcVuBYrcFD6XzmW': {'2.jpg'},
			  'zdj7Wi7qy2o3kgUC72q2aSqzXV8shrererADgd6NTP9NabpvB': {'3.jpg'},
			  'zdj7We7FUbukkozcTtYgcsSnLWGqCm2PfkK53nwJWLHEtuef4': {'6.jpg'},
			  'zdj7WZzR8Tw87Dx3dm76W5aehnT23GSbXbQ9qo73JgtwREGwB': {'7.jpg'},
			  'zdj7WfQCZgACUxwmhVMBp4Z2x6zk7eCMUZfbRDrswQVUY1Fud': {'8.jpg'},
			  'zdj7WdjnTVfz5AhTavcpsDT62WiQo4AeQy6s4UC1BSEZYx4NP': {'9.jpg'},
              'zdj7WXiB8QrNVQ2VABPvvfC3VW6wFRTWKvFhUW5QaDx6JMoma': {'10.jpg'}}
              

random.seed(3)

print(random.sample(range(0, len(files_mock)), 1))
set_files = {}
for key in random.sample(range(0, len(files_mock)), 4):
    list_file = list(files_mock)
    set_files.update({list_file[key]: files_mock.get(list_file[key])})

print(set_files)

print(random.sample(range(0, len(files_mock)), 4))
def integer_validate(value):
    try:
        return re.search("^(\d+)$",value).group(1)
    except Exception:
        return None

def group_samples_validate(value):
    try:
        r = re.search("^(\d+)\:(\d+)$", value)
        return r.groups()
    except Exception:
        return None, None


print(integer_validate("1"))

a, b  =  group_samples_validate("1:2")
print(a,b)