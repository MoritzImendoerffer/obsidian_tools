"""
Daily notes do contain following sections

# Header

Some info

### [[Project title 1]]
Some daily notes

### [[Project title 2]]
Some daily notes

Some other stuff


This script scrapes the text for each project and saves it in chronological order to the project notes
"""

import re
import json
import pathlib
import os
from collections import defaultdict

with open("./config.json", "r") as f:
    config = json.load(f)

vault_path = pathlib.Path(config['abspath_vault'])
daily_path = vault_path.joinpath(config['relpath_daily_notes'])
project_path = vault_path.joinpath(config['relpath_project_notes'])

# get paths to all daily notes
notes_pattern = r"\d{4}-\d{2}-\d{2}.md"
files= os.listdir(daily_path)
daily_notes = []
for file in files:
    if re.match(notes_pattern, file):
        daily_notes.append(file)
daily_notes.sort()

# extract text from daily notes
notes = [] 
for note in daily_notes:
    with open(daily_path.joinpath(note), 'r') as f:
        text = []
        for line in f:
            text.append(line.strip('\n'))
        notes.append(text)

# get all headings with level
project_notes_pattern = r'^(#+)\s+.*'
matches = [[i, ii, re.findall(project_notes_pattern, subitem)[0]] for i, item in enumerate(notes) 
           for ii, subitem in enumerate(item) if re.match(project_notes_pattern, subitem)]

# dictionary with key = note number, item = [line number, heading level]
heading_dict = defaultdict(list)
for item in matches:
    heading_dict[item[0]].append([item[1], len(item[2])])

# get matching headings
project_notes_pattern = r'^#+\s+\[\[(.*?)\]\]$'
hmatches = [[i, ii, re.findall(project_notes_pattern, subitem)[0]] for i, item in enumerate(notes) 
           for ii, subitem in enumerate(item) if re.match(project_notes_pattern, subitem)]

# extract the text between matched headings and create a project summary from it
project_texts = dict()
for ni, line_number, heading in hmatches:
    day = daily_notes[ni].split('.md')[0]
    heading_level = [item[1] for item in heading_dict[ni] if item[0] == line_number][0]
    next_heading = [item[0] for item in heading_dict[ni] if (item[0] > line_number) & (item[1] <= heading_level)][0]
    relevant_text = notes[ni][line_number+1:next_heading]
    if all([item == '' for item in notes[ni][line_number+1:next_heading]]):
        # skip if no text was provided between headings
        print(f"skipping: {heading} for day:  {day}")
        continue
    else:
        if heading not in project_texts.keys():
            project_texts[heading] = defaultdict(list)
        project_texts[heading][day].extend(relevant_text)

# TODO: currently, it overwrites the files each time. Might be better to append?
for project in project_texts:
    text2file = []
    for day in project_texts[project]:
        text = project_texts[project][day]
        text2file.append([day, text])
    with open(project_path.joinpath(project + ".md"), 'w') as f:
        for date, item in text2file:
            f.write("# " + date + '\n')
            for line in item:
                f.write(line + '\n')