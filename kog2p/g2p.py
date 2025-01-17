# -*- coding: utf-8 -*-
'''
g2p.py
~~~~~~~~~~

This script converts Korean graphemes to romanized phones and then to pronunciation.

    (1) graph2phone: convert Korean graphemes to romanized phones
    (2) phone2prono: convert romanized phones to pronunciation
    (3) graph2phone: convert Korean graphemes to pronunciation

Usage:  $ python g2p.py '스물 여덟째 사람'
        (NB. Please check 'rulebook_path' before usage.)

Yejin Cho (ycho@utexas.edu)
Jaegu Kang (jaekoo.jk@gmail.com)
Hyungwon Yang (hyung8758@gmail.com)
Yeonjung Hong (yvonne.yj.hong@gmail.com)

Created: 2016-08-11
Last updated: 2019-01-31 Yejin Cho

* Key updates made:
    - Executable in both Python 2 and 3.
    - G2P Performance test available ($ python g2p.py test)
    - G2P verbosity control available

'''

import re
import math


def isHangul(charint):
    hangul_init = 44032
    hangul_fin = 55203
    return charint >= hangul_init and charint <= hangul_fin


def checkCharType(var_list):
    #  1: whitespace
    #  0: hangul
    # -1: non-hangul
    checked = []
    for i in range(len(var_list)):
        if var_list[i] == 32:  # whitespace
            checked.append(1)
        elif isHangul(var_list[i]):  # Hangul character
            checked.append(0)
        else:  # Non-hangul character
            checked.append(-1)
    return checked


def graph2phone(graphs):
    # Encode graphemes as utf8
    try:
        graphs = graphs.decode('utf8')
    except AttributeError:
        pass

    integers = []
    for i in range(len(graphs)):
        integers.append(ord(graphs[i]))

    # Romanization (according to Korean Spontaneous Speech corpus; 성인자유발화코퍼스)
    phones = ''
    ONS = ['k0', 'kk', 'nn', 't0', 'tt', 'rr', 'mm', 'p0', 'pp',
           's0', 'ss', 'oh', 'c0', 'cc', 'ch', 'kh', 'th', 'ph', 'h0']
    NUC = ['aa', 'qq', 'ya', 'yq', 'vv', 'ee', 'yv', 'ye', 'oo', 'wa',
           'wq', 'wo', 'yo', 'uu', 'wv', 'we', 'wi', 'yu', 'xx', 'xi', 'ii']
    COD = ['', 'kf', 'kk', 'ks', 'nf', 'nc', 'nh', 'tf',
           'll', 'lk', 'lm', 'lb', 'ls', 'lt', 'lp', 'lh',
           'mf', 'pf', 'ps', 's0', 'ss', 'oh', 'c0', 'ch',
           'kh', 'th', 'ph', 'h0']

    # Pronunciation
    idx = checkCharType(integers)
    iElement = 0
    while iElement < len(integers):
        if idx[iElement] == 0:  # not space characters
            base = 44032
            df = int(integers[iElement]) - base
            iONS = int(math.floor(df / 588)) + 1
            iNUC = int(math.floor((df % 588) / 28)) + 1
            iCOD = int((df % 588) % 28) + 1

            s1 = '-' + ONS[iONS - 1]  # onset
            s2 = NUC[iNUC - 1]  # nucleus

            if COD[iCOD - 1]:  # coda
                s3 = COD[iCOD - 1]
            else:
                s3 = ''
            tmp = s1 + s2 + s3
            phones = phones + tmp

        elif idx[iElement] == 1:  # space character
            tmp = '#'
            phones = phones + tmp

        phones = re.sub('-(oh)', '-', phones)
        iElement += 1
        tmp = ''

    # 초성 이응 삭제
    phones = re.sub('^oh', '', phones)
    phones = re.sub('-(oh)', '', phones)

    # 받침 이응 'ng'으로 처리 (Velar nasal in coda position)
    phones = re.sub('oh-', 'ng-', phones)
    phones = re.sub('oh([# ]|$)', 'ng', phones)

    # Remove all characters except Hangul and syllable delimiter (hyphen; '-')
    phones = re.sub('(\W+)\-', '\\1', phones)
    phones = re.sub('\W+$', '', phones)
    phones = re.sub('^\-', '', phones)
    return phones


