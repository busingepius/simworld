import asyncio
import httpx
from demo import create_test_org

async def test_fetches():
    print("Setting up organization...")
    org_id = await create_test_org()
    print(f"Org ID: {org_id}")
    
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Login
        resp = await client.post("/api/auth/login", data={"username": "Acme Corp", "password": "any"})
        resp.raise_for_status()
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create World
        resp = await client.post("/api/worlds/", json={
            "name": "Test World",
            "domain": "Testing",
            "config": {}
        }, headers=headers)
        resp.raise_for_status()
        world_id = resp.json()["id"]
        print(f"World ID: {world_id}")
        
        # Test frontend calls
        try:
            print("Fetching world...")
            r = await client.get(f"/api/worlds/{world_id}", headers=headers)
            r.raise_for_status()
            
            print("Fetching agents...")
            r = await client.get(f"/api/worlds/{world_id}/agents", headers=headers)
            r.raise_for_status()
            
            print("Fetching runs...")
            r = await client.get(f"/api/worlds/{world_id}/runs", headers=headers)
            r.raise_for_status()
            
            print("Fetching reports...")
            r = await client.get(f"/api/worlds/{world_id}/reports", headers=headers)
            r.raise_for_status()
            
            print("SUCCESS! All fetches worked.")
        except Exception as e:
            print(f"FAILED: {e}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)

if __name__ == "__main__":
    asyncio.run(test_fetches())
