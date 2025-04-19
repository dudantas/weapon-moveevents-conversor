#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def read_lua_file(lua_file_path, attribute_type):
    # Initialize empty list for items and a dictionary for a single item
    items = []
    item = {}
    vocation_data = []
    capturing_vocation = False
    open_braces = 0

    # Read the LUA file line by line
    with open(lua_file_path, encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        # If currently capturing vocation data
        if capturing_vocation:
            open_braces += line.count('{')
            open_braces -= line.count('}')

            voc_match = re.findall(r'["\'](.*?)["\']', line)
            if len(voc_match) > 0:
                is_true = 'true' in line
                vocation_data.append({"vocation": voc_match[0], "allowed": 'true' if is_true else 'false'})

            if open_braces == 0:
                capturing_vocation = False
                item['vocation'] = vocation_data
                vocation_data = []

            continue

        match = re.match(r'(\w+)\s*=\s*(.*?)(,|\s*{)?$', line.strip())
        if match:
            key, value, _ = match.groups()
            value = value.rstrip(", {")
            if key == 'damage':
                damage_values = re.findall(r'\d+', value)
                item['damage'] = [int(x) for x in damage_values]
            elif key == 'vocation':
                capturing_vocation = True
                open_braces = 1
            else:
                item[key] = value.strip()
        elif '},' in line:
            if item:
                items.append({**item, 'tabletype': attribute_type})
                item = {}

    return items

# Mapping from weapon enum to lowercase string
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
    'WEAPON_MISSILE': 'missile',
    'WEAPON_FIRST': 'first'
}

def to_weapon_string(raw):
    # Converts WEAPON_SWORD -> sword; fallback to lowercase raw if not mapped
    raw_clean = raw.strip('"')
    return type_mapping.get(raw_clean, raw_clean.lower())

# Build XML snippet for a single <attribute key="script">...</attribute>
def build_snippet(data_list, indent):
    script_indent = indent + '\t'
    child_indent = script_indent + '\t'
    val = ";".join(sorted({d['tabletype'] for d in data_list}))

    lines = [f'{script_indent}<attribute key="script" value="{val}">']
    added = set()

    # Adding subelement 'eventType'
    for d in data_list:
        t = d.get('type', '').strip('"')
        if t in ('stepin', 'additem'):
            lines.append(f'{child_indent}<attribute key="eventType" value="{t}"/>')
            added.add('eventType')
            break

    # Adding subelement 'action'
    for d in data_list:
        if 'action' in d:
            lines.append(f'{child_indent}<attribute key="action" value="{d["action"].strip("\"")}"/>')
            added.add('action')
            break

    # Adding subelement 'breakChance'
    for d in data_list:
        bc = d.get('breakChance', d.get('breakchance'))
        if bc is not None:
            lines.append(f'{child_indent}<attribute key="breakChance" value="{bc}"/>')
            break

    # Adding subelement 'level'
    for d in data_list:
        if 'level' in d:
            lines.append(f'{child_indent}<attribute key="level" value="{d["level"]}"/>')
            break

    # Adding subelement 'mana'
    for d in data_list:
        if 'mana' in d:
            lines.append(f'{child_indent}<attribute key="mana" value="{d["mana"]}"/>')
            break

    # Adding subelement 'unproperly'
    for d in data_list:
        if 'unproperly' in d:
            lines.append(f'{child_indent}<attribute key="unproperly" value="{d["unproperly"]}"/>')
            break

    # Adding subelement 'weaponType'
    weapon_value = None
    for d in data_list:
        if 'weaponType' in d:
            weapon_value = to_weapon_string(d['weaponType'])
            break
    if weapon_value is None:
        for d in data_list:
            if d.get('tabletype') == 'weapon' and 'type' in d:
                weapon_value = to_weapon_string(d['type'])
                break
    if weapon_value:
        lines.append(f'{child_indent}<attribute key="weaponType" value="{weapon_value}"/>')

    # Adding subelement 'slot'
    for d in data_list:
        if 'slot' in d:
            lines.append(f'{child_indent}<attribute key="slot" value="{d["slot"].strip("\"")}"/>')
            break

    # Adding subelement 'damage'
    for d in data_list:
        if 'damage' in d and len(d['damage']) == 2:
            a, b = d['damage']
            lines.append(f'{child_indent}<attribute key="fromDamage" value="{a}"/>')
            lines.append(f'{child_indent}<attribute key="toDamage" value="{b}"/>')
            break

    # Adding subelement 'wandType'
    for d in data_list:
        if 'wandType' in d:
            lines.append(f'{child_indent}<attribute key="wandType" value="{d["wandType"].strip("\"")}"/>')
            break

    # Adding subelement 'vocation'
    for d in data_list:
        if 'vocation' in d:
            vocs = ", ".join(
                f"{v['vocation']}{';true' if v['allowed'] == 'true' else ''}"
                for v in d['vocation']
            )
            lines.append(f'{child_indent}<attribute key="vocation" value="{vocs}"/>')
            break

    lines.append(f'{script_indent}</attribute>')
    return lines

# Update the XML file with generated snippets from the combined LUA data
def main():
    weapons = read_lua_file('unscripted_weapons.lua', 'weapon')
    events = read_lua_file('unscripted_equipments.lua', 'moveevent')
    combined = weapons + events

    by_id = {}
    for d in combined:
        raw = d.get('itemId', d.get('itemid'))
        if raw is None:
            continue
        by_id.setdefault(str(raw), []).append(d)

    src = open('items.xml', encoding='iso-8859-1').read().splitlines()
    out = []
    i = 0
    while i < len(src):
        line = src[i]
        out.append(line)

        m = re.match(r'(\t*)<item\s+id="(\d+)"', line)
        if m:
            indent, iid = m.groups()
            if iid in by_id:
                block = []
                i += 1
                while i < len(src) and '</item>' not in src[i]:
                    block.append(src[i])
                    i += 1
                closing = src[i]
                out.extend(block)
                out.extend(build_snippet(by_id[iid], indent))
                out.append(closing)
                i += 1
                continue
        i += 1

    with open('items_new.xml', 'w', encoding='iso-8859-1', newline='\n') as f:
        f.write("\n".join(out))

if __name__ == '__main__':
    main()
