import csv, re, collections, json, sys, math, random
sys.path.insert(0, '.')
rows = json.load(open('fam.json'))
def junk(r):
    t = (r['tags'] + r['title']).lower()
    return ('spoken word' in t or 'window.clerk' in t or 'async' in t[:40]
            or r['family'] == 'other')
keep = []
for r in rows:
    if r['status'] != 'complete' or r['major_model_version'] not in ('v5', 'v5.5'): continue
    if float(r['duration']) < 90 or junk(r): continue
    keep.append(r)
print('after filters', len(keep), 'of', len(rows))
# dedupe: Suno returns 2 clips per generation -> same tags/prompt
seen, uniq = set(), []
for r in keep:
    k = (r['tags'][:150], r['gpt_description_prompt'][:150], r['is_instrumental'])
    if k in seen: continue
    seen.add(k); uniq.append(r)
print('after dedupe', len(uniq))
N = 20
strata = collections.defaultdict(list)
for r in uniq:
    strata[(r['family'], r['is_instrumental'])].append(r)
tot = len(uniq)
# largest-remainder proportional allocation over family x vocal strata
quota = {k: N * len(v) / tot for k, v in strata.items()}
alloc = {k: int(q) for k, q in quota.items()}
rem = N - sum(alloc.values())
for k in sorted(quota, key=lambda k: quota[k] - alloc[k], reverse=True)[:rem]:
    alloc[k] += 1
random.seed(42)
pick = []
for k, n in alloc.items():
    pick += random.sample(strata[k], min(n, len(strata[k])))
print('\nfamily x instrumental: pool -> sampled (exact share*20)')
for k in sorted(strata, key=lambda k: -len(strata[k])):
    print(f'{k[0]:22s} instr={k[1]:5s} pool={len(strata[k]):3d} ({100*len(strata[k])/tot:4.1f}%)  exact={quota[k]:.2f} -> {alloc[k]}')
print('\nfamily totals')
fp = collections.Counter(r['family'] for r in uniq); fs = collections.Counter(r['family'] for r in pick)
for f in fp: print(f'{f:22s} pool {100*fp[f]/tot:4.1f}%  sample {fs[f]}/{len(pick)}')
print('vocal in pool %.0f%% sample %.0f%%' % (100*sum(r['is_instrumental']=='False' for r in uniq)/tot, 100*sum(r['is_instrumental']=='False' for r in pick)/len(pick)))
json.dump(pick, open('pick.json', 'w'))
