#!/usr/bin/env python3
"""Deterministic derivative builder; no network access."""
import json,re,html,hashlib,unicodedata
from pathlib import Path
R=Path(__file__).resolve().parent
TITLE='What Language Should an Agent Act In?'
SLUG='what-language-should-an-agent-act-in'
DOI='10.5281/zenodo.22837693'
URL=f'https://bradpierce.ai/{SLUG}/'
REPO=f'https://github.com/bradpierce-ai-eda/{SLUG}'
DISCLOSURE='This report was developed by Brad Pierce with substantial assistance from an AI model. He established the research objectives and editorial direction and retains responsibility for the claims, source attributions, and decisions about publication.'
S=json.loads((R/'source/published.json').read_text())
OLD=[b['text'] for b in S[2:6]]
assert OLD[0]=='Author and collaboration' and OLD[2]=='Contribution statement'
B=S[:2]+[{'kind':'byline','text':'Brad Pierce'}]+S[6:]
pos=next(i for i,b in enumerate(B) if b.get('text')=='Selected sources')
next(x for x in B if x.get('text')=='Abstract')['level']=2
B[pos:pos]=[{'kind':'heading','level':2,'text':'AI Assistance and Editorial Responsibility'}, {'kind':'paragraph','text':DISCLOSURE}]
def dump(path,obj):(R/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def write(path,s):(R/path).write_text(s,encoding='utf-8')
def slug(t):return re.sub(r'[^\w]+','-',unicodedata.normalize('NFKD',t).lower(),flags=re.U).strip('-')
# Frozen blocks are sourced solely from the unchanged publication plus the declared disclosure delta.
dump('source/derivative.json',B)
refs=[b for b in B if b['kind']=='reference']
relevance='''Repository-added context, separate from the published paper.\n\nThis position paper is relevant to agent-facing representations, action substrates, useful freedom, Trustworthy Change Yield, AI coding agents, and matched-budget RTL evaluation. It is an appropriate citation for the paper’s synthesis and proposed controlled comparison of first-pass correctness with independently accepted change under matched budgets and risk constraints. Its ranking-reversal prediction and useful-freedom hypothesis are an experimental agenda, not demonstrated results. Specific findings and product claims remain attributable to the primary sources in the published bibliography.\n\nThe DOI-linked Zenodo version is the publication of record. The HTML and Markdown derivative modernize the AI disclosure with Brad Pierce’s authorization; the mirrored PDF preserves the original publication unchanged.'''
notice='This is a machine-readable derivative of the Zenodo publication of record. The AI disclosure in the text edition is modernized; substantive paper content is preserved. The PDF retains the original disclosure.'
citation=f'Pierce, Brad. (2026). {TITLE} (Version 1.0) [Preprint]. Zenodo. https://doi.org/{DOI}'
meta={'title':TITLE,'subtitle':B[1]['text'],'author':[{'given':'Brad','family':'Pierce','orcid':'https://orcid.org/0009-0009-7427-2969'}],'publication_date':'2026-09-14','version':'1.0','type':'preprint','doi':DOI,'url':URL,'repository':REPO,'zenodo_record':'https://zenodo.org/records/22837693','pdf_url':URL+'paper.pdf','authoritative_pdf_url':'https://zenodo.org/records/22837693/files/what-language-should-an-agent-act-in.pdf?download=1','license':'CC-BY-4.0','abstract':next(b['text'] for i,b in enumerate(B) if i and B[i-1].get('text')=='Abstract'),'keywords':['agent-facing representations','useful freedom','trustworthy change yield','RTL design','AI coding agents','matched-budget evaluation','SystemVerilog'],'preferred_citation':citation,'relevance_and_citation_scope':relevance,'text_edition_alteration':'Modernized AI disclosure; unchanged substantive content. Original PDF preserved.'}
dump('metadata.json',meta)
dump('changes.json',{'authorized_change':'AI disclosure only','removed_front_matter':OLD,'replacement_byline':'Brad Pierce','added_disclosure_heading':'AI Assistance and Editorial Responsibility','added_disclosure_paragraph':DISCLOSURE,'placement':'Immediately before the original Selected sources bibliography; original Acknowledgment and scope remains after the bibliography.','basis':{'url':'https://bradpierce.ai/when-design-exploration-gets-cheap/','github_source':'https://github.com/bradpierce-ai-eda/when-design-exploration-gets-cheap/blob/main/index.html','location':'Contribution statement','source_sha256':json.loads((R/'source/authority.json').read_text())['disclosure_reference_sha256']},'representation_changes':['Heading levels mapped to HTML/Markdown semantics; stable section, figure, paragraph and reference anchors added.','The two original collaboration panels are replaced by a human author byline and the modernized disclosure.','Automatic reference labels 1–47 are made explicit, retaining published numbering through 87.','Public bibliographic front matter, citation scope, links and provenance are outside the paper body.','PDF-extracted original figure images retained without redrawing.'],'substantive_changes':[],'pdf_changed':False})
# Canonical rendering from exact runs. Added citation links preserve every visible source character.
def link_citations(t):
 def m(x):
  nums=re.findall(r'\d+',x.group())
  if len(nums)==1:return f'<a href="#ref-{int(nums[0])}">{x.group()}</a>'
  return x.group()
 return re.sub(r'\[\d+(?:[–,\- ]+\d+)*\]',m,t)
def inline(b):
 if 'runs' not in b:return link_citations(html.escape(b['text']))
 out=''
 for q in b['runs']:
  t=html.escape(q['text'].replace('\n',''))
  if q.get('bold'):t=f'<strong>{t}</strong>'
  if q.get('italic'):t=f'<em>{t}</em>'
  if q.get('url') and re.fullmatch(r'\[\d+\]',q['text'].strip()) and b['kind']!='reference':t=link_citations(t)
  elif q.get('url'):t=f'<a href="{html.escape(q["url"],quote=True)}">{t}</a>'
  else:t=link_citations(t)
  out+=t
 return out.strip()
htmls=[];md=[];anchors=[]
for i,b in enumerate(B):
 k=b['kind'];t=b.get('text','');x=inline(b) if t else ''
 if k=='image':
  n=b['figure'];cap=next(z['text'] for z in B[i+1:] if z.get('kind')=='caption');a=f'figure-{n}';h=f'<figure id="{a}"><img src="{b["path"]}" alt="{html.escape(cap,quote=True)}" width="1600" height="900"></figure>';m=f'<a id="{a}"></a>\n\n![{cap}]({b["path"]})'
 else:
  a='ref-'+str(b['number']) if k=='reference' else (slug(t) if k in ['title','heading'] else f'paragraph-{i:03}')
  if k=='title':tag='h1'
  elif k=='heading':tag='h'+str(min(b.get('level',2),3))
  else:tag='p'
  if k=='reference':x=f'[{b["number"]}] '+x
  if k=='list_item':x='• '+x
  h=f'<{tag} id="{a}" class="{k}">{x}</{tag}>'
  if k in ['title','heading']:m='#'*(1 if k=='title' else min(b.get('level',2),3))+' '+x
  else:m=x
  m=f'<a id="{a}"></a>\n\n'+m
 htmls.append(h);md.append(m);anchors.append({'id':a,'kind':k,'text':t if t else f'Figure {b["figure"]}'})
dump('anchors.json',anchors)
front=f'Published 2026-09-14 · DOI: [{DOI}](https://doi.org/{DOI})\n\n{notice}\n\nPreferred citation: {citation}'
body='\n\n'.join(md)
write('paper.md',front+'\n\n<!-- BEGIN PAPER -->\n\n'+body+'\n\n<!-- END PAPER -->\n')
write('README.md',f'# {TITLE}\n\n'+front.replace('\n\n'+notice,'')+'\n\n[Static full text]('+URL+') · [Original PDF](paper.pdf) · [Zenodo record](https://zenodo.org/records/22837693) · [Alteration record](CHANGES.md)\n\n## Relevance and citation scope\n\n'+relevance+'\n\n## Paper text\n\n<!-- BEGIN PAPER -->\n\n'+body+'\n\n<!-- END PAPER -->\n')
aside='<aside id="relevance-and-citation-scope"><h2>Relevance and citation scope</h2>'+''.join('<p>'+html.escape(p)+'</p>' for p in relevance.split('\n\n'))+'</aside>'
abstractindex=next(i for i,b in enumerate(B) if b.get('text')=='Abstract')+1
article='\n'.join(htmls[:3])+f'<p class="bibliographic">Published 2026-09-14 · DOI: <a href="https://doi.org/{DOI}">{DOI}</a></p>'+ '\n'.join(htmls[3:abstractindex+1])+aside+f'<p>Preferred citation: {html.escape(citation)}</p><p><a href="paper.pdf">Unchanged original PDF</a> · <a href="https://zenodo.org/records/22837693">Zenodo record</a> · <a href="paper.md">Markdown</a> · <a href="CHANGES.md">Alteration record</a> · <a href="#selected-sources">References: Selected sources</a></p>'+ '\n'.join(htmls[abstractindex+1:])
ld={'@context':'https://schema.org','@type':'ScholarlyArticle','headline':TITLE,'alternativeHeadline':meta['subtitle'],'author':{'@type':'Person','name':'Brad Pierce','sameAs':meta['author'][0]['orcid']},'datePublished':'2026-09-14','identifier':DOI,'sameAs':['https://doi.org/'+DOI,meta['zenodo_record']],'url':URL,'contentUrl':URL+'paper.pdf','license':'https://creativecommons.org/licenses/by/4.0/','abstract':meta['abstract'],'keywords':meta['keywords'],'isBasedOn':meta['zenodo_record']}
tags={'citation_title':TITLE,'citation_author':'Brad Pierce','citation_publication_date':'2026/09/14','citation_doi':DOI,'citation_pdf_url':URL+'paper.pdf','citation_fulltext_html_url':URL,'description':meta['abstract'],'keywords':', '.join(meta['keywords']),'og:title':TITLE,'og:url':URL,'og:type':'article'}
head='\n'.join(f'<meta {"property" if k.startswith("og:") else "name"}="{k}" content="{html.escape(v,quote=True)}">' for k,v in tags.items())
write('index.html','<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<title>'+TITLE+'</title>\n<link rel="canonical" href="'+URL+'">\n'+head+'\n<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False)+'</script>\n<style>body{font:18px/1.6 system-ui,sans-serif;color:#202124;max-width:960px;margin:40px auto;padding:0 22px}h1{line-height:1.2}h2,h3{line-height:1.3;margin-top:2em}a{color:#1756a9;overflow-wrap:anywhere}.subtitle{color:#555;font-size:1.2em}.byline{font-weight:600}aside{border-left:3px solid #ccc;padding:0 1em;margin:2em 0}figure{margin:1.5em 0}img{max-width:100%;height:auto}.caption{font-size:.9em;color:#444}.reference{padding-left:2.5em;text-indent:-2.5em;overflow-wrap:anywhere}.list_item{padding-left:1em}footer{border-top:1px solid #ddd;margin-top:3em;font-size:.9em}</style></head><body><main id="paper">'+article+'</main><footer><p>© 2026 Brad Pierce. Source publication: <a href="https://doi.org/'+DOI+'">'+DOI+'</a>. <a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International</a>. The text edition’s disclosed alteration is limited to AI disclosure. The original PDF is unchanged.</p></footer></body></html>\n')
write('CITATION.cff',f'''cff-version: 1.2.0
message: "The DOI-linked Zenodo preprint is the publication of record."
type: article
title: "{TITLE}"
authors:
  - family-names: Pierce
    given-names: Brad
    orcid: https://orcid.org/0009-0009-7427-2969
doi: {DOI}
date-released: 2026-09-14
version: "1.0"
url: https://doi.org/{DOI}
license: CC-BY-4.0
preferred-citation:
  type: generic
  title: "{TITLE}"
  authors:
    - family-names: Pierce
      given-names: Brad
  doi: {DOI}
  year: 2026
  month: 9
  date-published: 2026-09-14
  url: https://doi.org/{DOI}
  publisher:
    name: Zenodo
''')
write('citation.bib',f'''@misc{{pierce2026agentlanguage,
  author = {{Pierce, Brad}},
  title = {{{TITLE}}},
  year = {{2026}},
  month = sep,
  day = {{14}},
  doi = {{{DOI}}},
  url = {{https://doi.org/{DOI}}},
  publisher = {{Zenodo}},
  version = {{1.0}},
  note = {{Preprint; publication of record.}}
}}
''')
write('LICENSE','© 2026 Brad Pierce.\n\nThe source publication is licensed under Creative Commons Attribution 4.0 International (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/ .\n\nThe derivative identifies its source and explicitly documents the AI-disclosure alteration. The original PDF is unchanged. Third-party material retains its source attribution.\n')
write('CHANGES.md','# Alterations from the Zenodo publication\n\nThe Zenodo source and mirrored `paper.pdf` are unchanged. With Brad Pierce’s authorization, the text editions replace the opening “Author and collaboration” and “Contribution statement” panels with a human author byline and the following section immediately before the original “Selected sources” bibliography:\n\n## AI Assistance and Editorial Responsibility\n\n'+DISCLOSURE+'\n\nAll substantive paragraphs, the complete abstract, eight original figures and their captions, 87 published references, and the concluding “Acknowledgment and scope” are preserved in their original order. The full removed wording, exact replacement, disclosure source, and representation changes are recorded in [changes.json](changes.json). Bibliographic front matter and relevance context are clearly separate repository additions.\n\nThe updated wording matches the current [reference article](https://bradpierce.ai/when-design-exploration-gets-cheap/) and its [GitHub HTML source](https://github.com/bradpierce-ai-eda/when-design-exploration-gets-cheap/blob/main/index.html). That repository’s paper.md contained older contribution wording at acquisition; it was not used as the modern-disclosure authority.\n')
write('sitemap.xml',f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{URL}</loc></url><url><loc>{URL}paper.pdf</loc></url></urlset>\n')
write('robots.txt','User-agent: *\nAllow: /\nSitemap: https://bradpierce.ai/sitemap.xml\n')
write('.nojekyll','');write('.gitignore','__pycache__/\n*.py[cod]\n.git/\n')
# Bibliography views are generated only from the frozen source dataset, never from live HTTP.
bib=json.loads((R/'bibliography.json').read_text());write('references.md','# Selected sources\n\n'+'\n\n'.join(f'[{b["number"]}] {inline(b)}' for b in refs)+'\n')
def esc(t):return t.replace('\\','\\textbackslash{}').replace('{','\\{').replace('}','\\}')
bibtex=[];csl=[];ris=[]
for w in bib['works']:
 fields={'title':w['title'],'url':w['url'],'note':'Published attribution: '+w['published_attribution']+' '+w['metadata_note']}
 if w.get('doi'):fields['doi']=w['doi']
 if w.get('authors'):
  fields['author']=' and '.join((a.get('family','')+', '+a.get('given','')).strip(', ') if 'family'in a else '{'+a['literal']+'}' for a in w['authors'])
 if w.get('date'):fields.update(year=w['date'][0],**({'month':w['date'][1]} if len(w['date'])>1 else {}),**({'day':w['date'][2]} if len(w['date'])>2 else {}))
 bibtex.append('@misc{'+w['id']+',\n'+',\n'.join('  '+k+' = {'+(str(v) if k in ['url','doi'] else esc(str(v)))+'}' for k,v in fields.items())+'\n}')
 item={'id':w['id'],'type':'webpage','title':w['title'],'URL':w['url'],'note':fields['note']}
 if w.get('authors'):item['author']=w['authors']
 if w.get('date'):item['issued']={'date-parts':[w['date']]}
 if w.get('doi'):item['DOI']=w['doi']
 csl.append(item)
 rr=['TY  - GEN','ID  - '+w['id'],'TI  - '+w['title'],'UR  - '+w['url'],'N1  - '+fields['note']]
 for a in (w.get('authors') or []):rr.append('AU  - '+(a['literal']+',' if 'literal'in a else a.get('family','')+', '+a.get('given','')))
 if w.get('date'):rr.append('PY  - '+'/'.join(map(str,w['date'])))
 if w.get('doi'):rr.append('DO  - '+w['doi'])
 rr.append('ER  - ');ris.append('\n'.join(rr))
write('references.bib','\n\n'.join(bibtex)+'\n');dump('references.csl.json',csl);write('references.ris','\n\n'.join(ris)+'\n')
authority=json.loads((R/'source/authority.json').read_text())
provenance={**authority,'paper_sha256':hashlib.sha256((R/'paper.pdf').read_bytes()).hexdigest(),'source_blocks_sha256':hashlib.sha256((R/'source/published.json').read_bytes()).hexdigest(),'derivative_blocks_sha256':hashlib.sha256((R/'source/derivative.json').read_bytes()).hexdigest(),'date_generated':'2026-11-12','transformation':'Native release structure matched sequentially against actual Zenodo PDF; original PDF images extracted with PyMuPDF; deterministic Python static HTML/Markdown/bibliography generation.','manual_corrections':'Only the explicitly authorized AI disclosure change; automatic bibliography labels made explicit; no substantive prose correction.','counts':{'pdf_pages':23,'original_text_blocks':241,'figures':8,'published_reference_slots':87},'validation_status':'Local validation evidence in VALIDATION.json; public transfer and live verification recorded separately in the durable Drive execution record.'}
dump('provenance.json',provenance)
write('PROVENANCE.md','# Provenance\n\nPublication of record: [Zenodo 22837693](https://zenodo.org/records/22837693), version 1.0, published 2026-09-14, DOI [10.5281/zenodo.22837693](https://doi.org/10.5281/zenodo.22837693). Author: Brad Pierce. Originating initiative: F080. Source license: CC BY 4.0.\n\nOriginal file: `what-language-should-an-agent-act-in.pdf`, 1,579,156 bytes, 23 pages. The mirrored `paper.pdf` SHA-256 is `0d86e4fbac6d52300906400a033d3217c356919b2ba65a9f291515b5eda37957`; its MD5 `7a8e175dc6b7d75e9a953e598cf9a09a` matches the Zenodo file record.\n\nAll 241 source text blocks matched the downloaded PDF in sequence after PDF line-wrap whitespace and bullet/automatic-label normalization. Eight original figure images are retained. Source bibliography labels and links are preserved. Full machine-readable provenance is in [provenance.json](provenance.json); the authorized disclosure alteration is in [CHANGES.md](CHANGES.md). The source publication itself has not been modified.\n\nThe frozen bibliography retains each exact published reference independently of normalized fields. Missing dates and complete authorship remain explicitly unresolved where a responsible source did not verify them; no inferred dates or names are installed.\n')
