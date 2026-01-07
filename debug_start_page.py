from bs4 import BeautifulSoup
from custom_components.stiebel_eltron_http.i18n_canonical import CanonicalKey, get_aliases
from custom_components.stiebel_eltron_http import parsing

soup = BeautifulSoup(open('scripts/testdata/s_0_0_en.html','r',encoding='utf-8').read(),'html.parser')

betr_aliases = get_aliases(CanonicalKey.START_OPERATION_MODE)
print(f"Aliases: {betr_aliases}")
print()

for i, h3 in enumerate(soup.find_all('h3')):
    text = h3.get_text().strip()
    if 'Operating mode' in text:
        # Find parent block
        parent = h3.find_parent(class_=True)
        val1 = parent.find('input', attrs={'id': 'val1', 'type': 'hidden'}) if parent else None
        
        # Check if heading matches aliases
        normalized = parsing._normalize_text(text)
        matches = parsing._matches_alias(normalized, betr_aliases)
        
        print(f"H3 {i}: '{text}'")
        print(f"  Normalized: '{normalized}'")
        print(f"  Matches aliases: {matches}")
        print(f"  Parent classes: {parent.get('class') if parent else 'NO PARENT'}")
        print(f"  Has val1: {val1 is not None}")
        if val1:
            print(f"  val1 value: {val1.get('value')}")
        print()
