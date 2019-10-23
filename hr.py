
import json
from collections import OrderedDict

#file_data = OrderedDict()

#with open('words.json', 'w', encoding="utf-8") as make_file:
#    json.dump(file_data, make_file, ensure_ascii=False, indent="\t")

with open('words.json') as json_file:
    file_data = json.load(json_file)

max = 0

for n, i in enumerate(file_data['list']):
    print('{} : {}'.format(i[0], i[1]*i[2]))
    i.append(i[1]*i[2])
    if (file_data['list'][max][3] < i[3]):
        max = n

print('max: {} of {}'.format(file_data['list'][max][3], file_data['list'][max][0]))

