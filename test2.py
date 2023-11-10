import json

a = {'key': None}

with open('m.json', 'w') as f:
    json.dump(a, f)