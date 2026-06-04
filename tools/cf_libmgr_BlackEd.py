#!/usr/bin/env python3
"""
CODEFORGE LIBRARY MANAGER v2.0 — BLACK EDITION
Standalone, dependency-free CLI & module for maintaining, cleaning, merging,
and editing CodeForge library.json files.

NEW FEATURES:
  • diff — Show differences between two library versions
  • show — Pretty-print JSON with syntax highlighting (ANSI)
  • dedup — Remove duplicate entries (same name+language)
  • audit — Check for broken references (invalid IDs in parameters)
  • batch-set — Bulk edit fields using JSON path syntax
  • rollback — Restore previous backup
  • init — Generate fresh library skeleton
  • --json output for scripting
  • --table output for search
  • --minify save option
  • Search by tags
  • Deep parameter validation
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
import difflib
from datetime import datetime
from pathlib import Path
from collections import defaultdict
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
    DIM = '\033[2m'

    @staticmethod
    def print_ok(msg):   print(f"{Term.OKGREEN}✅ {msg}{Term.ENDC}")
    @staticmethod
    def print_warn(msg): print(f"{Term.WARNING}⚠️  {msg}{Term.ENDC}")
    @staticmethod
    def print_err(msg):  print(f"{Term.FAIL}❌ {msg}{Term.ENDC}")
    @staticmethod
    def print_info(msg): print(f"{Term.OKCYAN}ℹ️  {msg}{Term.ENDC}")
    @staticmethod
    def print_header(msg): print(f"{Term.HEADER}{Term.BOLD}{msg}{Term.ENDC}")

    @staticmethod
    def json_colorize(data, indent=2):
        """Colorized JSON output (simplified)"""
        try:
            import json
            text = json.dumps(data, indent=indent, ensure_ascii=False)
            # Simple ANSI highlighting
            text = re.sub(r'("(\\u[a-fA-F0-9]{4}|\\[^u]|[^\\"])*")', f'{Term.OKGREEN}\\1{Term.ENDC}', text)
            text = re.sub(r'\b(true|false|null)\b', f'{Term.OKCYAN}\\1{Term.ENDC}', text)
            text = re.sub(r'\b(\d+)\b', f'{Term.WARNING}\\1{Term.ENDC}', text)
            return text
        except:
            return str(data)


# ═══════════════════════════════════════════════════════════════════
#  CORE MANAGER — BLACK EDITION
# ═══════════════════════════════════════════════════════════════════
class LibraryManagerBlack:
    REQUIRED_FN = {'id', 'name', 'language', 'type'}
    REQUIRED_VAR = {'id', 'name', 'language', 'type'}
    FN_DEFAULTS = {'type': 'function', 'parameters': [], 'returns': {'datatype': 'void', 'description': ''}, 'tags': [], 'throws': []}
    VAR_DEFAULTS = {'type': 'variable', 'datatype': 'string', 'default_value': '', 'scope': 'local', 'tags': []}
    
    # Valid datatypes pour validation
    VALID_DATATYPES = {'string', 'int', 'bool', 'PSCredential', 'string[]', 'hashtable', 
                       'object', 'double', 'DateTime', 'PSObject', 'list', 'dict', 'void'}
    VALID_LANGUAGES = {'PowerShell', 'CSharp', 'JavaScript', 'Python', 'Bash', 'Go'}

    def __init__(self, filepath=None):
        self.path = Path(filepath) if filepath else None
        self.data = {'metadata': {}, 'functions': [], 'variables': []}
        self._backup_list = []
        if self.path and self.path.exists():
            self.load()

    # ─── INIT ─────────────────────────────────────────────────────
    @staticmethod
    def init_template(output_path, name="New Library"):
        """Create a fresh library skeleton."""
        template = {
            "metadata": {
                "version": "2.0",
                "description": name,
                "created": datetime.now().strftime("%Y-%m-%d"),
                "author": "DSI — INGEN Systems",
                "scope": "",
                "validation_status": "DRAFT",
                "languages": ["PowerShell", "CSharp", "JavaScript"]
            },
            "functions": [
                {
                    "id": "fn_example_001",
                    "type": "function",
                    "name": "ExampleFunction",
                    "language": "PowerShell",
                    "famille": "Example",
                    "description": "This is an example function",
                    "parameters": [
                        {"name": "Input", "datatype": "string", "required": True, "description": "Input value"}
                    ],
                    "returns": {"datatype": "bool", "description": "Success status"},
                    "source": "function ExampleFunction { param([string]$Input) return $true }",
                    "tags": ["example"],
                    "throws": []
                }
            ],
            "variables": [
                {
                    "id": "var_example_001",
                    "type": "variable",
                    "name": "ExampleVar",
                    "language": "PowerShell",
                    "datatype": "string",
                    "default_value": "\"default\"",
                    "scope": "local",
                    "description": "Example variable",
                    "tags": ["example"]
                }
            ]
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        Term.print_ok(f"Created template library: {output_path}")

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
        self._scan_backups()
        Term.print_ok(f"Loaded: {p.name}")
        return self

    def _scan_backups(self):
        """List available backups for rollback."""
        if not self.path:
            return
        pattern = f"{self.path.stem}.*.bak"
        self._backup_list = sorted([f for f in self.path.parent.glob(pattern)], key=lambda x: x.stat().st_mtime, reverse=True)

    def _sanitize_keys(self, obj):
        if isinstance(obj, dict):
            return {k.strip(): self._sanitize_keys(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._sanitize_keys(i) for i in obj]
        if isinstance(obj, str):
            return obj.strip()
        return obj

    # ─── SHOW (pretty print) ──────────────────────────────────────
    def show(self, entry_id=None, color=True):
        """Pretty-print JSON with optional filtering by ID."""
        if entry_id:
            for item in self.data['functions'] + self.data['variables']:
                if item.get('id') == entry_id:
                    print(Term.json_colorize(item) if color else json.dumps(item, indent=2, ensure_ascii=False))
                    return
            Term.print_err(f"ID not found: {entry_id}")
        else:
            print(Term.json_colorize(self.data) if color else json.dumps(self.data, indent=2, ensure_ascii=False))

    # ─── DIFF ─────────────────────────────────────────────────────
    def diff(self, other_path):
        """Compare current library with another file."""
        other = LibraryManagerBlack(other_path)
        other.clean()
        
        # Index current items by ID
        curr_fn = {f['id']: f for f in self.data['functions']}
        curr_var = {v['id']: v for v in self.data['variables']}
        other_fn = {f['id']: f for f in other.data['functions']}
        other_var = {v['id']: v for v in other.data['variables']}
        
        added_fn = [k for k in other_fn if k not in curr_fn]
        removed_fn = [k for k in curr_fn if k not in other_fn]
        added_var = [k for k in other_var if k not in curr_var]
        removed_var = [k for k in curr_var if k not in other_var]
        
        # Modified functions
        modified_fn = []
        for k in set(curr_fn.keys()) & set(other_fn.keys()):
            if json.dumps(curr_fn[k], sort_keys=True) != json.dumps(other_fn[k], sort_keys=True):
                modified_fn.append(k)
        
        modified_var = []
        for k in set(curr_var.keys()) & set(other_var.keys()):
            if json.dumps(curr_var[k], sort_keys=True) != json.dumps(other_var[k], sort_keys=True):
                modified_var.append(k)
        
        Term.print_header("\n📊 DIFF REPORT")
        if added_fn: Term.print_info(f"➕ Functions added: {', '.join(added_fn[:10])}" + ("..." if len(added_fn)>10 else ""))
        if removed_fn: Term.print_warn(f"➖ Functions removed: {', '.join(removed_fn[:10])}" + ("..." if len(removed_fn)>10 else ""))
        if modified_fn: Term.print_info(f"🔄 Functions modified: {', '.join(modified_fn[:10])}" + ("..." if len(modified_fn)>10 else ""))
        if added_var: Term.print_info(f"➕ Variables added: {', '.join(added_var[:10])}" + ("..." if len(added_var)>10 else ""))
        if removed_var: Term.print_warn(f"➖ Variables removed: {', '.join(removed_var[:10])}" + ("..." if len(removed_var)>10 else ""))
        if modified_var: Term.print_info(f"🔄 Variables modified: {', '.join(modified_var[:10])}" + ("..." if len(modified_var)>10 else ""))
        
        if not any([added_fn, removed_fn, modified_fn, added_var, removed_var, modified_var]):
            Term.print_ok("No differences detected")
        
        return {'added_fn': added_fn, 'removed_fn': removed_fn, 'modified_fn': modified_fn,
                'added_var': added_var, 'removed_var': removed_var, 'modified_var': modified_var}

    # ─── CLEAN & REPAIR (amélioré) ────────────────────────────────
    def clean(self, deep=False):
        """Remove invalid entries, fill missing defaults, enforce types."""
        cleaned_fn = [f for f in self.data.get('functions', []) if isinstance(f, dict)]
        cleaned_var = [v for v in self.data.get('variables', []) if isinstance(v, dict)]

        for f in cleaned_fn:
            for k, v in self.FN_DEFAULTS.items():
                f.setdefault(k, copy.deepcopy(v))
            if not isinstance(f['parameters'], list): f['parameters'] = []
            if not isinstance(f['tags'], list): f['tags'] = []
            if not isinstance(f['throws'], list): f['throws'] = []
            if not isinstance(f['returns'], dict): f['returns'] = {'datatype': 'void', 'description': ''}
            
            # Deep validation
            if deep:
                # Validate language
                if f.get('language') not in self.VALID_LANGUAGES:
                    Term.print_warn(f"Function {f.get('id')}: unknown language '{f.get('language')}'")
                
                # Validate parameters
                for p in f['parameters']:
                    if p.get('datatype') not in self.VALID_DATATYPES and p.get('datatype') != 'flow':
                        Term.print_warn(f"Function {f.get('id')}: unknown datatype '{p.get('datatype')}' for param {p.get('name')}")

        for v in cleaned_var:
            for k, v_def in self.VAR_DEFAULTS.items():
                v.setdefault(k, v_def)
            if not isinstance(v['tags'], list): v['tags'] = []
            if deep and v.get('datatype') not in self.VALID_DATATYPES:
                Term.print_warn(f"Variable {v.get('id')}: unknown datatype '{v.get('datatype')}'")

        self.data['functions'] = cleaned_fn
        self.data['variables'] = cleaned_var
        Term.print_ok(f"Cleaned{' (deep)' if deep else ''}: Removed non-dict entries, enforced schema.")

    # ─── DEDUP ────────────────────────────────────────────────────
    def dedup(self):
        """Remove duplicate entries (same name + language)."""
        seen_fn = {}
        seen_var = {}
        unique_fn = []
        unique_var = []
        
        for f in self.data['functions']:
            key = (f.get('name', ''), f.get('language', ''))
            if key not in seen_fn:
                seen_fn[key] = f
                unique_fn.append(f)
            else:
                Term.print_warn(f"Dropped duplicate function: {f.get('name')} ({f.get('language')})")
        
        for v in self.data['variables']:
            key = (v.get('name', ''), v.get('language', ''))
            if key not in seen_var:
                seen_var[key] = v
                unique_var.append(v)
            else:
                Term.print_warn(f"Dropped duplicate variable: {v.get('name')} ({v.get('language')})")
        
        self.data['functions'] = unique_fn
        self.data['variables'] = unique_var
        Term.print_ok(f"Deduplicated: {len(seen_fn)} functions, {len(seen_var)} variables kept")

    # ─── AUDIT (nouveau) ──────────────────────────────────────────
    def audit(self):
        """Check for broken references, missing dependencies."""
        issues = []
        all_ids = {f['id'] for f in self.data['functions']} | {v['id'] for v in self.data['variables']}
        
        # Check function parameters that might reference other items (string references)
        for f in self.data['functions']:
            for p in f.get('parameters', []):
                default = p.get('default', '')
                if isinstance(default, str) and default.startswith('$'):
                    ref = default[1:]
                    if ref not in all_ids:
                        issues.append(f"Function {f['id']}: parameter '{p['name']}' default references unknown ID '{ref}'")
        
        # Check throws for non-existent exception types (simple heuristic)
        for f in self.data['functions']:
            for t in f.get('throws', []):
                if not re.match(r'^[A-Z][a-zA-Z0-9_]*$', t):
                    issues.append(f"Function {f['id']}: throw type '{t}' looks non-standard")
        
        # Check returns datatype
        for f in self.data['functions']:
            ret_type = f.get('returns', {}).get('datatype', 'void')
            if ret_type not in self.VALID_DATATYPES and ret_type != 'void':
                issues.append(f"Function {f['id']}: return datatype '{ret_type}' unknown")
        
        if issues:
            Term.print_header(f"\n🔍 AUDIT REPORT ({len(issues)} issues)")
            for issue in issues:
                Term.print_warn(issue)
        else:
            Term.print_ok("Audit passed — no issues detected")
        
        return issues

    # ─── BATCH SET (nouveau) ──────────────────────────────────────
    def batch_set(self, query, field, value, dry_run=False, field_type='name'):
        """Bulk update fields matching a query."""
        updated = 0
        for item in self.data['functions'] + self.data['variables']:
            field_value = item.get(field_type, '').lower()
            if query.lower() in field_value:
                if dry_run:
                    Term.print_info(f"[DRY RUN] Would update {item.get('id')}: {field} = {value}")
                else:
                    # Handle special fields that need type conversion
                    if field == 'tags' and isinstance(value, str):
                        item[field] = [v.strip() for v in value.split(',')]
                    elif field in ('parameters', 'returns') and isinstance(value, str):
                        try:
                            item[field] = json.loads(value)
                        except:
                            Term.print_warn(f"Could not parse JSON for {item.get('id')}.{field}")
                    else:
                        item[field] = value
                    Term.print_info(f"Updated {item.get('id')}: {field} = {value}")
                updated += 1
        
        if dry_run:
            Term.print_info(f"[DRY RUN] Would update {updated} items")
        else:
            Term.print_ok(f"Batch updated {updated} items")
        return updated

    # ─── ROLLBACK (nouveau) ───────────────────────────────────────
    def rollback(self, index=0):
        """Restore a previous backup. index=0 = most recent."""
        if not self._backup_list:
            Term.print_err("No backups found")
            return False
        
        if index >= len(self._backup_list):
            Term.print_err(f"Backup index {index} out of range (max {len(self._backup_list)-1})")
            return False
        
        backup_path = self._backup_list[index]
        Term.print_info(f"Rolling back to: {backup_path.name}")
        
        # Load backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Save as current
        self.save()
        Term.print_ok(f"Rollback complete. Current now equals {backup_path.name}")
        return True

    # ─── MERGE (amélioré) ─────────────────────────────────────────
    def merge(self, source_path, conflict_strategy='skip', dry_run=False):
        mgr = LibraryManagerBlack(source_path)
        mgr.clean()
        existing_ids = {f['id'] for f in self.data['functions']} | {v['id'] for v in self.data['variables']}
        
        merged_fn = merged_var = skipped_fn = skipped_var = 0
        
        for f in mgr.data['functions']:
            if f['id'] in existing_ids:
                if conflict_strategy == 'skip': skipped_fn += 1; continue
                if conflict_strategy == 'overwrite':
                    self.data['functions'] = [x for x in self.data['functions'] if x['id'] != f['id']]
                if conflict_strategy == 'suffix':
                    f['id'] = f"{f['id']}_merged"
            if not dry_run:
                self.data['functions'].append(f)
            merged_fn += 1

        for v in mgr.data['variables']:
            if v['id'] in existing_ids:
                if conflict_strategy == 'skip': skipped_var += 1; continue
                if conflict_strategy == 'overwrite':
                    self.data['variables'] = [x for x in self.data['variables'] if x['id'] != v['id']]
                if conflict_strategy == 'suffix':
                    v['id'] = f"{v['id']}_merged"
            if not dry_run:
                self.data['variables'].append(v)
            merged_var += 1

        if dry_run:
            Term.print_info(f"[DRY RUN] Would merge {merged_fn} fn, {merged_var} var. Skip: {skipped_fn} fn, {skipped_var} var")
        else:
            Term.print_ok(f"Merged {merged_fn} fn, {merged_var} var. Skipped: {skipped_fn} fn, {skipped_var} var.")

    # ─── CRUD ─────────────────────────────────────────────────────
    def add(self, entry_type='function', **kwargs):
        item = {'id': f"{'fn' if entry_type=='function' else 'var'}_{uuid.uuid4().hex[:8]}", **kwargs}
        lst = self.data['functions'] if entry_type == 'function' else self.data['variables']
        lst.append(item)
        Term.print_ok(f"Added {entry_type}: {item['id']}")

    def update(self, entry_id, updates):
        for item in self.data['functions'] + self.data['variables']:
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

    # ─── SEARCH & FILTER (amélioré) ───────────────────────────────
    def search(self, query, field='name', language=None, famille=None, tag=None, regex=False):
        query = query.lower()
        results = []
        for item in self.data['functions'] + self.data['variables']:
            if language and item.get('language') != language: continue
            if famille and item.get('famille') != famille: continue
            if tag and tag not in [t.lower() for t in item.get('tags', [])]: continue
            val = str(item.get(field, '')).lower()
            match = re.search(query, val) if regex else query in val
            if match:
                results.append(item)
        return results

    # ─── STATS (amélioré) ─────────────────────────────────────────
    def stats(self, detailed=False):
        fns = self.data['functions']
        vars_ = self.data['variables']
        langs = defaultdict(int)
        familles = defaultdict(int)
        tag_counts = defaultdict(int)
        
        for i in fns + vars_:
            l = i.get('language', 'Unknown')
            langs[l] += 1
        for i in fns:
            f = i.get('famille', 'Uncategorized')
            familles[f] += 1
        for i in fns + vars_:
            for t in i.get('tags', []):
                tag_counts[t] += 1
        
        stats = {'total_fn': len(fns), 'total_var': len(vars_), 'languages': dict(langs), 'families': dict(familles)}
        if detailed:
            stats['top_tags'] = dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:10])
            stats['avg_params'] = sum(len(f.get('parameters', [])) for f in fns) / max(len(fns), 1)
            stats['has_source'] = sum(1 for f in fns if f.get('source'))
        return stats

    # ─── VALIDATE (amélioré) ──────────────────────────────────────
    def validate(self, strict=False):
        errors = []
        for lst, name in [(self.data['functions'], 'functions'), (self.data['variables'], 'variables')]:
            for i, item in enumerate(lst):
                req = self.REQUIRED_FN if name == 'functions' else self.REQUIRED_VAR
                missing = req - set(item.keys())
                if missing: errors.append(f"{name}[{i}] missing: {missing}")
                if not isinstance(item.get('parameters' if name=='functions' else 'tags', []), list):
                    errors.append(f"{name}[{i}] parameters/tags must be list")
                
                if strict and name == 'functions':
                    # Validate parameter structure
                    for j, p in enumerate(item.get('parameters', [])):
                        if 'name' not in p: errors.append(f"{name}[{i}] param[{j}] missing 'name'")
                        if 'datatype' not in p: errors.append(f"{name}[{i}] param[{j}] missing 'datatype'")
                    
                    # Validate returns
                    ret = item.get('returns', {})
                    if not isinstance(ret, dict): errors.append(f"{name}[{i}] 'returns' must be dict")
                    elif 'datatype' not in ret: errors.append(f"{name}[{i}] 'returns' missing 'datatype'")
        
        return errors if errors else None

    # ─── SAVE & BACKUP ────────────────────────────────────────────
    def backup(self):
        if not self.path: return
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        bak = self.path.with_suffix(f'.{ts}.bak')
        shutil.copy2(self.path, bak)
        self._scan_backups()
        Term.print_ok(f"Backed up -> {bak.name}")

    def save(self, filepath=None, pretty=True, minify=False):
        p = Path(filepath) if filepath else self.path
        if not p: raise ValueError("No target path specified")
        self.backup()
        indent = None if minify else 2
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=indent, ensure_ascii=False, sort_keys=False)
        Term.print_ok(f"Saved -> {p.name} {'(minified)' if minify else '(pretty)'}")

    # ─── EXPORT CSV (amélioré) ────────────────────────────────────
    def export_csv(self, outpath=None):
        p = outpath or self.path.with_suffix('.csv')
        with open(p, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'type', 'name', 'language', 'famille', 'datatype', 'description', 'tags'])
            writer.writeheader()
            for item in self.data['functions']:
                row = {
                    'id': item.get('id', ''),
                    'type': 'function',
                    'name': item.get('name', ''),
                    'language': item.get('language', ''),
                    'famille': item.get('famille', ''),
                    'datatype': item.get('returns', {}).get('datatype', 'void'),
                    'description': item.get('description', ''),
                    'tags': ', '.join(item.get('tags', []))
                }
                writer.writerow(row)
            for item in self.data['variables']:
                row = {
                    'id': item.get('id', ''),
                    'type': 'variable',
                    'name': item.get('name', ''),
                    'language': item.get('language', ''),
                    'famille': '',
                    'datatype': item.get('datatype', ''),
                    'description': item.get('description', ''),
                    'tags': ', '.join(item.get('tags', []))
                }
                writer.writerow(row)
        Term.print_ok(f"Exported CSV -> {p.name}")


# ═══════════════════════════════════════════════════════════════════
#  CLI INTERFACE — BLACK EDITION
# ═══════════════════════════════════════════════════════════════════
def cli():
    parser = argparse.ArgumentParser(
        prog='cf_lib_manager_black',
        description='CodeForge Library JSON Manager v2.0 — BLACK EDITION',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  cf_lib_manager_black lib.json stats --detailed
  cf_lib_manager_black lib.json search "AD" --lang PowerShell --family ActiveDirectory
  cf_lib_manager_black lib.json batch-set "Logging" --field tags --value "logging,audit"
  cf_lib_manager_black lib.json diff other.json
  cf_lib_manager_black lib.json audit
  cf_lib_manager_black lib.json rollback 0
  cf_lib_manager_black init new_lib.json --name "My Library"
"""
    )
    parser.add_argument('file', nargs='?', help='Target library.json path (not needed for init)')
    sub = parser.add_subparsers(dest='command', required=True)

    # init (nouveau)
    p_init = sub.add_parser('init', help='Create a new library skeleton')
    p_init.add_argument('output', help='Output file path')
    p_init.add_argument('--name', default='New Library', help='Library name')

    # clean
    p_clean = sub.add_parser('clean', help='Remove invalid entries, normalize keys, fill defaults')
    p_clean.add_argument('--deep', action='store_true', help='Also validate datatypes/languages')
    p_clean.add_argument('--fix-ids', action='store_true', help='Repair & deduplicate IDs')
    p_clean.add_argument('--dedup', action='store_true', help='Remove duplicate entries')
    p_clean.add_argument('-s', '--save', action='store_true', help='Auto-save after clean')

    # show
    p_show = sub.add_parser('show', help='Pretty-print library JSON')
    p_show.add_argument('id', nargs='?', help='Specific entry ID')
    p_show.add_argument('--no-color', action='store_true', help='Disable ANSI colors')

    # diff
    p_diff = sub.add_parser('diff', help='Compare with another library')
    p_diff.add_argument('other', help='Other library.json path')

    # audit
    sub.add_parser('audit', help='Check for broken references and issues')

    # dedup
    sub.add_parser('dedup', help='Remove duplicate entries (same name+language)')

    # rollback
    p_rollback = sub.add_parser('rollback', help='Restore a previous backup')
    p_rollback.add_argument('index', nargs='?', type=int, default=0, help='Backup index (0=most recent)')

    # merge
    p_merge = sub.add_parser('merge', help='Merge another library.json')
    p_merge.add_argument('source', help='Source library.json')
    p_merge.add_argument('--strategy', choices=['skip', 'overwrite', 'suffix'], default='skip')
    p_merge.add_argument('--dry-run', action='store_true', help='Preview changes without saving')

    # batch-set
    p_batch = sub.add_parser('batch-set', help='Bulk update fields')
    p_batch.add_argument('query', help='Search string')
    p_batch.add_argument('--field', required=True, help='Field to update (name, famille, tags, etc.)')
    p_batch.add_argument('--value', required=True, help='New value')
    p_batch.add_argument('--field-type', default='name', choices=['name', 'id', 'famille'], help='Which field to match against')
    p_batch.add_argument('--dry-run', action='store_true', help='Preview without saving')

    # search
    p_search = sub.add_parser('search', help='Search elements')
    p_search.add_argument('query')
    p_search.add_argument('--field', default='name')
    p_search.add_argument('--lang')
    p_search.add_argument('--family')
    p_search.add_argument('--tag')
    p_search.add_argument('--regex', action='store_true')
    p_search.add_argument('--json', action='store_true', help='Output as JSON')
    p_search.add_argument('--table', action='store_true', help='Output as formatted table')

    # stats
    p_stats = sub.add_parser('stats', help='Show library statistics')
    p_stats.add_argument('--detailed', action='store_true', help='Show tags, avg params, etc.')
    p_stats.add_argument('--json', action='store_true', help='Output as JSON')

    # validate
    p_val = sub.add_parser('validate', help='Schema validation report')
    p_val.add_argument('--strict', action='store_true', help='Validate parameter structure')

    # export
    p_export = sub.add_parser('export', help='Export to CSV')
    p_export.add_argument('--output', help='Output file path')

    # add
    p_add = sub.add_parser('add', help='Add new function/variable')
    p_add.add_argument('--type', choices=['function', 'variable'], default='function')
    p_add.add_argument('--name', required=True)
    p_add.add_argument('--lang', required=True)
    p_add.add_argument('--family', default='')
    p_add.add_argument('--desc', default='')
    p_add.add_argument('--datatype', default='void', help='For variables or return type')

    # delete
    p_del = sub.add_parser('delete', help='Delete by ID')
    p_del.add_argument('id')

    args = parser.parse_args()

    # Handle init separately (no file needed)
    if args.command == 'init':
        LibraryManagerBlack.init_template(args.output, args.name)
        return

    if not args.file:
        Term.print_err("File path required (except for 'init')")
        sys.exit(1)

    mgr = LibraryManagerBlack(args.file)

    try:
        if args.command == 'clean':
            mgr.clean(deep=args.deep)
            if args.fix_ids: mgr.normalize_ids()
            if args.dedup: mgr.dedup()
            if args.save: mgr.save()

        elif args.command == 'show':
            mgr.show(args.id, color=not args.no_color)

        elif args.command == 'diff':
            mgr.diff(args.other)

        elif args.command == 'audit':
            mgr.audit()

        elif args.command == 'dedup':
            mgr.dedup()
            mgr.save()

        elif args.command == 'rollback':
            mgr.rollback(args.index)

        elif args.command == 'merge':
            mgr.merge(args.source, args.strategy, dry_run=args.dry_run)
            if not args.dry_run: mgr.save()

        elif args.command == 'batch-set':
            mgr.batch_set(args.query, args.field, args.value, args.dry_run, args.field_type)
            if not args.dry_run: mgr.save()

        elif args.command == 'search':
            results = mgr.search(args.query, args.field, args.lang, args.family, args.tag, args.regex)
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            elif args.table:
                print(f"\n{Term.HEADER}{'ID':<12} {'Name':<30} {'Language':<12} {'Family':<15}{Term.ENDC}")
                print(f"{Term.DIM}{'-'*75}{Term.ENDC}")
                for r in results:
                    print(f"{Term.OKCYAN}{r.get('id', ''):<12}{Term.ENDC} {r.get('name', ''):<30} {r.get('language', ''):<12} {r.get('famille', ''):<15}")
                print(f"{Term.DIM}{'-'*75}{Term.ENDC}")
                print(f"{Term.OKGREEN}{len(results)} results{Term.ENDC}")
            else:
                print(f"\n{Term.HEADER}🔍 Found {len(results)} results:{Term.ENDC}")
                for r in results:
                    print(f"  {Term.OKCYAN}{r.get('id', ''):12} | {r.get('name', ''):30} | {r.get('language', ''):12} | {r.get('famille', ''):15}{Term.ENDC}")

        elif args.command == 'stats':
            s = mgr.stats(detailed=args.detailed)
            if args.json:
                print(json.dumps(s, indent=2, ensure_ascii=False))
            else:
                print(f"\n{Term.HEADER}📊 Library Statistics:{Term.ENDC}")
                print(f"  Functions: {Term.BOLD}{s['total_fn']}{Term.ENDC}  |  Variables: {Term.BOLD}{s['total_var']}{Term.ENDC}")
                print(f"  Languages: {pformat(s['languages'])}")
                print(f"  Families:  {pformat(s['families'])}")
                if args.detailed:
                    print(f"  Top tags:  {pformat(s.get('top_tags', {}))}")
                    print(f"  Avg params per function: {s.get('avg_params', 0):.1f}")
                    print(f"  Functions with source: {s.get('has_source', 0)}/{s['total_fn']}")

        elif args.command == 'validate':
            errs = mgr.validate(strict=args.strict)
            if errs:
                print(f"\n{Term.FAIL}❌ Validation Failed ({len(errs)} issues):{Term.ENDC}")
                for e in errs: print(f"  • {e}")
            else:
                Term.print_ok("✅ Schema valid. No issues detected.")

        elif args.command == 'export':
            mgr.export_csv(args.output)

        elif args.command == 'add':
            kwargs = {
                'name': args.name, 
                'language': args.lang, 
                'famille': args.family, 
                'description': args.desc
            }
            if args.type == 'variable':
                kwargs['datatype'] = args.datatype
            else:
                kwargs['returns'] = {'datatype': args.datatype, 'description': ''}
            mgr.add(args.type, **kwargs)
            mgr.save()

        elif args.command == 'delete':
            mgr.delete(args.id)
            mgr.save()

    except Exception as e:
        Term.print_err(f"Execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    cli()