WORDS={'DRAM':['ddr3','ddr4','ddr5','sodimm','udimm','rdimm','lrdimm','ecc memory','server memory','pamiec ram','оперативна пам'],'SSD':['ssd','nvme','solid state','enterprise ssd','data center ssd','dysk polprzewodnikowy','твердотільний','u.2','u.3','e1.s','e3.s','sas ssd'],'Flash':['usb flash','pendrive','flash drive','microsd','micro sd','sd card','karta pamieci','карта пам'],'NAND':['nand','emmc','ufs','bics flash']}
BRANDS=['goodram','wilk elektronik','kioxia','exceria']; NEG=['furniture','chair','meble','krzeslo','меблі','printer toner']
def match(text):
    low=(text or '').lower()
    if any(x in low for x in NEG): return 'Other',0,[]
    scores={}; hits=[]
    for cat,terms in WORDS.items():
        found=[x for x in terms if x in low]
        if found: scores[cat]=25+15*len(found); hits+=found
    brands=[x for x in BRANDS if x in low]; hits+=brands
    if brands:
        for cat in scores: scores[cat]+=25
    if not scores:return 'Other',0,[]
    cat=max(scores,key=scores.get); return cat,min(100,scores[cat]),sorted(set(hits))
