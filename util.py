import json, sys, os

all_data = []
for subdir, dirs, files in os.walk('./scrapes'):
    for file in files:
        with open(file, 'r') as inFile:
            all_data += json.load(inFile)

with open('scrapes/shallow.json', 'w') as out:
    json.dump(all_data)

