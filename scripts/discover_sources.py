"""One-time official report URL discovery; no crawling beyond named IR pages."""
import concurrent.futures
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin

PAGES = {
    'amazon':'https://ir.aboutamazon.com/annual-reports-proxies-and-shareholder-letters/default.aspx',
    'alphabet':'https://abc.xyz/investor/earnings/',
    'nvidia':'https://investor.nvidia.com/financial-info/annual-reports-and-proxies/default.aspx',
    'salesforce':'https://investor.salesforce.com/financials/default.aspx',
    'accenture':'https://www.investor.accenture.com/news-and-events/annual-shareholder-meeting',
    'ibm':'https://www.ibm.com/investor/services/annual-report',
    'bac':'https://investor.bankofamerica.com/annual-reports-and-proxy-statements',
    'walmart':'https://stock.walmart.com/financials/annual-reports-and-proxies/default.aspx',
}
def run(item):
    name,url=item
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (public research; dui@szu.edu.cn)'})
        soup=BeautifulSoup(urllib.request.urlopen(req,timeout=20).read(),'html.parser')
        out=[]
        for a in soup.find_all('a',href=True):
            text=a.get_text(' ',strip=True); href=urljoin(url,a['href'])
            if ('annual' in (text+' '+href).lower() or '10-k' in text.lower()) and any(y in str(a.parent.parent) for y in ['2023','2024']):
                out.append((text,href))
        return name,list(dict.fromkeys(out))[:35]
    except Exception as exc:return name,str(exc)
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(run,PAGES.items()):print(row,flush=True)
