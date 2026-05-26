#!/usr/bin/env python3
"""
CODEFORGE LIBRARY MANAGER v1.0
Standalone, dependency-free CLI & module for maintaining, cleaning, merging,
and editing CodeForge library.json files.

Features:
  • Auto-clean malformed arrays (fixes 'str' object has no attribute 'get')
  • Key/Value whitespace normalization
  • Schema validation & auto-defaults
  • Smart merge with ID conflict resolution
  • Advanced search/filter (regex, language, famille, tags)
  • Auto-versioned backups
  • CSV export for bulk spreadsheet editing
  • Rich CLI with subcommands & ANSI colors
"""
import json
import os
import sys
import uuid
import re
import copy
import shutil
import csv
import io
from datetime import datetime
from pathlib import Path
import argparse
from pprint import pformat

# ═══════════════════════════════════════════════════════════════════
#  ANSI COLORS & FORMATTING
# ═══════════════════════════════════════════════════════════════════
class Term:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def print_ok(msg):   print(f"{Term.OKGREEN}✅ {msg}{Term.ENDC}")
    @staticmethod
    def print_warn(msg): print(f"{Term.WARNING}⚠️  {msg}{Term.ENDC}")
    @staticmethod
    def print_err(msg):  print(f"{Term.FAIL}❌ {msg}{Term.ENDC}")
    @staticmethod
    def print_info(msg): print(f"{Term.OKCYAN}ℹ️  {msg}{Term.ENDC}")

