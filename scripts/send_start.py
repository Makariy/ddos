import requests


def request():
    return requests.post('http://localhost:8000/', json={
        'action': {
            'target': {'host': 'localhost:8001/recipes/get/best_month/', 'protocol': 'http'},
            'command': {'title': 'ddos'}
        }
    })
