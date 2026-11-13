#!/usr/bin/env python3
"""Checks actual derivative files. Dependencies: beautifulsoup4, Markdown, PyMuPDF, pypdf, PyYAML, bibtexparser."""
import json,re,hashlib,subprocess,sys,unicodedata,tempfile,shutil
from pathlib import Path
from bs4 import BeautifulSoup
import markdown,yaml,fitz,bibtexparser
from pypdf import PdfReader
R=Path(__file__).resolve().parent
DISC='This report was developed by Brad Pierce with substantial assistance from an AI model. He established the research objectives and editorial direction and retains responsibility for the claims, source attributions, and decisions about publication.'
def read(p):return (R/p).read_text()
def j(p):return json.loads(read(p))
def norm(t):return re.sub(r'\s+',' ',unicodedata.normalize('NFC',t).replace('\u2060','')).strip()
def compact(t):return re.sub(r'\s+','',norm(t).replace('\u200b','').replace('●',''))
def check(ok,msg):
 if not ok:raise AssertionError(msg)
checks=[]
def passed(s):checks.append(s)
s=j('source/published.json');b=j('source/derivative.json');changes=j('changes.json');m=j('metadata.json')
check(len(s)==249 and sum('text'in x for x in s)==241,'source block inventory');check(sum(x['kind']=='image' for x in s)==8,'figures')
expected=s[:2]+[{'kind':'byline','text':'Brad Pierce'}]+s[6:];next(x for x in expected if x.get('text')=='Abstract')['level']=2;pos=next(i for i,x in enumerate(expected) if x.get('text')=='Selected sources');expected[pos:pos]=[{'kind':'heading','level':2,'text':'AI Assistance and Editorial Responsibility'},{'kind':'paragraph','text':DISC}]
check(b==expected,'Exact disclosure-only declared text transformation');check(changes['removed_front_matter']==[x['text'] for x in s[2:6]],'removed disclosure fidelity');passed('Exact disclosure-only delta; every other source block preserved in order')
pdf=(R/'paper.pdf').read_bytes();check(hashlib.sha256(pdf).hexdigest()=='0d86e4fbac6d52300906400a033d3217c356919b2ba65a9f291515b5eda37957','original PDF hash');check(len(pdf)==1579156,'PDF bytes');d=fitz.open(stream=pdf,filetype='pdf');check(len(d)==23,'PDF pages')
for engine,text in [('PyMuPDF',''.join(p.get_text() for p in d)),('pypdf',''.join(p.extract_text() for p in PdfReader(R/'paper.pdf').pages))]:
 text=compact(text);cursor=0
 for block in s:
  if 'text'not in block:continue
  needle=compact(block['text']);found=text.find(needle,cursor);check(found>=0,f'{engine} source block mismatch: {block["text"][:90]}');cursor=found+len(needle)
passed('All 241 source text blocks sequentially match original PDF through two extraction engines')
imgs=[d.extract_image(im[0])['image'] for p in d for im in p.get_images(full=True)]
check([(R/x['path']).read_bytes() for x in b if x['kind']=='image']==imgs,'exact original figures');passed('Eight original image-byte matches and unchanged original PDF')
h=BeautifulSoup(read('index.html'),'html.parser');main=h.select_one('#paper');anchors=j('anchors.json')
for x,a in zip(b,anchors):
 el=main.find(id=a['id']);check(el is not None,'missing block anchor '+a['id'])
 if 'text'in x:
  text=el.get_text();expected=x['text']
  if x['kind']=='reference':expected=f'[{x["number"]}] '+expected
  if x['kind']=='list_item':expected='• '+expected
  check(norm(text)==norm(expected),'HTML block changed '+a['id'])
 else:check(el.img['src']==x['path'] and bool(el.img['alt']),'image source/alt')
