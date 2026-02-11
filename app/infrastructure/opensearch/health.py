from opensearchpy import AsyncOpenSearch


async def check_opensearch_health(client: AsyncOpenSearch) -> bool:
    try:
        health = await client.cluster.health()
        return health.get("status") in {"green", "yellow"}
    except Exception:
        return False