def phone2prono(phones, rule_in, rule_out):
    # Apply g2p rules
    for pattern, replacement in zip(rule_in, rule_out):
        # print pattern
        phones = re.sub(pattern, replacement, phones)
        prono = phones
    return prono


def addPhoneBoundary(phones):
    # Add a comma (,) after every second alphabets to mark phone boundaries
    ipos = 0
    newphones = ''
    while ipos + 2 <= len(phones):
        if phones[ipos] == u'-':
            newphones = newphones + phones[ipos]
            ipos += 1
        elif phones[ipos] == u' ':
            ipos += 1
        elif phones[ipos] == u'#':
            newphones = newphones + phones[ipos]
            ipos += 1

        newphones = newphones + phones[ipos] + phones[ipos + 1] + u','
        ipos += 2

    return newphones


def addSpace(phones):
    ipos = 0
    newphones = ''
    while ipos < len(phones):
        if ipos == 0:
            newphones = newphones + phones[ipos] + phones[ipos + 1]
        else:
            newphones = newphones + ' ' + phones[ipos] + phones[ipos + 1]
        ipos += 2

    return newphones


def graph2prono(graphs, rule_in, rule_out):
    romanized = graph2phone(graphs)
    romanized_bd = addPhoneBoundary(romanized)
    prono = phone2prono(romanized_bd, rule_in, rule_out)

    prono = re.sub(u',', u' ', prono)
    prono = re.sub(u' $', u'', prono)
    prono = re.sub(u'#', u'-', prono)
    prono = re.sub(u'-+', u'-', prono)

    prono_prev = prono
    identical = False
    loop_cnt = 1

    while not identical:
        prono_new = phone2prono(re.sub(u' ', u',', prono_prev + u','), rule_in, rule_out)
        prono_new = re.sub(u',', u' ', prono_new)
        prono_new = re.sub(u' $', u'', prono_new)

        if re.sub(u'-', u'', prono_prev) == re.sub(u'-', u'', prono_new):
            identical = True
            prono_new = re.sub(u'-', u'', prono_new)
        else:
            loop_cnt += 1
            prono_prev = prono_new

    return prono_new