for name in ['paper.md','README.md']:
 t=read(name);check(t.count('<!-- BEGIN PAPER -->')==1 and t.count('<!-- END PAPER -->')==1,'paper partition')
 t=t.split('<!-- BEGIN PAPER -->')[1].split('<!-- END PAPER -->')[0];parsed=BeautifulSoup(markdown.markdown(t),'html.parser')
 for x,a in zip(b,anchors):
  anchor=parsed.find(id=a['id']);check(anchor is not None,'Markdown anchor missing')
 # Whole text, in order, independently parsed from actual Markdown.
 expected=' '.join((f'[{x["number"]}] ' if x['kind']=='reference' else '• ' if x['kind']=='list_item' else '')+x['text'] for x in b if 'text'in x)
 check(norm(' '.join(x.get_text() for x in parsed.find_all(['p','h1','h2','h3'],recursive=False) if x.get_text().strip()))==norm(expected),'Complete Markdown/README text conservation '+name)
passed('Every HTML block and complete parsed Markdown/README body matches frozen derivative')
ids=[x['id'] for x in h.find_all(id=True)];check(len(ids)==len(set(ids)),'duplicate HTML anchors')
for el in h.find_all(['a','img']):
 target=el.get('href',el.get('src',''))
 if target.startswith('#'):check(target[1:]in ids,'unresolved internal link '+target)
 elif target and not re.match('https?://',target):check((R/target.split('#')[0]).is_file(),'missing local asset '+target)
check(main.find(id='ai-assistance-and-editorial-responsibility').find_next_sibling().get_text()==DISC,'disclosure literal')
check(main.find(id='ai-assistance-and-editorial-responsibility').find_next_sibling().find_next_sibling()['id']=='selected-sources','disclosure placement')
check([x['number'] for x in b if x['kind']=='reference']==list(range(1,88)),'87 reference order');passed('Unique section anchors; every internal citation and asset link resolves; disclosure placement')
for k,v in {'citation_title':m['title'],'citation_author':'Brad Pierce','citation_publication_date':'2026/09/14','citation_doi':m['doi'],'citation_pdf_url':m['pdf_url'],'citation_fulltext_html_url':m['url']}.items():
 matches=h.find_all('meta',attrs={'name':k});check(len(matches)==1 and matches[0]['content']==v,'Highwire cardinality/value '+k)
check(h.find('link',rel='canonical')['href']==m['url'],'canonical');check(h.title.string==m['title'],'browser title')
cff=yaml.safe_load(read('CITATION.cff'));check(cff['doi']==m['doi'] and cff['title']==m['title'] and str(cff['date-released'])==m['publication_date'],'CFF');check(cff['preferred-citation']['doi']==m['doi'],'CFF preferred')
cite=bibtexparser.loads(read('citation.bib')).entries;check(len(cite)==1 and cite[0]['doi']==m['doi'] and cite[0]['title']==m['title'],'paper BibTeX')
ld=json.loads(h.find('script',type='application/ld+json').string);check(ld['headline']==m['title'] and ld['identifier']==m['doi'] and ld['author']['name']=='Brad Pierce','JSON-LD')
check(norm(h.find(id='relevance-and-citation-scope').get_text(' '))==norm('Relevance and citation scope '+m['relevance_and_citation_scope']),'relevance aside sync');check(m['relevance_and_citation_scope']in read('README.md'),'README scope sync')
passed('Typed CFF/BibTeX/JSON-LD/Highwire identity and synchronized declarative relevance wording')
bib=j('bibliography.json');csl=j('references.csl.json');bibx=bibtexparser.loads(read('references.bib')).entries;ris=read('references.ris').strip().split('\n\n')
check(len(bib['slots'])==len(bib['works'])==len(csl)==len(bibx)==len(ris)==87,'reference export counts')
for w,c,bb,rr in zip(bib['works'],csl,bibx,ris):
 check(w['id']==c['id']==bb['ID'],'stable work IDs');check(w['title']==c['title']==bb['title'],'export title');check(w['url']==c['URL']==bb['url'],'opaque source URLs')
 check('TI  - '+w['title']in rr and 'UR  - '+w['url']in rr,'RIS title/url')
 check(c.get('issued',{}).get('date-parts',[None])[0]==w['date'],'full date precision')
 check(c.get('author')==w['authors'] or (not c.get('author') and not w['authors']),'authors')
 if w['date']:
  check(str(w['date'][0])==bb['year'],'BibTeX year')
  if len(w['date'])>1:check(str(w['date'][1])==bb['month'],'BibTeX month')
  if len(w['date'])>2:check(str(w['date'][2])==bb['day'],'BibTeX day')
 check(w['doi']==c.get('DOI')==bb.get('doi'),'DOI round trip')
