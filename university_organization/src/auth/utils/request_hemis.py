from httpx import AsyncClient

async def fetch_hemis_data(base_url: str, endpoint: str, token: str) -> dict:
    """
    Fetch data from a Hemis API endpoint using a bearer token.

    Args:
        base_url (str): The base URL of the Hemis API.
        endpoint (str): The specific API endpoint to call.
        token (str): Bearer token for authorization.

    Returns:
        dict: The "data" field from the JSON response, or an empty dict if not present.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    async with AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        response.raise_for_status()
        return response.json().get("data", {})
