import csv, re, collections, sys, json
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
# ordered: first match wins; specific before general
FAM = [
 ('classical_orchestral', r'baroque|motet|orchestra|string quartet|symphon|cinematic|choir|chamber|opera|classical piano|solo piano|neo-classical|neoclassical'),
 ('ambient',   r'ambient|drone|soundscape|meditat|new age'),
 ('lofi_chill',r'lo-?fi|chillhop|chill hop|downtempo|psybient|trip-?hop'),
 ('hiphop',    r'hip[- ]?hop|boom[- ]?bap|trap|drill|phonk|rap\b|mpc'),
 ('rnb_soul',  r'neo[- ]?soul|r&b|rnb|\bsoul\b|gospel|motown'),
 ('latin',     r'bossa|reggaeton|corrido|latin|salsa|cumbia|bachata|samba|tango|mariachi|flamenco|dembow'),
 ('reggae_dub',r'reggae|\bdub\b|ska\b|dancehall'),
 ('world',     r'hindustani|raga|sitar|tabla|afrobeat|amapiano|highlife|soukous|afro|bollywood|k-?pop|j-?pop|gamelan|celtic|klezmer|world|sufi|qawwali|arabic|flamenc'),
 ('jazz_funk', r'jazz|funk|swing|big[- ]band|bebop|blues'),
 ('electronic',r'techno|house|trance|psytrance|edm|dubstep|drum and bass|drum & bass|dnb|jungle|garage|synthwave|electro|breakbeat|broken beat|idm|synthpop|disco|electronic|bass music|\bdance\b'),
 ('rock_metal',r'rock|metal|punk|grunge|indie|shoegaze|post-rock|guitar-driven|emo\b'),
 ('country_folk',r'country|folk|bluegrass|americana|acoustic singer|singer-songwriter'),
 ('pop',       r'\bpop\b|ballad|k-pop|hyperpop'),
]
def fam(r):
    s = ' '.join([r['title'], r['tags'][:300], r['gpt_description_prompt'][:300]]).lower()
    # check tags first (more reliable) then description
    for text in (r['tags'][:200].lower(), s):
        for name, pat in FAM:
            if re.search(pat, text): return name
    return 'other'
out=[]
for r in rows:
    r['family']=fam(r)
print(collections.Counter(r['family'] for r in rows))
json.dump([{**r} for r in rows], open(sys.argv[2],'w'))
for r in rows:
    if r['family']=='other': print('OTHER:', r['title'][:40],'|',r['tags'][:90])
