import requests
from ids_varldskulturmuseerna import record_ids

for record_id in record_ids:
        response = requests.get(f'https://localhost:8443/fedora/get/diva2:{record_id}/MODEL_NOREF', verify=False)
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            filename = (f"{record_id}_varldskulturmuserna.xml")
            with open(filename, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Data för record {record_id} sparad i {filename}")
        else:
            with open('errorlog.txt', 'a', encoding='utf-8') as log:
                log.write(f'{response.status_code}. {response.text}\n\n')
            print(f"Fel vid hämtning av record {record_id}, statuskod: {response.status_code}")
            
            