import json

import redis

from core.config import get_config


class CacheService:
    """Redis-backed cache with versioned namespaces."""

    def __init__(self):
        self.config = get_config()
        self._client = None
        self._available = None

    def _client_or_none(self):
        if self._available is False:
            return None
        if self._client is not None:
            return self._client
        try:
            client = redis.Redis.from_url(self.config.REDIS_URL, decode_responses=True)
            client.ping()
            self._client = client
            self._available = True
            return self._client
        except Exception:
            self._available = False
            return None

    def _namespace_version(self, namespace):
        client = self._client_or_none()
        if client is None:
            return "1"
        key = f"cache:ns:{namespace}"
        version = client.get(key)
        if version is None:
            client.set(key, "1")
            return "1"
        return version

    def build_key(self, namespace, identifier):
        version = self._namespace_version(namespace)
        return f"cache:{namespace}:v{version}:{identifier}"

    def get_json(self, namespace, identifier):
        client = self._client_or_none()
        if client is None:
            return None
        payload = client.get(self.build_key(namespace, identifier))
        if payload is None:
            return None
        try:
            return json.loads(payload)
        except Exception:
            return None

    def set_json(self, namespace, identifier, payload, ttl_seconds=None):
        client = self._client_or_none()
        if client is None:
            return
        ttl = ttl_seconds or self.config.CACHE_TTL_SECONDS
        client.setex(
            self.build_key(namespace, identifier),
            int(ttl),
            json.dumps(payload, default=str),
        )

    def bump_namespace(self, namespace):
        client = self._client_or_none()
        if client is None:
            return
        key = f"cache:ns:{namespace}"
        try:
            client.incr(key)
        except Exception:
            client.set(key, "1")


cache_service = CacheService()

