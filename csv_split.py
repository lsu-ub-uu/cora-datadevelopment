import pandas as pd
import csv

filePath = (r'C:\users\almta256\downloads\ltu_isi_feb2025.csv')  #<-- byt ut filen här
rows_per_file = 200

def split_csv(filePath, rows_per_file):
    df = pd.read_csv(filePath, dtype=str)

    for i in range(0, len(df), rows_per_file):
        chunk = df[i:i+rows_per_file]

        output_file= f'ltu_isi_part_{i//rows_per_file + 1}.csv'  #<-- ändra filnamn för outputfilen här
        chunk.to_csv(output_file, index=False, header=True, sep=',', quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8', na_rep='')
        print(f'Created: {output_file}')

split_csv(filePath, rows_per_file)