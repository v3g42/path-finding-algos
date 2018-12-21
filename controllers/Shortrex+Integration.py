
# coding: utf-8

# ### Here we are mapping your CSV

# In[ ]:

import requests
import json

url = 'http://localhost:4000/api/v3/dispatcher/tasks'
payload = {'page_size': 100000000, 'order_number': 'O-YTFOBGRYBFHA'}
headers = {'company_slug': 'cocacola',
           'access_token': 'EBZ8NJISmA7FKZ4y2ZMJMDjPVGmbI+1qswusC6BzmDY='}
r = requests.get(url, headers=headers, params=payload)
tasks = r.json()['data']

driver_dict = {}

for t in tasks:
    driver_key = t['order_item']['external_customer_id2']
    if driver_key in driver_dict:
        driver_dict[driver_key] = [t] + driver_dict[driver_key]
    else:
        driver_dict[driver_key] = [t]

# get workers yo
url_w = 'http://localhost:4000/api/v3/dispatcher/workers'
worker_payload = {'page_size': 1}

driver_dict_by_id = {}

for key in driver_dict.keys():
    worker_payload['name'] = key
    r = requests.get(url_w, headers=headers, params=worker_payload)
    if r.json()['data'][0]['name'] != key:
        raise Exception("I know python!")
    worker_id = str(r.json()['data'][0]['id'])
    driver_dict_by_id[worker_id] = driver_dict[key]
print(driver_dict_by_id.keys())


allocate_payload = {'_json': []}
for worker_id in driver_dict_by_id.keys():
    task_ids = []
    worker_object = {'polyline': [], 'commision': '0'}
    for task in driver_dict_by_id[worker_id]:
        task_ids = [task['id']] + task_ids
    worker_object['worker_id'] = worker_id
    worker_object['tasks'] = [{'id': 'startFromDepot'}]
    for task_id in task_ids:
        worker_object['tasks'] = worker_object['tasks'] +             [{'polyline': [], 'id': str(task_id), 'eta': None}]
    allocate_payload['_json'] = allocate_payload['_json'] + [worker_object]

allocate_url = 'http://localhost:4000/api/v3/dispatcher/tasks/allocate'


r = requests.post(allocate_url, headers=headers, json=allocate_payload)
print(allocate_payload)

print(r.text)

