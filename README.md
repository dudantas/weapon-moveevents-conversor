# **Sponsors**

See our [donate page](https://docs.opentibiabr.com/home/donate)
## Description

This Python script is responsible for reading LUA files and updating an XML file based on the gathered data. Its primary use-case is for managing weapon and move event information in a game.

## Dependencies

- Python 3.x
- `re` (Regular Expression Module)
- `xml.etree.ElementTree` (XML Manipulation Module)

## How to Use

### 1. Installation

Make sure you have Python 3.x installed on your system. You can download Python from [python.org](https://www.python.org/).

### 2. Prepare LUA and XML Files

Place the LUA files `unscripted_weapons.lua` and `unscripted_equipments.lua` in the same directory as the script. Make sure you also have an `items.xml` file that will be updated.

#### NOTE: In the unscripted_weapons file, the "type" variable must be renamed to "weaponType"

### 3. Run the Script

Execute the Python script using the following command on project folder:

```powershell
py -3 converter.py
```

#### For UNIX-like systems (Linux, macOS):
```bash
python3 converter.py
```

This will read the LUA files, process them, and then update the `items.xml` file. A new `items_new.xml` file will be generated with the updates.

### 4. Verification

Check the `items_new.xml` file to ensure updates were made as expected.

## Implementation Details

- The `read_lua_file` function is responsible for reading a LUA file and extracting necessary data.
- The `update_xml_file` function is responsible for updating the XML file with the data collected from LUA files.
- The script uses regular expressions to parse data from the LUA files.
- The script also offers a `pretty_xml` function to improve the formatting of the generated XML.

## Notes

- The regular expressions used in the script may not be suitable if the format of the LUA file changes. Ensure you fully test before using in a production environment.
