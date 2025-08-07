import os
import shutil
import stat
import sys
import tempfile
import getpass
from pathlib import Path


def main() -> int:
    user = getpass.getuser()
    root = Path(tempfile.gettempdir()) / f"pytest-of-{user}"
    print(f"[info] target={root}")
    if not root.exists():
        print("[info] nothing to clean")
        return 0

    def onerror(func, path, exc_info):  # noqa: D401
        try:
            os.chmod(path, stat.S_IWUSR | stat.S_IREAD)
            func(path)
        except Exception:  # noqa: BLE001
            print(f"[warn] cannot remove {path}")

    try:
        shutil.rmtree(root, onerror=onerror)
        print("[ok] removed")
        return 0
    except PermissionError as e:  # pragma: no cover (環境依存)
        print(f"[error] permission: {e}")
        if os.name == "nt":
            print("[hint] Run elevated: takeown /F \"{}\" /R /D Y && icacls \"{}\" /grant %USERNAME%:F /T /C".format(root, root))
        else:
            print("[hint] Try: sudo rm -rf '{}'".format(root))
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
