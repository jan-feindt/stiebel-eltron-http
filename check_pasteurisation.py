import json

langs = ['da', 'fi', 'sv', 'nl', 'fr', 'pl', 'cs', 'hu', 'it', 'es']

for lang in langs:
    file_path = f'custom_components/stiebel_eltron_http/translations/{lang}.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'dhw_pasteurisation' in data['entity']['sensor']:
        entry = data['entity']['sensor']['dhw_pasteurisation']
        print(f"{lang}: {json.dumps(entry, ensure_ascii=False, indent=2)}")
        print()
