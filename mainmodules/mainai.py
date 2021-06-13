import re, os
from fuzzywuzzy import fuzz

def getanswer(text):
    try:
        text=text.lower().strip()
        if os.path.exists('boltun.txt'):          
            a=0
            n=0
            nn=0
            file=open('boltun.txt','r', encoding='utf-8')
            mas=file.read().split('\n')
            
            for q in mas:
                if('u: ' in q):
                    aa=(fuzz.token_sort_ratio(q.replace('u: ',''), text))
                    if(aa>a and aa!=a):
                        a=aa
                        nn=n
                n=n+1
            s=mas[nn+1]
            return s
        else:
            return 'Нет ответа'
    except:
        return 'Нет ответа'

