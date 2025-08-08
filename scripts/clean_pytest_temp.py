import getpass
import os
import shutil
import stat
import tempfile
from pathlib import Path


def main() -> int:
    user = getpass.getuser()
    root = Path(tempfile.gettempdir()) / f"pytest-of-{user}"
    print(f"[info] target={root}")
    if not root.exists():
        print("[info] nothing to clean")
        return 0

    def onerror(func, path, exc_info):
        try:
            Path(path).chmod(stat.S_IWUSR | stat.S_IREAD)
            func(path)
        except Exception:
            print(f"[warn] cannot remove {path}")

    try:
        shutil.rmtree(root, onerror=onerror)
        print("[ok] removed")
        return 0
    except PermissionError as e:  # pragma: no cover (環境依存)
        print(f"[error] permission: {e}")
        if os.name == "nt":
            print(
                f'[hint] Run elevated: takeown /F "{root}" /R /D Y && '
                f'icacls "{root}" /grant %USERNAME%:F /T /C'
            )
        else:
            print(f"[hint] Try: sudo rm -rf '{root}'")
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
