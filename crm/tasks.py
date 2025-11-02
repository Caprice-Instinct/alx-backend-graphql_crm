from celery import shared_task
from datetime import datetime
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        query = gql("""
            query {
                allCustomers {
                    edges {
                        node {
                            id
                        }
                    }
                }
                allOrders {
                    edges {
                        node {
                            id
                            totalAmount
                        }
                    }
                }
            }
        """)
        
        result = client.execute(query)
        
        total_customers = len(result['allCustomers']['edges'])
        total_orders = len(result['allOrders']['edges'])
        total_revenue = sum(float(order['node']['totalAmount']) for order in result['allOrders']['edges'])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"
        
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(report)
            
    except Exception as e:
        print(f"Error generating CRM report: {e}")