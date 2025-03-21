import pandas as pd
import json

# Load the JSON data
with open('/mnt/data/tree-sitter_lang_test.json', 'r') as file:
    data = json.load(file)

# Normalize the JSON data to a flat table
df = pd.json_normalize(data, record_path=[[]])

# Save the DataFrame to an Excel file
output_path = '/mnt/data/tree-sitter_lang_test.xlsx'
df.to_excel(output_path, index=False)