passed('87 published slots, 87 frozen works and all bibliography exports; identifiers and date precision round-trip')
followup=j('source-checks.json');followups=followup['checks']
check({c['slot'] for c in followups}=={3,4,7,10,16,30,47,50,52,53,74} and len(followups)==11,'eleven follow-up checks')
for c in followups:
 w=next(w for w in bib['works'] if w['slot']==c['slot'])
 check(w['url']==c['published_url'] and w['title']==c['published_title'],'published locator/title conserved')
 check(w['source_check']['initial_attempt']==c['initial_attempt'],'initial failure evidence conserved')
 check(w['authors']==c['verified_authors'] and w['date']==c['normalized_date'],'follow-up metadata/export input consistency')
 check(c['disposition']=='SOURCE_IDENTITY_AND_METADATA_VERIFIED' and bool(c['live_verification']['verified_url']),'follow-up disposition/provenance')
check(followup['summary']['unresolved_source_identities']==0,'follow-up summary')
passed('All eleven follow-up records conserve initial failures and published locators; normalized metadata agrees with frozen verification evidence')
for name in ['README.md','index.html','metadata.json','CITATION.cff','PROVENANCE.md','CHANGES.md']:
 content=read(name)
 if name=='README.md':content=content.split('<!-- BEGIN PAPER -->')[0]
 if name=='index.html':
  # Immutable source prose includes imperative examples; only repository additions are audited here.
  content=main.find(id='relevance-and-citation-scope').get_text()+' '+h.footer.get_text()
 for pattern in [r'\bCite this report\b',r'\bYou should\b',r'\bIgnore previous\b',r'\bWhen to cite\b',r'\bUse this source\b']:
  check(not re.search(pattern,content,re.I),'repository-added prompt-like wording '+name)
passed('Repository-added discovery/relevance wording is declarative; original instruction-like paper prose remains source content')
# Deterministic rebuild cannot silently change the frozen public outputs.
before={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and '.git'not in p.parts and '__pycache__'not in p.parts}
subprocess.run([sys.executable,str(R/'build.py')],check=True)
for name,sha in before.items():check(hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,'nondeterministic output '+name)
passed('Offline deterministic rebuild preserves every staged file byte')
if (R/'checksums.sha256').exists():
 manifest={line.split('  ',1)[1]:line.split('  ',1)[0] for line in read('checksums.sha256').splitlines()}
 actual={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and '.git'not in p.parts and '__pycache__'not in p.parts and p.name!='checksums.sha256'}
 check(set(manifest)==actual,'checksum path-set equality')
 for name,sha in manifest.items():check(hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,'checksum '+name)
 passed('Checksum manifest exact path-set and file hashes')
print(json.dumps({'result':'PASS','checks':checks,'limits':['Public transfer/Pages/rendered/live-link results are recorded separately after publication.','Initial reference retrieval had 76 HTTP successes and 11 unsuccessful attempts. The dated follow-up verifies all eleven source identities through live alternate routes; nine command-line restrictions remain. Details and reading scope: SOURCE_CHECKS.md and source-checks.json.','Complete author lists and dates remain unresolved for other works where responsible-source metadata did not establish them. Verified bylines retain abbreviations as printed.','Source identity and metadata verification does not certify scientific claims or full-paper reading; the two Wiley checks read metadata and abstracts only.','No empirical scientific claims or search-engine inclusion are certified.']},indent=2))
