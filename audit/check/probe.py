import urllib.request,urllib.error,ssl,socket,csv,sys
from concurrent.futures import ThreadPoolExecutor
URLS=[l.strip() for l in open('/home/user/test/audit/check/urls.txt') if l.strip()]
ctx=ssl.create_default_context()
try: ctx.load_verify_locations('/root/.ccr/ca-bundle.crt')
except Exception: pass
UA='Mozilla/5.0 (compatible; LinkAudit/1.0)'
def probe(u):
    for meth in ('HEAD','GET'):
        try:
            rq=urllib.request.Request(u,method=meth,headers={'User-Agent':UA})
            with urllib.request.urlopen(rq,timeout=20,context=ctx) as r:
                return (u,r.status,'')
        except urllib.error.HTTPError as e:
            if meth=='HEAD' and e.code in (403,405,501): continue
            return (u,e.code,'http')
        except urllib.error.URLError as e:
            return (u,0,str(e.reason)[:60])
        except (socket.timeout,TimeoutError):
            return (u,0,'timeout')
        except Exception as e:
            return (u,0,type(e).__name__)
    return (u,0,'unknown')
res=[]
with ThreadPoolExecutor(max_workers=24) as ex:
    for i,r in enumerate(ex.map(probe,URLS),1):
        res.append(r)
        if i%100==0: print(i,flush=True)
w=csv.writer(open('/home/user/test/audit/check/status.csv','w',newline=''),delimiter=';')
w.writerow(['url','status','err']); w.writerows(res)
ok=sum(1 for _,s,_ in res if 200<=s<400)
print('checked',len(res),'live',ok,'dead',len(res)-ok)
