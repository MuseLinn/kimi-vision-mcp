import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_server_imports():
    import server

    assert hasattr(server, "main")
