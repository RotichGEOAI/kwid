"""
api/base.py
Shared HTTP client used by every connector in Module 3. Provides:
  - retry/backoff via urllib3.Retry
  - a uniform timeout
  - a lightweight on-disk JSON cache (TTL-based) to avoid hammering
    free/public endpoints during development
  - a documented fallback contract: every connector's `fetch_*` method
    returns (data, meta) where meta["status"] is one of
    "success" | "fallback" | "error", so calling code (services/) and
    the UI can show provenance rather than pretend all data is live.
"""
import hashlib
import json
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config
from core.logging_config import get_logger

logger = get_logger(__name__)

CACHE_DIR = Config.DATA_DIR / "raw" / "_api_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class BaseAPIClient:
    """Common request/caching/retry logic for all external connectors."""

    source_name = "BASE"

    def __init__(self, timeout=None, max_retries=None):
        self.timeout = timeout or Config.HTTP_TIMEOUT_SECONDS
        self.session = requests.Session()
        retries = Retry(
            total=max_retries or Config.HTTP_MAX_RETRIES,
            backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    # ---------- caching ----------
    def _cache_path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode()).hexdigest()[:24]
        return CACHE_DIR / f"{self.source_name}_{digest}.json"

    def _read_cache(self, key: str, ttl: int):
        path = self._cache_path(key)
        if not path.exists():
            return None
        if time.time() - path.stat().st_mtime > ttl:
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def _write_cache(self, key: str, payload):
        try:
            self._cache_path(key).write_text(json.dumps(payload))
        except OSError:
            logger.warning("Could not write cache for %s", key)

    # ---------- core request ----------
    def get(self, url, params=None, headers=None, ttl=None, use_cache=True):
        """GET with caching + retries. Raises requests.RequestException on failure."""
        ttl = ttl if ttl is not None else Config.__dict__.get("CACHE_TTL_SECONDS", 3600)
        cache_key = f"{url}?{json.dumps(params or {}, sort_keys=True)}"

        if use_cache:
            cached = self._read_cache(cache_key, ttl)
            if cached is not None:
                logger.debug("[%s] cache hit for %s", self.source_name, url)
                return cached

        resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if use_cache:
            self._write_cache(cache_key, data)
        return data

    def safe_fetch(self, fetch_fn, fallback_fn, *args, **kwargs):
        """
        Wraps a live-fetch callable with a fallback callable. Returns
        (data, meta) so callers always get *something* renderable and
        know whether it's live or synthetic.
        """
        try:
            data = fetch_fn(*args, **kwargs)
            return data, {"status": "success", "source": self.source_name}
        except Exception as exc:  # noqa: BLE001 - deliberately broad at the boundary
            logger.warning("[%s] live fetch failed (%s); using fallback.", self.source_name, exc)
            if not Config.ALLOW_SYNTHETIC_FALLBACK:
                return None, {"status": "error", "source": self.source_name, "detail": str(exc)}
            data = fallback_fn(*args, **kwargs)
            return data, {"status": "fallback", "source": self.source_name, "detail": str(exc)}
