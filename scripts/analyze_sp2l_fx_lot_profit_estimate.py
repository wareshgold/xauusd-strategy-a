"""
Research-only FX discovery analyzer.

Converts discovery matrix R values into approximate USD values for a fixed
0.01 lot size using MT5 symbol specifications when provided.

No canonical strategy decisions are made here.
"""

import argparse
import csv
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--symbol-specs', required=True,
                    help='JSON: symbol -> {r_value_usd_at_0_01_lot: number}')
    ap.add_argument('--output-json', required=True)
    args = ap.parse_args()

    specs = json.load(open(args.symbol_specs, encoding='utf-8'))
    rows = []

    with open(args.input, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if not r.get('net_r'):
                continue
            sym = r['symbol_requested']
            one_r = float(specs.get(sym, {}).get('r_value_usd_at_0_01_lot', 0))
            rr = dict(r)
            rr['estimated_usd_net_at_0_01_lot'] = float(r['net_r']) * one_r
            rows.append(rr)

    rows.sort(key=lambda x: x['estimated_usd_net_at_0_01_lot'], reverse=True)

    json.dump({
        'status': 'COMPLETE',
        'research_only': True,
        'rows': rows,
        'notes': [
            'USD estimates depend on supplied MT5 symbol specifications.',
            'No configuration is promoted to canonical Strategy A.'
        ]
    }, open(args.output_json, 'w', encoding='utf-8'), indent=2)

    print(f'COMPLETE rows={len(rows)}')


if __name__ == '__main__':
    main()
