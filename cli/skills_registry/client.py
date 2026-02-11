"""HTTP client for Skills Registry API."""

import httpx
from .config import get_registry_url, get_api_key


class RegistryClient:
    def __init__(self):
        self._client = httpx.Client(
            base_url=get_registry_url(),
            headers={"X-API-Key": get_api_key()},
            timeout=30.0,
        )

    def _handle(self, resp: httpx.Response) -> dict | list | None:
        if resp.status_code == 204:
            return None
        if not resp.is_success:
            detail = resp.json().get("detail", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            raise RuntimeError(f"API error ({resp.status_code}): {detail}")
        return resp.json()

    # Skills
    def search_skills(self, keyword: str | None = None, tag: str | None = None) -> dict:
        params = {}
        if keyword: params["keyword"] = keyword
        if tag: params["tag"] = tag
        return self._handle(self._client.get("/api/v1/skills", params=params))

    def get_skill_install(self, skill_id: int) -> dict:
        return self._handle(self._client.get(f"/api/v1/skills/{skill_id}/install"))

    def create_skill(self, data: dict) -> dict:
        return self._handle(self._client.post("/api/v1/skills", json=data))

    def record_skill_install(self, skill_id: int, agent_type: str = "kiro"):
        self._handle(self._client.post(f"/api/v1/skills/{skill_id}/install", params={"agent_type": agent_type}))

    # MCPs
    def search_mcps(self, keyword: str | None = None) -> dict:
        params = {}
        if keyword: params["keyword"] = keyword
        return self._handle(self._client.get("/api/v1/mcps", params=params))

    def get_mcp_install(self, mcp_id: int) -> dict:
        return self._handle(self._client.get(f"/api/v1/mcps/{mcp_id}/install"))

    def record_mcp_install(self, mcp_id: int, agent_type: str = "kiro"):
        self._handle(self._client.post(f"/api/v1/mcps/{mcp_id}/install", params={"agent_type": agent_type}))

    # Agents
    def search_agents(self, keyword: str | None = None) -> dict:
        params = {}
        if keyword: params["keyword"] = keyword
        return self._handle(self._client.get("/api/v1/agents", params=params))

    def get_agent_install(self, agent_id: int) -> dict:
        return self._handle(self._client.get(f"/api/v1/agents/{agent_id}/install"))

    def record_agent_install(self, agent_id: int, agent_type: str = "kiro"):
        self._handle(self._client.post(f"/api/v1/agents/{agent_id}/install", params={"agent_type": agent_type}))

    # Search
    def search_all(self, keyword: str) -> dict:
        return self._handle(self._client.get("/api/v1/search", params={"q": keyword}))
