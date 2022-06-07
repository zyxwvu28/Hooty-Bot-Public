import pandas as pd
import glob
from datetime import date
from chardet import detect
today = str(date.today())

# Read all .log files and append them together
input_files = glob.glob("Logs/*.log")
output_file = f'Logs/HootyBot_Combined_Logs_{today}.txt'
combined_log_list = []

n = 1
input_len = len(input_files)
for i in input_files:
    print(f'Processing {n}/{input_len}: {i}')
    x = ''
    with open(i, encoding='utf-8') as f:
        try:
            combined_log_list.append(f.read())
        except:
            with open(i, encoding='cp1252') as f:
                combined_log_list.append(f.read())
    n += 1
    
combined_log_text = '\n'.join(combined_log_list)
        
with open(output_file, 'w', encoding = 'utf-8') as f:
    f.write(combined_log_text)
    
print(f'File saved to {output_file}')