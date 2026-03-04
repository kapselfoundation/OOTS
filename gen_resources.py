import os
import hashlib
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Configuration
BASE_DIR = "." 
OUTPUT_FILE = "resources.xml"

def get_md5_etag(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return f'"{hash_md5.hexdigest()}"' # S3 ETags require double quotes

def generate_s3_xml():
    root = ET.Element("ListBucketResult", xmlns="http://s3.amazonaws.com/doc/2006-03-01/")
    ET.SubElement(root, "Name").text = "MinecraftResources"
    
    for dirpath, _, filenames in os.walk(BASE_DIR):
        for filename in filenames:
            if filename == OUTPUT_FILE or filename.endswith(".py"):
                continue

            file_path = os.path.join(dirpath, filename)
            rel_key = os.path.relpath(file_path, BASE_DIR).replace("\\", "/")
            
            stats = os.stat(file_path)
            last_mod = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            contents = ET.SubElement(root, "Contents")
            ET.SubElement(contents, "Key").text = rel_key
            ET.SubElement(contents, "LastModified").text = last_mod
            ET.SubElement(contents, "ETag").text = get_md5_etag(file_path)
            ET.SubElement(contents, "Size").text = str(stats.st_size)
            ET.SubElement(contents, "StorageClass").text = "STANDARD"

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml_str)

if __name__ == "__main__":
    generate_s3_xml()
    print(f"Generated {OUTPUT_FILE} in S3 format.")