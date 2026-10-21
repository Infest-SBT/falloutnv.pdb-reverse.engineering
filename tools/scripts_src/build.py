"""Сборка scripts/fnv_apply_{ghidra,ida}.py из частей: python3 build.py <out_dir>"""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
common = open(os.path.join(here, 'common.py'), encoding='utf-8').read()
for tool in ('ghidra', 'ida'):
    L = open(os.path.join(here, tool + '_head.py'), encoding='utf-8').read().split('\n')
    k = next(i for i, l in enumerate(L) if l and not l.startswith('#'))
    body = open(os.path.join(here, tool + '_body.py'), encoding='utf-8').read()
    out = ['# -*- coding: utf-8 -*-'] + L[:k] + ['from __future__ import print_function, unicode_literals', ''] + L[k:] + [common, body]
    open(os.path.join(sys.argv[1], 'fnv_apply_%s.py' % tool), 'w', encoding='utf-8').write('\n'.join(out))
