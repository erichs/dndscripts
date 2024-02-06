from email.mime import image
from genericpath import isfile
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from pathlib import Path
import requests
import string
import re
import sys
import hashlib
from openai import OpenAI
import os

def download_image(image_url, local_filename):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(local_filename, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

size_radius = {
    'tiny': 0.5,
    'small': 1,
    'medium': 1,
    'large': 2,
    'huge': 3,
    'gargantuan': 4
}

def find_count_before_creature(text, creature):
    count_values = {
        'a': 1,
        'an': 1,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10
    }

    pattern = r'\b(a|an|one|two|three|four|five|six|seven|eight|nine|ten)\s+' + re.escape(creature) + r's?\b'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        return count_values[match.group(1).lower()] 
    else:
        return None 

def normalize_and_hash(text):
    normalized_text = re.sub(r'\s+', ' ', text).strip().lower()
    return hashlib.md5(normalized_text.encode('utf-8')).hexdigest()

def is_header(s: str) -> bool:
    lines = s.split('\n')
    return lines[0] == lines[1]

def size_category(s: str) -> str:
    pattern = r'\b(Tiny|Large|Medium|Small|Gargantuan|Huge)\b'
    match = re.search(pattern, s, re.IGNORECASE)
    return match.group().lower() if match else ''

def type_category(input_string):
    cleaned_input = input_string.translate(str.maketrans('', '', string.punctuation))
    words = cleaned_input.lower().split()
    return words[1] if len(words) > 1 else ""

def count_creatures(pdf_path, creatures):
    creature_names = [c['name'].lower() for c in creatures if 'name' in c]
    seen_hashes = set()
    e = 0
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            e += 1
            if isinstance(element, LTTextContainer):
                text = element.get_text().strip().lower()
                # skip if we've seen this line before
                text_hash = normalize_and_hash(text)
                if text_hash in seen_hashes:
                    continue
                seen_hashes.add(text_hash)

                for creature in creatures:
                    name = creature['name'].lower()
                    if name in text:
                        if "adjustment" in text:
                            continue
                        creature_count = find_count_before_creature(text, name)
                        if creature_count:
                            creature['count'] += creature_count
    return creatures

def extract_creatures(pdf_path):
    creatures = []

    pages = extract_pages(pdf_path)
    for page_layout in pages:
        # Convert page_layout to an iterator to manually control iteration
        elements = iter(page_layout)
        try:
            current_element = next(elements)
            while True:
                next_element = next(elements)
                if isinstance(current_element, LTTextContainer):
                    text = current_element.get_text()
                    if is_header(text):
                        # Creature statblocks begin with two lines of the form:
                        # <creature name header>
                        # <size> <type>, <alignment>
                        if isinstance(next_element, LTTextContainer):
                            next_text = next_element.get_text()
                            size = size_category(next_text)
                            if size:
                                creature = text.split('\n')[0]
                                s = size.lower()
                                filename = f'{creature.lower().replace(" ", "_")}_{s}_{size_radius[s]}in'
                                type = type_category(next_text)
                                creatures.append({"name": creature, 
                                                  "size": size, 
                                                  "type": type,
                                                  "filename": filename,
                                                  "count": 1})
                            else:
                                break
                current_element = next_element
        except StopIteration:
            pass
    return creatures

# Usage
if len(sys.argv) < 2:
    print("Usage: python script_name.py <pdf_file_path>")
    sys.exit(1)

pdf_path = sys.argv[1]
print('Extracting creatures...')
creatures = extract_creatures(pdf_path)
print(f'Found {len(creatures)} creatures.')
print('Adjusting creature counts...')
creatures = count_creatures(pdf_path, creatures)
client = OpenAI()
for creature in creatures:
    creature['filename'] += f'_{creature["count"]}ct.webp'
    if os.path.isfile(creature["filename"]):
        print(f'Found {creature["filename"]}.')
        continue
    print(f'Generating {creature["filename"]}...')
    image = client.images.generate(prompt=f'a {creature["size"]} {creature["type"]}, similar to a {creature["name"]}, in a gritty fantasy style. Dramatic full-body shot.', model='dall-e-3')
    download_image(image.data[0].url, creature["filename"])
print('Done.')