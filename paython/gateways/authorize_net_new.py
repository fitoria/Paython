import json
import time
import logging
from collections import OrderedDict

from paython.exceptions import MissingDataError
from paython.lib.api import JsonGateway 

logger = logging.getLogger(__name__)


# {
#     "createTransactionRequest": {
#         "merchantAuthentication": {
#             "name": "5KP3u95bQpv",
#             "transactionKey": "346HZ32z3fP4hTG2"
#         },
#         "refId": "123456",
#         "transactionRequest": {
#             "transactionType": "authOnlyTransaction",
#             "amount": "5",
#             "payment": {
#                 "creditCard": {
#                     "cardNumber": "5424000000000015",
#                     "expirationDate": "2025-12",
#                     "cardCode": "999"
#                 }
#             },
#             "lineItems": {
#                 "lineItem": {
#                     "itemId": "1",
#                     "name": "vase",
#                     "description": "Cannes logo",
#                     "quantity": "18",
#                     "unitPrice": "45.00"
#                 }
#             },
#             "tax": {
#                 "amount": "4.26",
#                 "name": "level2 tax name",
#                 "description": "level2 tax"
#             },
#             "duty": {
#                 "amount": "8.55",
#                 "name": "duty name",
#                 "description": "duty description"
#             },
#             "shipping": {
#                 "amount": "4.26",
#                 "name": "level2 tax name",
#                 "description": "level2 tax"
#             },
#             "poNumber": "456654",
#             "customer": {
#                 "id": "99999456654"
#             },
#             "billTo": {
#                 "firstName": "Ellen",
#                 "lastName": "Johnson",
#                 "company": "Souveniropolis",
#                 "address": "14 Main Street",
#                 "city": "Pecan Springs",
#                 "state": "TX",
#                 "zip": "44628",
#                 "country": "US"
#             },
#             "shipTo": {
#                 "firstName": "China",
#                 "lastName": "Bayles",
#                 "company": "Thyme for Tea",
#                 "address": "12 Main Street",
#                 "city": "Pecan Springs",
#                 "state": "TX",
#                 "zip": "44628",
#                 "country": "US"
#             },
#             "customerIP": "192.168.1.1",
#             "userFields": {
#                 "userField": [
#                     {
#                         "name": "MerchantDefinedFieldName1",
#                         "value": "MerchantDefinedFieldValue1"
#                     },
#                     {
#                         "name": "favorite_color",
#                         "value": "blue"
#                     }
#                 ]
#             },
# 	    "processingOptions": {
#              "isSubsequentAuth": "true"
#             },
# 	     "subsequentAuthInformation": {
#              "originalNetworkTransId": "123456789NNNH",
#              "originalAuthAmount": "45.00",
#              "reason": "resubmission"
#             },			
#             "authorizationIndicatorType": {
#             "authorizationIndicator": "pre"
#           }
#         }
#     }
# }

BASE_TRANSACTION_DICT = { 
    "createTransactionRequest": {
        "merchantAuthentication": {
            "name": "5KP3u95bQpv",
            "transactionKey": "346HZ32z3fP4hTG2"
        }
    },
    "refId": "123456",
    "transactionRequest": {}
}

BASE_TRANSACTION_REQUEST_DICT = {
    "transactionType": "",
    "amount": "",
    "payment": {
        "creditCard": {
            "cardNumber": "",
            "expirationDate": "",
            "cardCode": ""
        }
    },
    "lineItems": {},
    "tax": {},
    "duty": {},
    "shipping": {},
    "poNumber": "",
    "customer": {},
    "billTo": {},
    "shipTo": {},
    "customerIP": "",
    "transactionSettings": {},
    "userFields": {},
    "processingOptions": {},
}

