import pytest
from tests.conftest import make_client


@pytest.mark.asyncio
async def test_conceal_and_reveal():
    async with make_client() as client:
        resp = await client.post("/keys/conceal", json={"secret_data": {"key": "value"}})
        secret_id = resp.json()["id"]

        resp2 = await client.post(f"/keys/secrets/{secret_id}/reveal")
        assert resp2.status_code == 200
        assert resp2.json()["secret"] == "value"


@pytest.mark.asyncio
async def test_reveal_twice_fails():
    async with make_client() as client:
        resp = await client.post("/keys/conceal", json={"secret_data": {"key": "value"}})
        secret_id = resp.json()["id"]

        await client.post(f"/keys/secrets/{secret_id}/reveal")
        resp2 = await client.post(f"/keys/secrets/{secret_id}/reveal")
        assert resp2.status_code == 403


@pytest.mark.asyncio
async def test_wrong_password_then_lockout():
    async with make_client(client_ip="9.9.9.9") as client:
        resp = await client.post(
            "/keys/conceal",
            json={"secret_data": {"key": "value", "password": "correct"}},
        )
        secret_id = resp.json()["id"]

        for _ in range(4):
            r = await client.post(
                f"/keys/secrets/{secret_id}/reveal",
                json={"password": "wrong"},
            )
            assert r.status_code == 403
            assert r.json()["detail"] == "Incorrect password"

        r5 = await client.post(
            f"/keys/secrets/{secret_id}/reveal",
            json={"password": "wrong"},
        )
        assert r5.status_code == 403
        assert "Too many attempts" in r5.json()["detail"]

        r6 = await client.post(
            f"/keys/secrets/{secret_id}/reveal",
            json={"password": "correct"},
        )
        assert "Too many attempts" in r6.json()["detail"]


@pytest.mark.asyncio
async def test_different_clients_dont_affect_each_other():
    async with make_client() as client_a, make_client(client_ip="8.8.8.8") as client_b:
        resp = await client_a.post(
            "/keys/conceal",
            json={"secret_data": {"key": "value", "password": "correct"}},
        )
        secret_id = resp.json()["id"]

        for _ in range(5):
            await client_a.post(f"/keys/secrets/{secret_id}/reveal", json={"password": "wrong"})

        r = await client_b.post(f"/keys/secrets/{secret_id}/reveal", json={"password": "correct"})
        assert r.status_code == 200