# ═══════════════════════════════════════════════════════════════════
#  CORE MANAGER
# ═══════════════════════════════════════════════════════════════════
class LibraryManager:
    REQUIRED_FN = {'id', 'name', 'language', 'type'}
    REQUIRED_VAR = {'id', 'name', 'language', 'type'}
    FN_DEFAULTS = {'type': 'function', 'parameters': [], 'returns': {'datatype': 'void', 'description': ''}, 'tags': [], 'throws': []}
    VAR_DEFAULTS = {'type': 'variable', 'datatype': 'string', 'default_value': '', 'scope': 'local', 'tags': []}

    def __init__(self, filepath=None):
        self.path = Path(filepath) if filepath else None
        self.data = {'metadata': {}, 'functions': [], 'variables': []}
        if self.path and self.path.exists():
            self.load()

    # ─── LOAD & NORMALIZE ─────────────────────────────────────────
    def load(self, filepath=None):
        p = Path(filepath) if filepath else self.path
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")
        with open(p, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        self._sanitize_keys(raw)
        self.data = raw
        self.path = p
        Term.print_ok(f"Loaded: {p.name}")
        return self

    def _sanitize_keys(self, obj):
        """Strip whitespace from ALL JSON keys/values recursively."""
        if isinstance(obj, dict):
            new = {k.strip(): self._sanitize_keys(v) for k, v in obj.items()}
            return new
        if isinstance(obj, list):
            return [self._sanitize_keys(i) for i in obj]
        if isinstance(obj, str):
            return obj.strip()
        return obj

    # ─── CLEAN & REPAIR ───────────────────────────────────────────
    def clean(self):
        """Remove invalid entries, fill missing defaults, enforce types."""
        cleaned_fn = [f for f in self.data.get('functions', []) if isinstance(f, dict)]
        cleaned_var = [v for v in self.data.get('variables', []) if isinstance(v, dict)]

        # Auto-fill & type enforcement
        for f in cleaned_fn:
            for k, v in self.FN_DEFAULTS.items():
                f.setdefault(k, copy.deepcopy(v))
            if not isinstance(f['parameters'], list): f['parameters'] = []
            if not isinstance(f['tags'], list): f['tags'] = []
            if not isinstance(f['throws'], list): f['throws'] = []
            if not isinstance(f['returns'], dict): f['returns'] = {'datatype': 'void', 'description': ''}

        for v in cleaned_var:
            for k, v_def in self.VAR_DEFAULTS.items():
                v.setdefault(k, v_def)
            if not isinstance(v['tags'], list): v['tags'] = []

        self.data['functions'] = cleaned_fn
        self.data['variables'] = cleaned_var
        Term.print_ok("Cleaned: Removed non-dict entries, enforced schema, filled defaults.")

    def normalize_ids(self):
        """Ensure all IDs exist and are unique. Append _dup if needed."""
        seen = set()
        for lst in (self.data['functions'], self.data['variables']):
            for item in lst:
                if not item.get('id'):
                    item['id'] = f"auto_{uuid.uuid4().hex[:6]}"
                base, counter = item['id'], 0
                while item['id'] in seen:
                    counter += 1
                    item['id'] = f"{base}_{counter}"
                seen.add(item['id'])
        Term.print_ok("Normalized & deduplicated IDs.")

    # ─── MERGE ────────────────────────────────────────────────────
    def merge(self, source_path, conflict_strategy='skip'):
        """Merge another library.json. Strategies: skip, overwrite, suffix."""
        mgr = LibraryManager(source_path)
        mgr.clean()
        existing_ids = {f['id'] for f in self.data['functions']} | {v['id'] for v in self.data['variables']}
        
        merged_fn = merged_var = skipped_fn = skipped_var = 0
        for f in mgr.data['functions']:
            if f['id'] in existing_ids:
                if conflict_strategy == 'skip': skipped_fn += 1; continue
                if conflict_strategy == 'overwrite':
                    self.data['functions'] = [x for x in self.data['functions'] if x['id'] != f['id']]
                if conflict_strategy == 'suffix':
                    f['id'] = f"{f['id']}_m"
            self.data['functions'].append(f)
            merged_fn += 1

        for v in mgr.data['variables']:
            if v['id'] in existing_ids:
                if conflict_strategy == 'skip': skipped_var += 1; continue
                if conflict_strategy == 'overwrite':
                    self.data['variables'] = [x for x in self.data['variables'] if x['id'] != v['id']]
                if conflict_strategy == 'suffix':
                    v['id'] = f"{v['id']}_m"
            self.data['variables'].append(v)
            merged_var += 1

        Term.print_ok(f"Merged {merged_fn} fn, {merged_var} var. Skipped: {skipped_fn} fn, {skipped_var} var.")

    # ─── CRUD ─────────────────────────────────────────────────────
    def add(self, entry_type='function', **kwargs):
        item = {'id': f"{'fn' if entry_type=='function' else 'var'}_{uuid.uuid4().hex[:6]}", **kwargs}
        lst = self.data['functions'] if entry_type == 'function' else self.data['variables']
        lst.append(item)
        Term.print_ok(f"Added {entry_type}: {item['id']}")

    def update(self, entry_id, updates):
        lst = self.data['functions'] + self.data['variables']
        for item in lst:
            if item.get('id') == entry_id:
                item.update(updates)
                Term.print_ok(f"Updated {entry_id}")
                return True
        Term.print_err(f"ID not found: {entry_id}")
        return False

    def delete(self, entry_id):
        before_f = len(self.data['functions'])
        self.data['functions'] = [f for f in self.data['functions'] if f.get('id') != entry_id]
        before_v = len(self.data['variables'])
        self.data['variables'] = [v for v in self.data['variables'] if v.get('id') != entry_id]
        if len(self.data['functions']) < before_f or len(self.data['variables']) < before_v:
            Term.print_ok(f"Deleted {entry_id}")
        else:
            Term.print_err(f"ID not found: {entry_id}")

    # ─── SEARCH & FILTER ──────────────────────────────────────────
    def search(self, query, field='name', language=None, famille=None, regex=False):
        query = query.lower()
        results = []
        for item in self.data['functions'] + self.data['variables']:
            if language and item.get('language') != language: continue
            if famille and item.get('famille') != famille: continue
            val = str(item.get(field, '')).lower()
            match = re.search(query, val) if regex else query in val
            if match:
                results.append(item)
        return results

    def stats(self):
        fns = self.data['functions']
        vars_ = self.data['variables']
        langs = {}
        for i in fns + vars_:
            l = i.get('language', 'Unknown')
            langs[l] = langs.get(l, 0) + 1
        familles = {}
        for i in fns:
            f = i.get('famille', 'Uncategorized')
            familles[f] = familles.get(f, 0) + 1
        return {'total_fn': len(fns), 'total_var': len(vars_), 'languages': langs, 'families': familles}

    # ─── VALIDATE ─────────────────────────────────────────────────
    def validate(self):
        errors = []
        for lst, name in [(self.data['functions'], 'functions'), (self.data['variables'], 'variables')]:
            for i, item in enumerate(lst):
                req = self.REQUIRED_FN if name == 'functions' else self.REQUIRED_VAR
                missing = req - set(item.keys())
                if missing: errors.append(f"{name}[{i}] missing: {missing}")
                if not isinstance(item.get('parameters' if name=='functions' else 'tags', []), list):
                    errors.append(f"{name}[{i}] parameters/tags must be list")
        return errors if errors else None

    # ─── SAVE & BACKUP ────────────────────────────────────────────
    def backup(self):
        if not self.path: return
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        bak = self.path.with_suffix(f'.{ts}.bak')
        shutil.copy2(self.path, bak)
        Term.print_ok(f"Backed up -> {bak.name}")

    def save(self, filepath=None, pretty=True):
        p = Path(filepath) if filepath else self.path
        if not p: raise ValueError("No target path specified")
        self.backup()
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False, sort_keys=False)
        Term.print_ok(f"Saved -> {p.name}")

    # ─── EXPORT CSV ───────────────────────────────────────────────
    def export_csv(self, outpath=None):
        p = outpath or self.path.with_suffix('.csv')
        with open(p, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id','type','name','language','famille','description','tags'])
            writer.writeheader()
            for item in self.data['functions'] + self.data['variables']:
                row = {k: (', '.join(v) if isinstance(v, list) else v) for k, v in item.items() if k in writer.fieldnames}
                writer.writerow(row)
        Term.print_ok(f"Exported CSV -> {p.name}")

# ═══════════════════════════════════════════════════════════════════
#  CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════
def cli():
    parser = argparse.ArgumentParser(
        prog='cf_lib_manager',
        description='CodeForge Library JSON Manager v1.0',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('file', help='Target library.json path')
    sub = parser.add_subparsers(dest='command', required=True)

    # clean
    p_clean = sub.add_parser('clean', help='Remove invalid entries, normalize keys, fill defaults')
    p_clean.add_argument('--fix-ids', action='store_true', help='Repair & deduplicate IDs')
    p_clean.add_argument('-s', '--save', action='store_true', help='Auto-save after clean')

    # merge
    p_merge = sub.add_parser('merge', help='Merge another library.json')
    p_merge.add_argument('source', help='Source library.json')
    p_merge.add_argument('--strategy', choices=['skip','overwrite','suffix'], default='skip')

    # search
    p_search = sub.add_parser('search', help='Search elements')
    p_search.add_argument('query')
    p_search.add_argument('--field', default='name')
    p_search.add_argument('--lang')
    p_search.add_argument('--family')
    p_search.add_argument('--regex', action='store_true')

    # stats
    sub.add_parser('stats', help='Show library statistics')

    # validate
    sub.add_parser('validate', help='Schema validation report')

    # export
    sub.add_parser('export', help='Export to CSV')

    # add
    p_add = sub.add_parser('add', help='Add new function/variable')
    p_add.add_argument('--type', choices=['function','variable'], default='function')
    p_add.add_argument('--name', required=True)
    p_add.add_argument('--lang', required=True)
    p_add.add_argument('--family', default='')
    p_add.add_argument('--desc', default='')

    # delete
    p_del = sub.add_parser('delete', help='Delete by ID')
    p_del.add_argument('id')

    args = parser.parse_args()
    mgr = LibraryManager(args.file)

    try:
        if args.command == 'clean':
            mgr.clean()
            if args.fix_ids: mgr.normalize_ids()
            if args.save: mgr.save()

        elif args.command == 'merge':
            mgr.merge(args.source, args.strategy)
            mgr.save()

        elif args.command == 'search':
            results = mgr.search(args.query, args.field, args.lang, args.family, args.regex)
            print(f"\n{Term.HEADER}🔍 Found {len(results)} results:{Term.ENDC}")
            for r in results:
                print(f"  {Term.OKCYAN}{r['id']:10} | {r['name']:30} | {r.get('language',''):12} | {r.get('famille',''):15}{Term.ENDC}")

        elif args.command == 'stats':
            s = mgr.stats()
            print(f"\n{Term.HEADER}📊 Library Statistics:{Term.ENDC}")
            print(f"  Functions: {Term.BOLD}{s['total_fn']}{Term.ENDC}  |  Variables: {Term.BOLD}{s['total_var']}{Term.ENDC}")
            print(f"  Languages: {pformat(s['languages'])}")
            print(f"  Families:  {pformat(s['families'])}")

        elif args.command == 'validate':
            errs = mgr.validate()
            if errs:
                print(f"\n{Term.FAIL}❌ Validation Failed ({len(errs)} issues):{Term.ENDC}")
                for e in errs: print(f"  • {e}")
            else:
                Term.print_ok("✅ Schema valid. No issues detected.")

        elif args.command == 'export':
            mgr.export_csv()

        elif args.command == 'add':
            kwargs = {'name': args.name, 'language': args.lang, 'famille': args.family, 'description': args.desc}
            mgr.add(args.type, **kwargs)
            mgr.save()

        elif args.command == 'delete':
            mgr.delete(args.id)
            mgr.save()

    except Exception as e:
        Term.print_err(f"Execution failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli()