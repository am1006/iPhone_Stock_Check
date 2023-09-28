#!/usr/bin/env python3

import requests
import os
import socket
from datetime import datetime
from pytz import timezone

bot_token=""
chat_id = ""

# Get OS name
os_name = socket.gethostname().removesuffix('.localdomain')

# Get current time in AEST
current_time = datetime.now(timezone('Australia/Sydney')).strftime('%Y-%m-%d %H:%M:%S')


def check_availability():
    url = 'https://www.apple.com/au/shop/fulfillment-messages?pl=true&mts.0=regular&mts.1=compact&parts.0=MU783ZP/A&searchNearby=true&store=R483'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    body = {}

    response = requests.post(url, headers=headers, json=body)

    results = response.json()

    canberra_store = results['body']['content']['pickupMessage']['stores'][0]

    if not canberra_store or canberra_store['storeName'] != 'Canberra':
        print('Canberra store not found')
        return

    parts_availability = canberra_store['partsAvailability']['MU783ZP/A']
    pickup_display = parts_availability['pickupDisplay']

    store_pickup_product_title = parts_availability['messageTypes']['compact']['storePickupProductTitle']
    store_pickup_quote = parts_availability['messageTypes']['compact']['storePickupQuote']

    return [pickup_display, store_pickup_product_title, store_pickup_quote]

def tele_msg(msg, disable_notification=False):
    telegram = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&disable_notification={disable_notification}&parse_mode=html&text={msg}'

    try:
        requests.post(telegram)
    except requests.exceptions.RequestException as e:
        print(e)

def scheduled():
    pickup_display, store_pickup_product_title, store_pickup_quote = check_availability()

    if not pickup_display or not store_pickup_product_title or not store_pickup_quote:
        message = '{os_name} @ {current_time}:\n⚠️Error: Something went wrong - Canberra store not found'
        print(message)

        try:
            tele_msg(message, disable_notification=False)
        except requests.exceptions.RequestException as e:
            print(e)

        return

    if pickup_display != 'available':
        message = f'{os_name} @ {current_time}:\n🚫<b>Not available</b>: {store_pickup_product_title} - {store_pickup_quote}'
        print(message)

        try:
            tele_msg(message, disable_notification=True)
        except requests.exceptions.RequestException as e:
            print(e)

        return

    
    elif pickup_display == 'available':
        message = f'{os_name} @ {current_time}:\n✅\n✅\n✅\n✅\n✅\n✅\n<b>Available: {store_pickup_product_title} - {store_pickup_quote}</b>'
        print(message)

        try:
            tele_msg(message, disable_notification=False)
        except requests.exceptions.RequestException as e:
            print(e)

        return
    
    print(message)
    return

scheduled()
