import os
from pathlib import Path
import shutil
import sys
import uuid

import pytest


sakura_source = Path(os.environ["SAKURA_SOURCE"])
sys.path[:0] = [
    str(Path(__file__).resolve().parents[1]),
    str(sakura_source),
    str(sakura_source / "app" / "plugin_sdk"),
]


@pytest.fixture
def tmp_path():
    """测试数据留在仓库内，避免 Windows 临时目录的权限问题。"""
    path = Path(__file__).resolve().parents[1] / "temp" / uuid.uuid4().hex
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path)
