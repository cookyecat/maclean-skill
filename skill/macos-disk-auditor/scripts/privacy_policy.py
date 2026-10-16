#!/usr/bin/env python3
"""Privacy-first filesystem scope policy. No filesystem recursion or content reads.

AI assesses reclaimability and conditions. This module only enforces technical
scope, privacy invariants and safe discovery locations; it never approves deletion.
"""
from __future__ import annotations
from pathlib import Path
import re

POLICY_ID = 'privacy-safe-v1'
EXCLUDED_CLASSES = ('personal_documents', 'communications', 'cloud_data',
                    'credentials', 'app_profiles', 'unselected_projects')

# Exact, known regenerable technical locations. This is a scanning boundary,
# NOT a recommendation to delete anything found here.
EXACT = {
    '.npm/_cacache': ('npm_cache', 'home'),
    '.cache/uv': ('uv_cache', 'home'),
    '.cache/puppeteer': ('puppeteer_cache', 'home'),
    'Library/Caches/ms-playwright': ('downloaded_runtime', 'library'),
}
DYNAMIC = (
    ('.npm/_npx', r'[0-9a-f]{8,40}', 'npx_install', 'home'),
    ('.cache/codex-runtimes', r'codex-runtime-install-[A-Za-z0-9_-]{4,40}', 'codex_runtime_installer', 'home'),
    ('.codex/packages/app-server-daemon/releases', r'\d+\.\d+\.\d+(?:-[A-Za-z0-9._-]+)?', 'codex_daemon_old', 'home'),
    ('Library/Application Support/Cursor/User/globalStorage/anysphere.cursor-agent-worker/agent-cli/.local/share/cursor-agent/versions', r'20\d\d\.\d\d\.\d\d[-_][A-Za-z0-9-]+', 'old_version', 'library'),
)
SENSITIVE_PARTS = {'documents', 'desktop', 'downloads', 'pictures', 'movies', 'music',
                   'mail', 'messages', 'keychains', 'photos', 'mobile documents',
                   'cloudstorage', 'mobilesync', 'clouddocs', 'addressbook', 'facetime',
                   'knowledge', 'fileprovider', 'com.apple.tcc', 'containers',
                   'group containers', '.ssh', '.gnupg', '.git'}

class PolicyDenied(ValueError):
    pass


def _relative(home: Path, target: Path) -> str:
    home = Path(home).expanduser().absolute()
    target = Path(target).expanduser().absolute()
    try:
        parts = target.relative_to(home).parts
    except ValueError:
        raise PolicyDenied('target outside authorized HOME') from None
    if not parts or any(p in ('', '.', '..') for p in parts):
        raise PolicyDenied('HOME parent or nonliteral target is not scannable')
    # No symlink ancestors, including existing target. Blocks escaping through
    # a link to a sensitive tree without resolving or traversing its contents.
    cur = home
    if cur.is_symlink():
        raise PolicyDenied('symlinked HOME requires manual handling')
    for part in parts:
        cur = cur / part
        if cur.is_symlink():
            raise PolicyDenied('symlink component forbidden')
    return '/'.join(parts)


def authorize_scan(home: Path, target: Path, project_root: Path | None = None, user_selected_cache: bool = False):
    """Return (kind, group) for an approved *scan location*, never deletion approval.

    Caller explicitly supplies project_root to permit only its Cargo target.
    No permission for project source, git metadata or arbitrary project children.
    """
    relative = _relative(home, target)
    if relative in EXACT:
        return EXACT[relative]
    for parent, pattern, kind, group in DYNAMIC:
        prefix = parent + '/'
        if relative.startswith(prefix) and re.fullmatch(pattern, relative[len(prefix):]):
            return kind, group
    if user_selected_cache and relative.startswith('Library/Caches/'):
        parts = Path(relative).parts
        if len(parts) == 3 and parts[-1].casefold() not in SENSITIVE_PARTS:
            return 'agent_reviewed_cache', 'user_selected'
        raise PolicyDenied('Only a user-selected exact application-cache leaf is allowed')
    if project_root is not None:
        project_rel = _relative(home, project_root)
        if (any(p.casefold() in SENSITIVE_PARTS for p in Path(project_rel).parts)
                or not (project_rel.startswith('Developer/') or project_rel.startswith('.codex/worktrees/'))):
            raise PolicyDenied('selected project root outside safe developer locations')
        if relative == project_rel + '/target':
            return 'cargo_target', 'developer'
    raise PolicyDenied('path not in privacy-safe technical scan scope')


def discover(home: Path, group: str | None = None, project_root: Path | None = None):
    """Discover exact approved technical leaves; never enumerate Home/Library roots.

    Glob only known technical staging/version directories; no broad discovery.
    """
    home = Path(home).expanduser().absolute()
    found = []
    for rel, (kind, section) in EXACT.items():
        if group in (None, section):
            p = home / rel
            if not p.is_symlink() and p.is_dir():
                authorize_scan(home, p)
                found.append((p, kind, section))
    for parent, regex, kind, section in DYNAMIC:
        if group not in (None, section):
            continue
        directory = home / parent
        if directory.is_symlink() or not directory.is_dir():
            continue
        # Confirm no ancestor symlink before enumerating the known runtime dir.
        _relative(home, directory)
        for p in sorted(directory.iterdir()):
            if re.fullmatch(regex, p.name) and not p.is_symlink() and p.is_dir():
                authorize_scan(home, p)
                found.append((p, kind, section))
    if project_root is not None and group in (None, 'developer'):
        p = Path(project_root).expanduser().absolute() / 'target'
        authorize_scan(home, p, project_root=project_root)
        if p.is_dir() and not p.is_symlink():
            found.append((p, 'cargo_target', 'developer'))
    return found


def public_id(kind: str, index: int):
    return f'{kind}-{index:03d}'


def protected_cleanup_target(home: Path, target: Path) -> None:
    """Hard veto for sensitive locations, independent of AI decisions/plan consent."""
    rel = _relative(home, target)
    # The legacy Library cleanup kinds may allow narrow app cache/log leaves,
    # but not any leaf underneath a sensitive personal-data parent.
    lower = [p.casefold() for p in Path(rel).parts]
    if any(part in SENSITIVE_PARTS for part in lower):
        raise PolicyDenied('privacy-protected location may not be cleaned by this Skill')
    # Refuse broad directories even if the upstream kind validator were relaxed.
    if rel in {'Library', 'Library/Caches', 'Library/Application Support', '.npm', '.cache', '.codex', 'Developer'}:
        raise PolicyDenied('broad parent cleanup forbidden')
