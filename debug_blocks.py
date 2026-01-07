import sys
sys.path.insert(0, 'c:/GitHub/stiebel-eltron-http')

from bs4 import BeautifulSoup
from custom_components.stiebel_eltron_http.i18n import CanonicalKey, get_aliases
from custom_components.stiebel_eltron_http import parsing

soup = BeautifulSoup(open('scripts/testdata/s_0_0_en.html','r',encoding='utf-8').read(),'html.parser')
betr_aliases = get_aliases(CanonicalKey.START_OPERATION_MODE)

print(f"Aliases: {betr_aliases}")
print()

match_count = 0
for i, block in enumerate(soup.find_all(class_=True)):
    h3 = block.find("h3")
    if not h3:
        continue
    
    heading = parsing._normalize_text(h3.get_text())
    matches = parsing._matches_alias(heading, betr_aliases)
    
    if matches:
        match_count += 1
        val1 = block.find("input", attrs={"id": "val1", "type": "hidden"})
        
        print(f"MATCH {match_count}: Block {i}")
        print(f"  Heading: '{heading}'")
        print(f"  Has val1: {val1 is not None}")
        if val1:
            print(f"  val1 value: {val1.get('value')}")
        print()
