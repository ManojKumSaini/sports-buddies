import xmltodict
import json

def xml_to_json(xml_file_path, json_file_path):
    with open(xml_file_path, 'r', encoding='utf-8') as xml_file:
        xml_content = xml_file.read()
        data_dict = xmltodict.parse(xml_content)
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_dict, json_file, indent=2)

# Call the function with your file names
xml_to_json('Export.xml', 'export.json')