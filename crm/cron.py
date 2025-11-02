from datetime import datetime
import requests
import json
from .models import Product

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"
    
    try:
        response = requests.post('http://localhost:8000/graphql', 
                               json={'query': '{ hello }'})
        if response.status_code == 200:
            message += f"{timestamp} GraphQL endpoint responsive\n"
    except:
        pass
    
    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write(message)

def update_low_stock():
    mutation = """
    mutation {
        updateLowStockProducts {
            success
            message
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    """
    
    try:
        response = requests.post('http://localhost:8000/graphql', 
                               json={'query': mutation})
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {}).get('updateLowStockProducts', {})
            
            timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                for product in data.get('updatedProducts', []):
                    f.write(f"{timestamp}: Updated {product['name']} - New stock: {product['stock']}\n")
    except Exception as e:
        print(f"Error updating low stock: {e}")