from pathlib import Path
from bs4 import BeautifulSoup
import json,re,sys
root=Path(__file__).parent
html=(root/'index.html').read_text(encoding='utf-8')
soup=BeautifulSoup(html,'html.parser')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
def has_id(i): return soup.select_one('#'+i) is not None
# Structure
need(not [i for i in {x.get('id') for x in soup.select('[id]')} if i and len(soup.select('#'+i))>1],'Dubbele IDs gevonden')
for i in ['opmeting-form','btn-clear-all','btn-dossiers','btn-import-json','btn-export-json','json-file-input','dossier-dialog','validation-box','ral-kleur','ral-palette','ral-results','vloergeleider','antipaniek-raillengte','proline-security-row','security-rc2','security-rc3','glas-type-l','glas-code-l','glas-type-r','glas-code-r','print-meta','print-footer-dossier']:
    need(has_id(i),f'Ontbrekend element: {i}')
# Required customer fields
for i in ['werf','datum-opmeting','dossiernummer','contactpersoon','locatie','deurlocatie','technieker']:
    need(has_id(i) and soup.select_one('#'+i).has_attr('required'),f'Verplicht dossier/klantveld ontbreekt: {i}')
# Features
for token,msg in [('loadFullRalPalette','Volledig dynamisch RAL-palet ontbreekt'),('localStorage','Autosave ontbreekt'),('Opmeting_Mesure.mobileconfig','iOS-profiel ontbreekt'),('U-profiel','U-profiel ontbreekt'),('guide-full-rect','Volledige rail ontbreekt'),('guide-ap-l','Antipaniekrail ontbreekt'),('validateMeasurements','Dynamische validatie ontbreekt'),('clearEverything','Wis Alles ontbreekt')]: need(token in html,msg)
need('serviceWorker' not in html,'Offline/serviceworker mag niet aanwezig zijn')
for token,msg in [('ralLexicon','RAL-vertaalwoordenboek ontbreekt'),('localizeRalName','RAL-naamvertaling ontbreekt'),('labelNl','Nederlandse RAL-zoeknamen ontbreken'),('labelFr','Franse RAL-zoeknamen ontbreken'),('normalizeRalText','Accent-onafhankelijke RAL-zoekfunctie ontbreekt')]: need(token in html,msg)
need(len(soup.select('#glas-type-l option'))>=10,'Te weinig glastypes')
need(any(o.get('value')=='U-profiel' for o in soup.select('#vloergeleider option')),'U-profiel keuzewaarde ontbreekt')
need('updateAntipaniekLength' in html,'Antipaniek raillengteberekening ontbreekt')
need('leafLeft+100' in html,'Formule deurvleugel links + 100 mm ontbreekt')
need("opening.includes('Dubbel')?2:1" in html,'Automatische keuze 1 of 2 rails ontbreekt')
# Manifest
manifest=json.loads((root/'manifest.webmanifest').read_text())
need(manifest.get('name')=='Opmeting Mesure','Manifestnaam fout')
for f in ['icon-180.png','icon-192.png','icon-512.png','README.md','FEATURE_COMPARISON.md']:
    need((root/f).exists(),f'Pakketbestand ontbreekt: {f}')
if errors:
    print('REGRESSION TEST FAILED')
    for e in errors: print('-',e)
    sys.exit(1)
print('REGRESSION TEST PASSED: alle cumulatieve functies aanwezig, offline bewust uitgesloten.')
