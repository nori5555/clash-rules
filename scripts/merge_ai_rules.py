#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并最全 Clash AI 规则集：v2fly category-ai-!cn（全展开）+ blackmatrix7 + ACL4SSR"""
import urllib.request, re, os

UA = {'User-Agent': 'Mozilla/5.0'}
OUT = os.environ.get('OUTPUT_DIR', os.getcwd())  # 输出目录：Actions 里=仓库根

# 上游 AI 源未覆盖的补充域名（人工维护，每次合并都会带上）
EXTRA_DOMAINS = {
    'labs.google.com',        # Google Muse / 各类实验性 AI 产品入口
}
def fetch(url, timeout=30, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            if i == tries - 1: raise
            import time; time.sleep(1.5 * (i + 1))

def expand_include(lines, basedir='https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/', seen=None, depth=0):
    """递归展开 v2fly include:xxx 语法，剔除 @cn 条目，返回域名集合"""
    if seen is None: seen = set()
    out = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'): continue
        if line.startswith('include:'):
            inc = line.split()[0][8:]
            if inc in seen or depth > 20: continue
            seen.add(inc)
            try:
                sub = fetch(basedir + inc).splitlines()
                out |= expand_include(sub, basedir, seen, depth + 1)
            except Exception as e:
                print(f'  [warn] include {inc}: {e}')
            continue
        # 普通域名行，可能有属性如 "domain @cn"
        parts = line.split()
        dom = parts[0]
        attrs = parts[1:]
        if any(a == '@cn' for a in attrs):  # -!cn 语义剔除 @cn
            continue
        out.add(dom.lower())
    return out

def parse_clash_list(text):
    """blackmatrix7/ACL4SSR 格式: DOMAIN-SUFFIX,xxx / DOMAIN-KEYWORD,xxx / DOMAIN,xxx"""
    suffix, kw, dom = set(), set(), set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('payload:'):
            continue
        if line.startswith('DOMAIN-SUFFIX,'):
            suffix.add(line.split(',')[1].strip().lower())
        elif line.startswith('DOMAIN-KEYWORD,'):
            kw.add(line.split(',')[1].strip().lower())
        elif line.startswith('DOMAIN,'):
            dom.add(line.split(',')[1].strip().lower())
        else:
            # 可能是纯域名行
            p = line.split(',')
            if len(p) == 1 and re.match(r'^[a-z0-9.*-]+\.[a-z]{2,}$', p[0], re.I):
                suffix.add(p[0].strip().lower())
    return suffix, kw, dom

print('[*] 1/4 拉取并展开 v2fly category-ai-!cn ...')
ai_src = fetch('https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/category-ai-!cn').splitlines()
ai_domains = expand_include(ai_src)
print(f'    -> {len(ai_domains)} 个域名')

print('[*] 2/4 拉取 blackmatrix7 ...')
bm_domains, bm_kw = set(), set()
for name in ['OpenAI/OpenAI', 'Claude/Claude', 'Gemini/Gemini', 'BardAI/BardAI', 'Copilot/Copilot', 'AiQiCha/AiQiCha']:
    try:
        t = fetch(f'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/{name}.list')
        s, k, d = parse_clash_list(t)
        bm_domains |= s | d; bm_kw |= k
        print(f'    {name}: +{len(s|d)} 域名 +{len(k)} 关键字')
    except Exception as e:
        print(f'    {name}: 跳过 ({e})')

print('[*] 3/4 拉取 ACL4SSR ...')
ac_domains, ac_kw = set(), set()
for name in ['AI', 'OpenAi', 'Claude', 'ClaudeAI', 'Gemini', 'Copilot']:
    try:
        t = fetch(f'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/{name}.list')
        s, k, d = parse_clash_list(t)
        ac_domains |= s | d; ac_kw |= k
        print(f'    {name}: +{len(s|d)} 域名 +{len(k)} 关键字')
    except Exception as e:
        print(f'    {name}: 跳过 ({e})')

print('[*] 4/4 合并去重 ...')
merged = ai_domains | bm_domains | ac_domains | EXTRA_DOMAINS
merged.discard('')
kw_all = bm_kw | ac_kw
print(f'    域名后缀合计: {len(merged)}')
print(f'    关键字合计:   {len(kw_all)}')

os.makedirs(OUT, exist_ok=True)
# 1) rule-provider 格式（纯域名列表，behavior: domain）
with open(os.path.join(OUT, 'AI_MERGED.list'), 'w') as f:
    f.write('# Clash AI ruleset - 最全合并版 (v2fly category-ai-!cn + blackmatrix7 + ACL4SSR)\n')
    f.write('# 生成时间: 2026-10-27 | 域名后缀列表, 供 rule-provider behavior:domain 使用\n')
    f.write('# 来源: github.com/v2fly/domain-list-community, blackmatrix7/ios_rule_script, ACL4SSR/ACL4SSR\n')
    for d in sorted(merged):
        f.write(d + '\n')
# 2) 规则行格式（DOMAIN-SUFFIX）
with open(os.path.join(OUT, 'AI_MERGED_RULES.txt'), 'w') as f:
    for d in sorted(merged):
        f.write(f'DOMAIN-SUFFIX,{d},PROXY\n')
    for k in sorted(kw_all):
        f.write(f'DOMAIN-KEYWORD,{k},PROXY\n')
print(f'[OK] 输出到 {OUT}/')