class AuthorizeNetNew(JsonGateway):
    """New Authorize.net version with request.api endpoint"""
    VERSION = '3.1'
    DELIMITER = ';'
    LIVE_TEST = 'live_test'

    # This is how we determine whether or not we allow 'test' as an init param
    API_URI = {
        'live' : 'https://api.authorize.net/xml/v1/request.api',
        'test' : 'https://apitest.authorize.net/xml/v1/request.api'
    }
    # Response Code: 1 = Approved, 2 = Declined, 3 = Error, 4 = Held for Review
    # AVS Responses: A = Address (Street) matches, ZIP does not,  P = AVS not applicable for this transaction,
    # AVS Responses (cont'd): W = Nine digit ZIP matches, Address (Street) does not, X = Address (Street) and nine digit ZIP match,
    # AVS Responses (cont'd): Y = Address (Street) and five digit ZIP match, Z = Five digit ZIP matches, Address (Street) does not
    # response index keys to map the value to its proper dictionary key

    debug = False
    test = False
    REQUEST_FIELDS = {}
    #{'transactionResponse': {'responseCode': '3', 'authCode': '', 'avsResultCode': 'P', 'cvvResultCode': '', 'cavvResultCode': '', 'transId': '0', 'refTransID': '', 'transHash': '', 'testRequest': '0', 'accountNumber': 'XXXX1111', 'accountType': 'Visa', 'errors': [{'errorCode': '11', 'errorText': 'A duplicate transaction has been submitted.'}], 'transHashSha2': '', 'SupplementalDataQualificationIndicator': 0}, 'refId': '', 'messages': {'resultCode': 'Error', 'message': [{'code': 'E00027', 'text': 'The transaction was unsuccessful.'}]}}
    API_CALL_NAME = ''

    def __init__(self, username='test', password='testpassword', debug=False, test=False, delim=None):
        """
        setting up object so we can run 4 different ways (live, debug, test & debug+test)
        There are two different test modes:
        - test=True: regular test mode where the authentication and verification
          is done on the authorize.net staging server.
          For this you need to use the credentials of your test account.
        - test="live_test": the transaction is processed on the live authorize.net
          server but is not submitted to financial institutions for authorization.
          For this you need to use the credentials of the live authorize.net
          account.

        For further details please see:
        http://developer.authorize.net/guides/AIM/wwhelp/wwhimpl/common/html/wwhelp.htm#context=AIM&file=5_TestTrans.html
        """
        # passing fields to bubble up to Base Class
        super(AuthorizeNetNew, self).__init__(translations=self.REQUEST_FIELDS, debug=debug)
        super(AuthorizeNetNew, self).set("merchantAuthentication", {"name": username, "transactionKey": password})

        if debug:
            self.debug = True

        if test:
            if test != self.LIVE_TEST:
                self.test = True
                test_string = 'regular'
            else:
                test_string = 'live'
            debug_string = " paython.gateways.authorize_net.__init__() -- You're in %s test mode (& debug, obviously) " % test_string
            logger.debug(debug_string.center(80, '='))
        else:
            self.test = False

    def params(self):
        """
        returns arguments that are going to be sent to the POST (here for debugging)
        """
        request_wrapper = {self.API_CALL_NAME: self.REQUEST_DICT}
        return json.dumps(request_wrapper).encode('utf-8') 

    def charge_setup(self, api_call_name='createTransactionRequest', method_call_name='transactionRequest'):
        """
        standard setup, used for charges
        """
        self.API_CALL_NAME = api_call_name
        super(AuthorizeNetNew, self).set('refId', "")
        super(AuthorizeNetNew, self).set(method_call_name, OrderedDict())
        debug_string = " paython.gateways.authorize_net.charge_setup() Just set up for a charge "
        logger.debug(debug_string.center(80, '='))

    def use_credit_card(self, credit_card, method_name='transactionRequest'):
        """
        Sets up credit card for charge
        """
        cc_dict = OrderedDict()
        cc_dict['cardNumber'] = credit_card.number
        cc_dict['expirationDate'] = f"{credit_card.exp_month}-{credit_card.exp_year}" 
        cc_dict['cardCode'] = credit_card.verification_value
        self.REQUEST_DICT[method_name]['payment'] = {"creditCard": cc_dict} 
        debug_string = " paython.gateways.authorize_net.use_credit_card() -- Just set up a credit card "
        logger.debug(debug_string.center(80, '='))

    def set_billing_info(self, **kwargs):
        bill_info = OrderedDict()
        bill_info['firstName'] = kwargs.get('first_name', '')
        bill_info['lastName'] = kwargs.get('last_name', '') 
        bill_info['company'] = kwargs.get('company', '')
        bill_info['address'] = kwargs.get('address', '')
        bill_info['city'] = kwargs.get('city', '')
        bill_info['zip'] = kwargs.get('zip_code', '')
        bill_info['country'] = kwargs.get('country', '')
        method_name = kwargs.get('method_name', 'transactionRequest') 
        self.REQUEST_DICT[method_name]['billTo'] = bill_info
        logger.debug("paython.gateways.authorize_net.set_billing_info() -- Just set up billing info ")
    
    def set_shipping_info(self, **kwargs):
        ship_to = OrderedDict()
        ship_to['firstName'] = kwargs.get('first_name', '')
        ship_to['lastName'] = kwargs.get('last_name', '') 
        ship_to['company'] = kwargs.get('company', '')
        ship_to['address'] = kwargs.get('address', '')
        ship_to['city'] = kwargs.get('city', '')
        ship_to['zip'] = kwargs.get('zip_code', '')
        ship_to['country'] = kwargs.get('country', '')
        method_name = kwargs.get('method_name', 'transactionRequest') 
        self.REQUEST_DICT[method_name]['shipTo'] = ship_to 
        logger.debug("paython.gateways.authorize_net.set_shipping_info() -- Just set up billing info ")
    
    def auth(self, amount, credit_card=None, billing_info=None, shipping_info=None, is_partial=False, split_id=None, invoice_num=None):
        """
        Sends charge for authorization based on amount
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?
        if invoice_num is not None:
            self.REQUEST_DICT['refId'] = invoice_num

        self.REQUEST_DICT['transactionRequest']['transactionType'] = "authOnlyTransaction" 
        self.REQUEST_DICT['transactionRequest']['amount'] = str(amount) 

        # validating or building up request
        if not credit_card:
            debug_string = "paython.gateways.authorize_net.auth()  -- No CreditCard object present. You passed in %s " % (credit_card)
            logger.debug(debug_string)

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            self.use_credit_card(credit_card)

        if billing_info:
            self.set_billing_info(**billing_info)

        if shipping_info:
            self.set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def settle(self, amount, trans_id):
        """
        Sends prior authorization to be settled based on amount & trans_id PRIOR_AUTH_CAPTURE
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        self.REQUEST_DICT['transactionRequest']['transactionType'] = "priorAuthCaptureTransaction" 
        self.REQUEST_DICT['transactionRequest']['amount'] = str(amount) 
        self.REQUEST_DICT['transactionRequest']['refTransId'] = str(trans_id) 

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def capture(self, amount, credit_card=None, billing_info=None, 
                shipping_info=None, line_item={}):
        """
        Sends transaction for capture (same day settlement) based on amount.
        """
        self.charge_setup() # considering turning this into a decorator?

        self.REQUEST_DICT['transactionRequest']['transactionType'] = "authCaptureTransaction" 
        self.REQUEST_DICT['transactionRequest']['amount'] = str(amount) 
        #"lineItems": {
        #        "lineItem": {
        #            "itemId": "1",
        #            "name": "vase",
        #            "description": "Cannes logo",
        #            "quantity": "18",
        #            "unitPrice": "45.00"
        #        }
                # validating or building up request
        if not credit_card:
            debug_string = "paython.gateways.authorize_net.auth()  -- No CreditCard object present. You passed in %s " % (credit_card)
            logger.debug(debug_string)

            raise MissingDataError('You did not pass a CreditCard object into the auth method')
        else:
            self.use_credit_card(credit_card)

        if line_item:
            line_items = {'lineItem': line_item}
            self.REQUEST_DICT['transactionRequest']['lineItems'] = line_items

        if billing_info:
            self.set_billing_info(**billing_info)

        if shipping_info:
            self.set_shipping_info(**shipping_info)

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def void(self, trans_id, split_id=None):
        """
        Sends a transaction to be voided (in full)
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        self.REQUEST_DICT['transactionRequest']['transactionType'] = "voidTransaction" 
        self.REQUEST_DICT['transactionRequest']['refTransId'] = str(trans_id) 

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def credit(self, amount, trans_id, credit_card, split_id=None):
        """
        Sends a transaction to be refunded (partially or fully)
        """
        #set up transaction
        self.charge_setup() # considering turning this into a decorator?

        self.REQUEST_DICT['transactionRequest']['transactionType'] = "refundTransaction" 
        self.REQUEST_DICT['transactionRequest']['amount'] = str(amount) 
        self.use_credit_card(credit_card)
        self.REQUEST_DICT['transactionRequest']['refTransId'] = str(trans_id) 

        # send transaction to gateway!
        response, response_time = self.request()
        return self.parse(response, response_time)

    def create_subscription(self, name, amount, credit_card, 
                            billing_info, interval_length, 
                            interval_unit, start_date, 
                            total_occurrences):
        '''Creates a subscription (recurring billing)'''
        self.charge_setup('ARBCreateSubscriptionRequest', 'subscription') # considering turning this into a decorator?
        self.REQUEST_DICT['subscription']['name'] = name 
        payment_schedule = OrderedDict()
        payment_schedule['interval'] = OrderedDict()
        payment_schedule['interval']['length'] = interval_length
        payment_schedule['interval']['unit'] = interval_unit
        payment_schedule['startDate'] = start_date
        payment_schedule['totalOccurrences'] = total_occurrences
        payment_schedule['trialOccurrences'] = '0'
        self.REQUEST_DICT['subscription']['paymentSchedule'] = payment_schedule 
        self.REQUEST_DICT['subscription']['amount'] = amount
        self.REQUEST_DICT['subscription']['trialAmount'] = '0' 
        self.use_credit_card(credit_card, 'subscription')
        self.set_billing_info(method_name='subscription', **billing_info)

        response, response_time = self.request()
        return self.parse(response, response_time)

    def cancel_subscription(self, subscription_id):
        '''Creates a subscription (recurring billing)'''
        self.charge_setup('ARBCancelSubscriptionRequest', 'subscriptionId') # considering turning this into a decorator?
        self.REQUEST_DICT['subscriptionId'] = subscription_id

        response, response_time = self.request()
        return self.parse(response, response_time)


    def request(self):
        """
        Makes a request using lib.api.GetGateway.make_request() & move some debugging away from other methods.
        """
        # decide which url to use (test|live)
        if self.test == self.LIVE_TEST or not self.test:
            url = self.API_URI['live']
        else:
            url = self.API_URI['test'] # here just in case we want to granularly change endpoint

        debug_string = " paython.gateways.authorize_net.request() -- Attempting request to: "
        logger.debug(debug_string.center(80, '='))
        debug_string = "%s with params: %s" % (url, super(AuthorizeNetNew, self).params())
        logger.debug(debug_string)
        logger.debug('as dict: %s' % self.REQUEST_DICT)

        # make the request
        start = time.time() # timing it
        response = super(AuthorizeNetNew, self).make_request(url)
        end = time.time() # done timing it
        response_time = '%0.2f' % (end - start)

        debug_string = " paython.gateways.authorize_net.request()  -- Request completed in %ss " % response_time
        logger.debug(debug_string.center(80, '='))

        return response, response_time

    def standardize(self, spec_response, response_time, approved):
        """
        Translates gateway specific response into Paython generic response.
        Expects list or dictionary for spec_repsonse & dictionary for field_mapping.
        """
        # manual settings
        self.RESPONSE_FIELDS['response_time'] = response_time
        self.RESPONSE_FIELDS['approved'] = approved

        self.RESPONSE_FIELDS['messages'] = spec_response['messages']
        try:
            self.RESPONSE_FIELDS['response'] = spec_response['transactionResponse']
            self.RESPONSE_FIELDS['refId'] = spec_response['refId']
        except:
            pass
        self.RESPONSE_FIELDS.update(spec_response)
        return self.RESPONSE_FIELDS

    def parse(self, response, response_time):
        """
        On Specific Gateway due differences in response from gateway
        """
        response = response.decode('utf-8-sig')
        debug_string = " paython.gateways.authorize_net.parse() -- Raw response: "
        logger.debug(debug_string.center(80, '='))
        logger.debug("\n %s" % response)

        #splitting up response into a list so we can map it to Paython generic response
        response = json.loads(response) 
        approved = response['messages']['resultCode'] == 'Ok'

        debug_string = " paython.gateways.authorize_net.parse() -- Response as list: "
        logger.debug(debug_string.center(80, '='))
        logger.debug('\n%s' % response)

        return self.standardize(response, response_time, approved)
