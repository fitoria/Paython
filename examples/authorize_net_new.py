"""authorize_net.py - Authorize.Net example"""

try:
    from paython import api, gateways, CreditCard
except ImportError:
    # adding paython to the path
    # to run this without installing the library
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

    # trying again
    from paython import api, gateways, CreditCard

AUTHORIZE_NET_SETTINGS = {
   'username': 'test',
   'password': 'test',
   'debug': True,
   'test': True,
}

api = gateways.AuthorizeNetNew(**AUTHORIZE_NET_SETTINGS)

mycard = {
    'first_name': 'Fralnk',
    'last_name': 'McFrlanklen',
    'number': '4111111111111111',
    'exp_mo': '12',
    'exp_yr': '2025',
    'cvv': '900',
}

cc_obj = CreditCard(**mycard)

billing = {
    'address': '7519 NW 88th Terrace',
    'city': 'Tamarac',
    'state': 'FL',
    'zipcode': '33320',
    'phone': '9546703289',
    'email': 'auston@gmail.com',
    'first_name': 'Franklin',
    'last_name': 'McFranklen',
}

print(api.auth('10', cc_obj, billing))
print(api.capture(float('20.02'), cc_obj))
print(api.void('80008071132'))

print(api.create_subscription("Test subscription", '10', cc_obj, billing, '1', 'months','2023-11-09', '12'))
print(api.cancel_subscription('9017260'))