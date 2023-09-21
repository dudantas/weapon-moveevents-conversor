from xml.etree.ElementTree import parse, SubElement

import re

def read_lua_file(lua_file_path, attribute_type):
    # Initialize empty list for items and a dictionary for a single item
    items = []
    item = {}
    vocation_data = []
    capturing_vocation = False
    open_braces = 0

    # Read the LUA file line by line
    with open(lua_file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        #print(f"Reading line: {line.strip()}")  # Debugging

        # If currently capturing vocation data
        if capturing_vocation:
            #print("Capturing vocation...")  # Debugging
            open_braces += line.count('{')
            open_braces -= line.count('}')

            voc_match = re.findall(r'["\'](.*?)["\']', line)
            if len(voc_match) > 0:
                is_true = 'true' in line
                vocation_data.append({"vocation": voc_match[0], "allowed": 'true' if is_true else 'false'})
                #print(f"Captured vocation data: {vocation_data[-1]}")  # Debugging

            if open_braces == 0:
                capturing_vocation = False
                item['vocation'] = vocation_data
                #print(f"Finished capturing vocation: {vocation_data}")  # Debugging
                vocation_data = []

            continue

        match = re.match(r'(\w+) *= *(.*?)(,|\s*{)?$', line.strip())
        if match:
            key, value, _ = match.groups()
            value = value.rstrip(", {")
            #print(f"Matched Key: {key}, Value: {value}")  # Debugging
            if key == 'damage':
                damage_values = re.findall(r'\d+', value)
                item['damage'] = [int(x) for x in damage_values]
            elif key == 'vocation':
                capturing_vocation = True
                open_braces = 1
            else:
                item[key] = value
                #print(f"Stored Key: {key}, Value: {value}")  # Debugging
        elif '},' in line:
            if item:
                items.append({**item, 'tabletype': attribute_type})
                #print(f"Appending item: {items}")  # Debugging
                item = {}

    return items

lua_file_path_weapon = 'unscripted_weapons.lua'
weapons_data = read_lua_file(lua_file_path_weapon, 'weapon')

lua_file_path_moveevent = 'unscripted_equipments.lua'
moveevent_data = read_lua_file(lua_file_path_moveevent, 'moveevent')

combined_data = weapons_data + moveevent_data

from xml.etree.ElementTree import tostring
from xml.dom.minidom import parseString

type_mapping = {
    'WEAPON_NONE': 'none',
    'WEAPON_SWORD': 'sword',
    'WEAPON_CLUB': 'club',
    'WEAPON_AXE': 'axe',
    'WEAPON_SHIELD': 'shield',
    'WEAPON_DISTANCE': 'distance',
    'WEAPON_WAND': 'wand',
    'WEAPON_AMMO': 'ammo',
    'WEAPON_QUIVER': 'quiver',
    'WEAPON_MISSILE': 'missile'
}

def pretty_xml(element):
    """
    Receives an ElementTree element and returns a formatted XML string.
    """
    rough_string = tostring(element, 'utf-8')
    reparsed = parseString(rough_string)
    pretty_str = reparsed.toprettyxml(indent="\t")
    return '\n'.join([line for line in pretty_str.splitlines() if line.strip()])

def add_sub_element(attribute_scripts, key, value):
    # Converting the provided key to lowercase
    key_lower = key.lower()

    # Iterates through all 'attribute' child elements of 'attribute_scripts'
    for child in attribute_scripts:
        if child.tag == 'attribute':
            existing_key = child.get('key', '').lower()  # Converting to uppercase

            if existing_key == key_lower:
                return  # Already exists

    # If not exists, add
    sub_element = SubElement(attribute_scripts, 'attribute')
    sub_element.set('key', key)
    sub_element.set('value', str(value))  # Converting to string, because the XML value must be a string.

# Update the XML file based on combined_data
def update_xml_file(xml_file_path, combined_data):
    tree = parse(xml_file_path)
    root = tree.getroot()

    for item in root.findall('item'):
        item_id = item.get('id')
        item_data_list = [d for d in combined_data if d.get('itemId') == item_id]

        if not item_data_list:
            continue

        # Check if attribute with key 'scripts' already exists
        attribute_scripts = item.find("./attribute[@key='script']")

        # If not exists, create
        if attribute_scripts is None:
            attribute_scripts = SubElement(item, 'attribute')
            attribute_scripts.set('key', 'script')

        # Update value for key 'script'
        attribute_types = ';'.join(sorted(set(d['tabletype'] for d in item_data_list)))
        attribute_scripts.set('value', attribute_types)

        for item_data in item_data_list:
            # Adding subelement 'action'
            if 'action' in item_data:
                add_sub_element(attribute_scripts, 'action', item_data['action'])

            # Adding subelement 'scriptType'
            if 'type' in item_data and item_data['type'].strip('"') in ['stepin', 'additem']:
                add_sub_element(attribute_scripts, 'eventType', item_data['type'].strip('"'))

            # Adding subelement 'breakChance'
            if 'breakchance' in item_data or 'breakChance' in item_data:
                add_sub_element(attribute_scripts, 'breakChance', item_data.get('breakchance') or item_data.get('breakChance'))

            if 'level' in item_data:
                add_sub_element(attribute_scripts, 'level', item_data['level'])

            # Adding subelement 'mana'
            if 'mana' in item_data:
                add_sub_element(attribute_scripts, 'mana', item_data['mana'])

            # Adding subelement 'unproperly'
            if 'unproperly' in item_data:
                add_sub_element(attribute_scripts, 'unproperly', item_data['unproperly'])

            # Adding subelement 'slot'
            if 'slot' in item_data:
                slot_value = item_data['slot'].strip('"')  # Remove as aspas duplas no início e no fim
                add_sub_element(attribute_scripts, 'slot', slot_value)
    
            # Adding subelement 'damage'
            if 'damage' in item_data:
                damage_values = item_data['damage']
                if len(damage_values) == 2:
                    add_sub_element(attribute_scripts, 'fromDamage', damage_values[0])
                    add_sub_element(attribute_scripts, 'toDamage', damage_values[1])

            if 'weaponType' in item_data:
                weapon_type = type_mapping.get(item_data['weaponType'], 'unknown')
                add_sub_element(attribute_scripts, 'weaponType', weapon_type)

            # Adding subelement 'wandType'
            if 'wandType' in item_data:
                add_sub_element(attribute_scripts, 'wandType', item_data['wandType'].strip('"'))

            if 'vocation' in item_data:
                vocation_values = ', '.join(
                        [f"{v['vocation']}{';' + v['allowed'] if v['allowed'] == 'true' else ''}" for v in item_data['vocation']]
                )
                add_sub_element(attribute_scripts, 'vocation', vocation_values)

    # Write the XML
    with open("items_new.xml", "w") as f:
        f.write(pretty_xml(root))

# Run:
xml_file_path = 'items.xml'
update_xml_file(xml_file_path, combined_data)
