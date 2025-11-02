#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)

query = gql("""
    query {
        allOrders(orderDate_Gte: "%s") {
            edges {
                node {
                    id
                    customer {
                        email
                    }
                    orderDate
                }
            }
        }
    }
""" % (datetime.now() - timedelta(days=7)).isoformat())

try:
    result = client.execute(query)
    with open('/tmp/order_reminders_log.txt', 'a') as f:
        for edge in result['allOrders']['edges']:
            order = edge['node']
            f.write(f"{datetime.now()}: Order ID {order['id']}, Customer Email: {order['customer']['email']}\n")
    print("Order reminders processed!")
except Exception as e:
    print(f"Error: {e}")