def runKoG2P(graph):
    rule_in = ['ii,ll,[#-]y([aeoquv]),', '(h0,aa|t0,xx),ll,-ii,ll,', 's0,vv,ll,-ii,kf,', 'mm,uu,ll,-k0,oo,-k0,ii,',
               's0,ii,ll,-s0,ii,ll', 'k0,ii,-s0,xx,lk,', 'c0,vv,ll,-ya,kf,', 'k0,xx,mf,-yo,-ii,ll,', 'lt,-ii,',
               '(?<=nn,vv,)lb,(?=-(c0,(uu|vv),kf|t0,(uu|vv),ng))', '(?<=s0,ii,)lh,-c0,(?=xx,ng)', 't0,aa,lk,',
               '(wq|we|oo),nf,-k0,aa,c0,', 'mm,aa,tf,-h0,yv,ng,', 'k0,vv,th,-oo,s0,', 'c0,uu,ll,-nn,vv,mf,-k0,ii,',
               'h0,oo,th,-ii,-p0,uu,ll,', 's0,aa,ks,-ii,ll,', 'mm,qq,nf,-ii,pf,', 'kk,oo,ch,-ii,ph,',
               'nn,qq,-p0,oo,kf,-ya,kf,', 'h0,aa,nf,-yv,-rr,xx,mf,', 'nn,aa,mf,-c0,oo,nf,-yv,-p0,ii,',
               's0,ii,nf,-yv,-s0,vv,ng,', 's0,qq,kf,-yv,nf,-ph,ii,ll,', 't0,aa,mf,-yo,', 'nn,uu,nf,-yo,-k0,ii,',
               'vv,pf,-yo,ng,', 's0,ii,kf,-yo,ng,-yu,', 'nf,-yu,nf,-rr,ii,', '(c0|s0),(aa|oo|uu),ll,-ii,(ph|p0|pf),',
               '(?=(^|#))h0,aa,nf,-ii,ll,', '(?=(^|#))mm,aa,kf,-ii,ll,', 'mm,oo,ll,-s0,aa,ng,-s0,ii,kf,',
               'oo,s0,#ii,pf,', '(nf|ll),-yv,-s0,vv,-s0,', '(ng|mf|nf),-y([aeoquv]),', '(wv|ii),ll,-y([aeoquv]),',
               'll,-y([aeoquv]),', 'ii,ll,-c0,vv,ll,', '(th|tf|s0),-y([aeoquv]),', '(<=^|#)mm,aa,kf,-ii,ll',
               'k0,uu,-k0,xx,nf,-rr,yu,', 'k0,aa,ll,-([ct])0,xx,ng,', 'p0,aa,ll,-t0,oo,ng,', 'c0,vv,ll,-t0,oo,',
               'mm,aa,ll,-s0,aa,ll,', 'p0,uu,ll,-s0,', 'ii,ll,-s0,ii,', 'p0,aa,ll,-c0,vv,nf,',
               '(?<=(s0,ii,nf,|s0,aa,mf,)-)(c|k|t)0,', '(?<=k0,ii,mf,-)p0,', '(?<=t0,vv,-t0,xx,mf,-)c0,',
               'c0,aa,mf,-c0,aa,-rr,ii,', '(?<=(ng|ll),-)c0,(?=uu,ll,-k0,ii)', '(?<=(nf|ll),-)p0,vv,pf,',
               '(?<=(nf|tf),-)p0,(?=aa,-rr,aa,mf)', 'p0,aa,-rr,aa,mf,-k0,yv,ll,', '(?<=(mf|kf),-)p0,(?=aa,pf,)',
               '(?<=nn,uu,nf,-)t0,', 'mm,aa,kf,-yv,mf,', 'p0,aa,lb,-(t|k)0,', 'p0,aa,lb,-nn,', 'nn,vv,lb,-(t|k)0,',
               'mm,(aa|vv),s0,-ii,ss,-t0,aa,', 'mm,(aa|vv),s0,-vv,ps,-t0,aa,', 'c0,vv,c0,-vv,-mm,ii,',
               'h0,vv,s0,-uu,s0,-xx,mf,', 'k0,aa,ps,-vv,-ch,ii,', 'k0,aa,ps,-ii,ss,-nn,xx,nf,', 'c0,vv,lm,-c0,ii,',
               'oo,lm,-k0,(?=[iy])', 'k0,uu,lm,-k0,ii,-t0,aa,', '(nn|k0|h0),aa,ll,-(p|s|c|k|t)0,', 'ch,vv,s0,-ii,nf,',
               '(?<=(mf|nf),-)ii,-p0,uu,ll,', '(?<=(nf|ll),-)k0,oo,-rr,ii,', '(?<=(nf|ll),-)s0,qq,',
               '(?<=(nf|ll),-)c0,qq,-c0,uu,', 'k0,ii,ll,-k0,aa,', 'mm,uu,ll,-t0,oo,ng,-ii,', 'mm,uu,ll,-c0,',
               '(?<=(nf|ll),-)p0,aa,-t0,aa,kf,', '(?<=(nf|ll),-)s0,oo,kf,', '(?<=s0,uu,ll,-)(c|p|t)0,',
               'k0,aa,ng,-k0,aa,', '(?<=(ng|mf),-)t0,aa,ll,', 't0,xx,ng,-p0,uu,ll,', 'ch,aa,ng,-s0,aa,ll,',
               '(?<=(ll|ng),-)c0,uu,ll,-k0,ii,', 'aa,nf,-k0,oo,', '(?<=kk,yv,-aa,nf,-)(t|c)0,',
               'ii,-c0,uu,kf,-ii,-c0,uu,kf,', 'ya,-k0,xx,mf,-ya,-k0,xx,mf,', 'p0,ee,-k0,qq,s0,-ii,s0,',
               'kk,qq,s0,-ii,ph,', 'nn,aa,-mm,uu,s0,-ii,ph,', 'qq,s0,-yv,ll,', 't0,wi,s0,-(?=[aeqiouyvwx])',
               'nn,xx,c0,-yv,-rr,xx,mf,', 't0,ii,-k0,xx,tf,-(ii|xx|ee),',
               '(c0|ch|th|h0),ii,-xx,(c0|ch|th|h0),-(ii|xx|ee),', 'ph,ii,-xx,ph,-(ii|xx|ee),',
               'kh,ii,-xx,kh,-(ii|xx|ee),', 'l(b|p),-h0,', 'nh,-(c|k|t)0,', 'lh,-(c|k|t)0,', 'lk,-h0,', 'nc,-h0,',
               '(k0,aa,|k0,uu,|k0,vv,|oo,|p0,aa,|nn,aa,|nn,xx,|p0,uu,|^ii,|-,ii,mm,aa,|mm,uu,|(^|-,)vv,)lk,-(t0|c0|s0),',
               '(k0,aa,|k0,uu,|k0,vv,|vv,|oo,|mm,aa,|p0,aa,|nn,aa,|nn,xx,|mm,uu,|p0,uu,|^ii,|-,ii,)lk,-k0,',
               'nh,-(k|t|c)0,', 'nh,-s0,', 'nh,-nn,', 'nh,-(?=[aeqiouyvwx])', 'lh,-nn,', 'lh,-(k|t|c)0,', 'lh,-s0,',
               'lh,-(?=[aeqiouyvwx])', 'nc,-([ktsc])0,', '(c0,vv,|c0,ii,|k0,uu,|t0,aa,|(^|-,)oo,|k0,oo,)lm,-([ktsc])0,',
               '(p0,aa,|tt,vv,|(^|-,)yv,|nn,vv,|(^|-,)ya,|cc,aa,)lb,-([ktsc])0,', 'h0,(aa|uu),lt,-nn,',
               'h0,(aa|uu),lt,-([ktsc])0,', 'lk,-(c|k|p|s|t)0,', 'l(b|p),-p0,', 's0,-p0,', 'l(b|t),-(c|k|s|t|p)0,',
               'lp,-(c|k|s|t)0,', '(c[h0]|s[s0]|t[fh]),-(c|k|s|t)0,', 'k[fhks],-(c|k|p|s|t)0,', 'p[sfh],-(c|k|p|s|t)0,',
               '(?<=(kf|kh|ks|ss|c0|ch|tf|th),-)p0,', 'h0,-s0,', 'nh,-s0,', 'lh,-s0,', '(ks|lk),(?=(#|$|-[ptkshcmnr]))',
               'n[ch],(?=(#|$|-[ptkshcmnr]))', 'l[bsth],(?=(#|$|-[ptkshcmnr]))', 'lm,(?=(#|$|-[ptkshcmnr]))',
               '(ps|lp),(?=(#|$|-[ptkshcmnr]))', '([kp])s,-(?=[aeqiouyvwx])', 'ls,-(?=[aeqiouyvwx])',
               'nc,-(?=[aeqiouyvwx])', 'lk,-(?=[aeqiouyvwx])', 'lm,-(?=[aeqiouyvwx])', 'lb,-(?=[aeqiouyvwx])',
               'l([tp]),-(?=[aeqiouyvwx])', '(?<=[pk])0,-rr,', '(c0|ch|s0|ss|tf|nh|h0),-nn,', 'nc,-(p|t|k)0,',
               'nc,(?=-[ptkshcmnr])', 'lm,-k0,', 'lm,(?=-[ptkshcmnr])', 'k[fhks],(?=-(nn|mm),)', 'lk,(?=-(nn|mm),)',
               'p[sfh],(?=-(nn|mm),)', 'l[bp],(?=-(nn|mm),)', '(?<=(mf|ng|pf|kf),-)rr,',
               '(c0|ch|s0|ss|tf|nh|h0),(?=-mm,)', 'll,-(?=y)', '(nf|ll),-rr,', 'l[lht],-nn,', 'tf,-(?=[iy])',
               'th,-(?=[iy])', 'tf,-h0,(?=[iy])', '(p|k)f,-h0,', 'h0,-(c|k|t)0,', '(tf|th|s0),(-|#)h0,',
               '(s0|ss|kk|p0|ph|pp|t0|th|tt|c0|ch|kh|kk|k0|mm|nn),-(?=[aeqiouyvwx])', 'nh,-(?=[aeqiouyvwx])',
               '(s0|ss|c0|ch|th),(?=-[ptkshcmnr])', 'h0,-(?=[aeqiouyvwx])', 'lh,-?(?=[aeqiouyvwx])',
               '(p|t|k)f,-?(?=[aeqiouyvwx])', '(m|n)f,-?(?=[aeqiouyvwx])', '(s0|ss|c0|ch|th),(?=-|#|$)',
               '(kh|kk|ks|lk),(?=-|#|$|[ptkshcmnr])', '(ph|lp|ps),(?=-|#|$|[ptkshcmnr])',
               '(?<=[ptkshcmnr].),-(?=[aeqiouyvwx])', 'l[bhstp],(?=-|#|$|[ptkshcmnr])', 'nh,(?=-|#|$|[ptkshcmnr])',
               '(?<=[aeqiouyvwx].,)ll,-(?=[aeqiouyvwx])', 'll,-ll,']
    rule_out = ['ii,ll,rr,y\\1,', '\\1,ll,rr,ii,ll,', 's0,vv,ll,rr,ii,kf,', 'mm,uu,ll,kk,oo,k0,ii,',
                's0,ii,ll,s0,ii,ll', 'k0,ii,s0,xx,kf,', 'c0,vv,rr,ya,kf,', 'k0,xx,-mm,yo,-ii,ll,', 'll,-ch,ii,', 'pf,',
                'll,cc,', 't0,aa,kf,', '\\1,nf,k0,aa,tf,', 'mm,aa,th,yv,ng,', 'k0,vv,t0,oo,tf,',
                'c0,uu,ll,rr,vv,mf,-kk,ii,', 'h0,oo,nf,nn,ii,p0,uu,ll,', 's0,aa,ng,nn,ii,ll,', 'mm,qq,nf,nn,ii,pf,',
                'kk,oo,nf,nn,ii,pf,', 'nn,qq,p0,oo,ng,nn,ya,kf,', 'h0,aa,nf,nn,yv,rr,xx,mf,',
                'nn,aa,mf,c0,oo,nf,nn,yv,p0,ii,', 's0,ii,nf,nn,yv,s0,vv,ng,', 's0,qq,ng,nn,yv,nf,ph,ii,ll,',
                't0,aa,mf,nn,yo,', 'nn,uu,nf,nn,yo,k0,ii,', 'vv,mf,nn,yo,ng,', 's0,ii,k0,yo,ng,nn,yu,',
                'nf,nn,yu,ll,rr,ii,', '\\1,\\2,ll,rr,ii,pf,', 'h0,aa,nf,nn,ii,ll,', 'mm,aa,ng,nn,ii,ll,',
                'mm,oo,ll,ss,aa,ng,s0,ii,kf,', 'oo,nf,nn,ii,pf,', '\\1,nn,yv,s0,vv,tf,', '\\1,nn,y\\2,', '\\1,rr,y\\2,',
                'll,rr,y\\1,', 'ii,ll,cc,vv,ll,', 'nf,-nn,y\\2,', 'mm,aa,ng,nn,ii,ll', 'k0,uu,k0,xx,nf,nn,yu,',
                'k0,aa,ll,\\1\\1,xx,ng,', 'p0,aa,ll,tt,oo,ng,', 'c0,vv,ll,tt,oo,', 'mm,aa,ll,ss,aa,ll,', 'p0,uu,ll,ss,',
                'ii,ll,ss,ii,', 'p0,aa,ll,cc,vv,nf,', '\\2\\2,', 'pp,', 'cc,', 'c0,aa,mf,cc,aa,rr,ii,', 'cc,',
                'pp,vv,pf,', 'pp,', 'p0,aa,rr,aa,mf,kk,yv,ll,', 'pp,', 'tt,', 'mm,aa,ng,nn,yv,mf,', 'p0,aa,pf,\\1\\1,',
                'p0,aa,mf,nn,', 'nn,vv,ll,\\1\\1,', 'mm,\\1,t0,ii,tf,tt,aa,', 'mm,\\1,t0,vv,pf,tt,aa,',
                'c0,vv,t0,vv,mm,ii,', 'h0,vv,t0,uu,s0,xx,mf,', 'k0,aa,p0,vv,ch,ii,', 'k0,aa,p0,ii,nf,nn,xx,nf,',
                'c0,vv,mf,cc,ii,', 'oo,mf,k0,', 'k0,uu,mf,k0,ii,t0,aa,', '\\1,aa,ll,\\2\\2,', 'ch,vv,t0,ii,nf,',
                'nn,ii,p0,uu,ll,', 'kk,oo,rr,ii,', 'ss,qq,', 'cc,qq,c0,uu,', 'k0,ii,ll,kk,aa,', 'mm,uu,ll,tt,oo,ng,ii,',
                'mm,uu,ll,-cc,', 'pp,aa,t0,aa,kf,', 'ss,oo,kf,', '\\1\\1,', 'k0,aa,ng,kk,aa,', 'tt,aa,ll,',
                't0,xx,ng,pp,uu,ll,', 'ch,aa,ng,ss,aa,ll,', 'k0,aa,ng,cc,uu,ll,k0,ii,', 'aa,nf,kk,oo,', '\\1\\1,',
                'ii,c0,uu,ng,nn,ii,c0,uu,kf,', 'ya,k0,xx,mf,nn,ya,k0,xx,mf,', 'p0,ee,k0,qq,nf,nn,ii,tf,',
                'kk,qq,nf,nn,ii,pf,', 'nn,aa,mm,uu,nf,nn,ii,pf,', 'qq,nf,nn,yv,ll,', 't0,wi,nf,-nn,',
                'nn,xx,tf,nn,yv,rr,xx,mf,', 't0,ii,k0,xx,s0,\\1,', '\\1,ii,xx,s0,\\3,', 'ph,ii,xx,p0,\\1,',
                'kh,ii,xx,k0,\\1,', 'll,-ph,', 'nf,-\\1h,', 'll,-\\1h,', 'll,-kh,', 'nf,-ch,', '\\1kf,-\\3,',
                '\\1ll,-kk,', 'nf,-\\1h,', 'nf,-ss,', 'nf,-nn,', '-nn,', 'll,-rr,', 'll,-\\1h,', 'll,-ss,', '-rr,',
                'nf,-\\1\\1,', '\\1mf,-\\3\\3,', '\\1ll,-\\4\\4,', 'h0,\\1,ll,-ll,', 'h0,\\1,ll,-\\2\\2,',
                'kf,-\\1\\1,', 'pf,-pp,', 'tf,-pp,', 'll,-\\2\\2,', 'pf,-\\1\\1,', 'tf,-\\2\\2,', 'kf,-\\1\\1,',
                'pf,-\\1\\1,', 'pp,', '-ss,', 'nf,-ss,', 'll,-ss,', 'kf,', 'nf,', 'll,', 'mf,', 'pf,', '\\1f,-ss,',
                'll,-ss,', 'nf,-c0,', 'll,-k0,', 'll,-mm,', 'll,-p0,', 'll,-\\1h,', 'f,-nn,', 'nf,-nn,', 'nf,-\\1\\1,',
                'nf,', 'mf,-kk,', 'mf,', 'ng,', 'ng,', 'mf,', 'mf,', 'nn,', 'nf,', '-rr,', 'll,-rr,', 'll,-rr,', '-c0,',
                '-ch,', '-ch,', '-\\1h,', '-\\1h,', '-th,', '-\\1,', '-nn,', 'tf,', '-', '-rr,', '-\\g<1>0,',
                '-\\1\\1,', 'tf,', 'kf,', 'pf,', ',', 'll,', 'nf,-', '-rr,', 'll,-rr,']

    prono = graph2prono(graph, rule_in, rule_out)

    return prono
