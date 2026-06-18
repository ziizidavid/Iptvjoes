import re,requests
from concurrent.futures import ThreadPoolExecutor,as_completed
SOURCE='https://raw.githubusercontent.com/doms9/iptv/refs/heads/default/M3U8/events.m3u8'
KEEP=['football','soccer','fifa','world cup','piala dunia','uefa','champions','premier league','la liga','serie a','bundesliga','afc','euro','copa america']
REMOVE=['cricket','baseball','mlb','nfl','nhl','rugby','golf','tennis']

def alive(url):
    try:
        return requests.get(url,timeout=8,stream=True,headers={'User-Agent':'Mozilla/5.0'}).status_code in (200,206)
    except: return False

raw=requests.get(SOURCE,timeout=20).text.splitlines()
blocks=[];i=0
while i<len(raw):
    if raw[i].startswith('#EXTINF'):
      b=[raw[i]];j=i+1
      while j<len(raw) and not raw[j].startswith('#EXTINF'): b.append(raw[j]);j+=1
      txt=' '.join(b).lower()
      if not any(x in txt for x in REMOVE) and any(x in txt for x in KEEP): blocks.append(b)
      i=j
    else:i+=1
valid=[]
with ThreadPoolExecutor(max_workers=20) as ex:
  fut=[]
  for b in blocks:
    url=next((x for x in reversed(b) if x.startswith('http')),None)
    txt=b[0].lower()
    keep4k=any(x in txt for x in ['4k','uhd','2160p'])
    fut.append((b,keep4k,url,ex.submit(alive,url) if url and not keep4k else None))
  for b,keep4k,url,f in fut:
    ok=keep4k or (f and f.result())
    if ok:
      b[0]=re.sub(r'group-title="[^"]*"','',b[0])
      valid.extend(b);valid.append('')

with open('IPTV.m3u','r',encoding='utf-8') as f: base=f.read().split('# --- AUTO GENERATED ---')[0].rstrip()
with open('IPTV.m3u','w',encoding='utf-8') as f:
  f.write(base+'\n\n# --- AUTO GENERATED ---\n'+'\n'.join(valid))
print('updated')
