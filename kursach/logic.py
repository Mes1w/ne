import itertools
# code 2-7-4-1 : Q4=2,Q3=7,Q2=4,Q1=1 ; minimal binary representation
W=(2,7,4,1)
def enc():
    d={}
    for v in range(16):
        bits=[(v>>3)&1,(v>>2)&1,(v>>1)&1,v&1]
        s=sum(w*b for w,b in zip(W,bits))
        if s<=9 and s not in d: d[s]=v
    return [d[i] for i in range(10)]
CODE=enc()
USED=set(CODE); DC=sorted(set(range(16))-USED)
VARS=['Q4','Q3','Q2','Q1']
def implicants():
    out=[]
    for mask in range(1,16):       # which vars are fixed
        for val in range(16):
            if val & ~mask: continue
            out.append((mask,val))
    out.append((0,0))
    return out
def covers(imp,m): return (m&imp[0])==imp[1]
def nlits(imp): return bin(imp[0]).count('1')
def minimize(ones,dc):
    ones=set(ones); dc=set(dc); ok=ones|dc
    if not ones: return []
    if len(ok)==16: return [(0,0)]
    imps=[i for i in implicants() if all((not covers(i,m)) or m in ok for m in range(16)) and any(covers(i,m) for m in ones)]
    # primes
    primes=[i for i in imps if not any(j!=i and (j[0]&i[0])==j[0] and (i[1]&j[0])==j[1] for j in imps)]
    best=None
    for k in range(1,len(primes)+1):
        for comb in itertools.combinations(primes,k):
            if all(any(covers(i,m) for i in comb) for m in ones):
                cost=(sum(nlits(i) for i in comb),)
                if best is None or cost<best[0]: best=(cost,comb)
        if best: break
    return sorted(best[1],key=lambda i:(-i[0],i[1]))
def term_str(imp):
    if imp[0]==0: return '1'
    s=[]
    for k,n in enumerate(VARS):
        b=8>>k
        if imp[0]&b: s.append(n if imp[1]&b else '!'+n)
    return '·'.join(s)
def sop_str(t): return ' + '.join(term_str(i) for i in t) if t else '0'
def ev(t,m): return int(any(covers(i,m) for i in t))
NXT={CODE[i]:CODE[(i+1)%10] for i in range(10)}
def jk():
    res={}
    for k,n in enumerate(VARS):
        b=8>>k
        J1=[m for m in USED if not m&b and NXT[m]&b]; Jdc=[m for m in range(16) if m in DC or m&b]
        K1=[m for m in USED if m&b and not NXT[m]&b]; Kdc=[m for m in range(16) if m in DC or not m&b]
        res['J'+n[1]]=minimize(J1,Jdc); res['K'+n[1]]=minimize(K1,Kdc)
    return res
SEG={0:'abcdef',1:'bc',2:'abdeg',3:'abcdg',4:'bcfg',5:'acdfg',6:'acdefg',7:'abc',8:'abcdefg',9:'abcdfg'}
if __name__=='__main__':
    print('CODE',[format(c,'04b') for c in CODE],'DC',[format(c,'04b') for c in DC])
    f=jk()
    for k,v in f.items(): print(k,'=',sop_str(v))
    # recovery from forbidden states
    def step(m):
        n=0
        for k,nm in enumerate(VARS):
            b=8>>k; J=ev(f['J'+nm[1]],m); K=ev(f['K'+nm[1]],m); q=1 if m&b else 0
            q2=(J and not q) or (q and not K)
            if q2: n|=b
        return n
    for m in range(16): assert m not in USED or step(m)==NXT[m]
    for m in DC:
        p=[m]
        while p[-1] not in USED and len(p)<20: p.append(step(p[-1]))
        print('dc',[format(x,'04b') for x in p])
    P=minimize([CODE[9]],DC); print('P =',sop_str(P))
    for s in 'abcdefg':
        on=[CODE[d] for d in range(10) if s in SEG[d]]; off=[CODE[d] for d in range(10) if s not in SEG[d]]
        print(s,'on :',sop_str(minimize(on,DC)),'   | off(n):',sop_str(minimize(off,DC)))
    # mux search for b,f : select pair, residual literal
    for s in 'bf':
        on=set(CODE[d] for d in range(10) if s in SEG[d])
        for sel in itertools.combinations(range(4),2):
            rest=[k for k in range(4) if k not in sel]
            row=[]
            for a in range(4):
                cells=[]
                for r in range(4):
                    m=0
                    for i,k in enumerate(sel):
                        if (a>>(1-i))&1: m|=8>>k
                    for i,k in enumerate(rest):
                        if (r>>(1-i))&1: m|=8>>k
                    cells.append(m)
                cands=[]
                for name,fn in [('0',lambda m:0),('1',lambda m:1)]+[(VARS[k],(lambda m,k=k:1 if m&(8>>k) else 0)) for k in rest]+[('!'+VARS[k],(lambda m,k=k:0 if m&(8>>k) else 1)) for k in rest]:
                    if all(m in DC or fn(m)==(m in on) for m in cells): cands.append(name)
                row.append(cands[:3] if cands else None)
            print(s,'sel',[VARS[k] for k in sel],row if all(row) else 'NO')
