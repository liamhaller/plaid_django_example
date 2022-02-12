#from django.views.decorators.csrf import ensure_csrf_cookie
#from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import plaid
from plaid.api import plaid_api
import datetime
import os





plaid_client_id = os.getenv('PLAID_CLIENT_ID')
plaid_public_key = os.getenv('PLAID_PUBLIC_KEY') 
plaid_secret = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')



host = plaid.Environment.Sandbox

#if PLAID_ENV == 'sandbox':
    #host = plaid.Environment.Sandbox

#if PLAID_ENV == 'development':
    #host = plaid.Environment.Development

#if PLAID_ENV == 'production':
    #host = plaid.Environment.Production


def get_plaid_client():
    configuration = plaid.Configuration(
    #host=host,
    api_key={
        'clientId': plaid_client_id,
        'secret': plaid_secret,
        'plaidVersion': '2020-09-14'
        }
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    return client


# Global access token (workaround to make this demo simple)
# Should be stored in a database that relates access token to user account
access_token = None


def index(request):
    return render(request, 'index.html', {'plaid_public_key': plaid_public_key,
                                          'PLAID_ENV': PLAID_ENV})

def get_access_token(request):
    global access_token

    public_token = request.POST['public_token']
    client = get_plaid_client()
    exchange_response = client.Item.public_token.exchange(public_token)
    access_token = exchange_response['access_token']
    
    return JsonResponse(exchange_response)

def set_access_token(request):
    global access_token

    access_token = request.POST['access_token']

    return JsonResponse({'error': False})

def accounts(request):
    global access_token
    client = get_plaid_client()
    accounts = client.Auth.get(access_token)
    return JsonResponse(accounts)

def item(request):
    global access_token
    client = get_plaid_client()
    item_response = client.Item.get(access_token)
    institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
    return JsonResponse({'item': item_response['item'],
                         'institution': institution_response['institution']})

def transactions(request):
    global access_token
    client = get_plaid_client()
    start_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-30))
    end_date = "{:%Y-%m-%d}".format(datetime.datetime.now())
    response = client.Transactions.get(access_token, start_date, end_date)
    return JsonResponse(response)

def create_public_token(request):
    global access_token
    client = get_plaid_client()
    response = client.Item.public_token.create(access_token)
    return JsonResponse(response)
