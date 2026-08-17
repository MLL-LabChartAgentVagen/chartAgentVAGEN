"""按请求内容哈希缓存回复。

作用有两个：同一份提示词重跑不再花钱，以及让"整条流水线可复现"这句话
在有 LLM 的那一步也成立。
"""

from __future__ import annotations

import json
from hashlib import blake2b
from pathlib import Path

from .types import Response, Usage


class ResponseCache:
    def __init__(self, directory: str | Path) -> None:
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)

    def path(self, key: str) -> Path:
        digest = blake2b(key.encode("utf-8"), digest_size=12).hexdigest()
        return self.dir / f"{digest}.json"

    def get(self, key: str) -> Response | None:
        path = self.path(key)
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        return Response(raw["text"], raw["model"], Usage(**raw["usage"]),
                        raw.get("stop_reason", "end_turn"), raw.get("latency_s", 0.0))

    def put(self, key: str, response: Response) -> None:
        self.path(key).write_text(json.dumps({
            "key": key,
            "text": response.text,
            "model": response.model,
            "usage": response.usage.__dict__,
            "stop_reason": response.stop_reason,
            "latency_s": response.latency_s,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
