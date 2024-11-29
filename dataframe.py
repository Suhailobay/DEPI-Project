import os
import pandas as pd
from RAG_News import XMLParser
def load_data_from_xml_files(directory):
    all_data = []
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            xml_parser = XMLParser(os.path.join(directory, filename))
            xml_parser.parse_xml()
            all_data.extend(xml_parser.extract_information())
    return all_data

# Load data from the 'news_xml_files' directory
directory = 'news_xml_files'  # Update to your actual directory
data = load_data_from_xml_files(directory)

# Convert the list of dictionaries into a DataFrame
df = pd.DataFrame(data)

# Check the DataFrame
print(df.head())