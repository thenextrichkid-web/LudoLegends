"""API tests for authentication and authorization — OTP, tokens, role checks."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from tests.conftest import auth_header


@pytest.mark.asyncio
class TestAuthAPI:
    async def test_request_otp(self, client: AsyncClient, db: AsyncSession):
        resp = await client.post(
            "/api/auth/otp/request",
            json={"phone": "+919999999999"},
        )
        assert resp.status_code == 200
        assert "OTP sent" in resp.json().get("message", "")

    async def test_verify_otp_wrong_otp(self, client: AsyncClient, db: AsyncSession):
        await client.post("/api/auth/otp/request", json={"phone": "+919999999998"})
        resp = await client.post(
            "/api/auth/otp/verify",
            json={"phone": "+919999999998", "otp": "000000"},
        )
        assert resp.status_code == 400

    async def test_verify_otp_success(self, client: AsyncClient, db: AsyncSession):
        await client.post("/api/auth/otp/request", json={"phone": "+919999999997"})
        resp = await client.post(
            "/api/auth/otp/verify",
            json={"phone": "+919999999997", "otp": "123456"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_get_me_authenticated(self, client: AsyncClient, test_user: User, user_token: str):
        resp = await client.get("/api/auth/me", headers=auth_header(user_token))
        assert resp.status_code == 200
        assert resp.json()["id"] == test_user.id

    async def test_get_me_no_token(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestAuthorization:
    async def test_player_cannot_access_admin(self, client: AsyncClient, test_user: User, user_token: str):
        resp = await client.get("/api/admin/dashboard", headers=auth_header(user_token))
        assert resp.status_code == 403

    async def test_admin_can_access_admin(self, client: AsyncClient, test_admin: User, admin_token: str):
        resp = await client.get("/api/admin/dashboard", headers=auth_header(admin_token))
        assert resp.status_code == 200

    async def test_admin_cannot_change_roles(self, client: AsyncClient, test_admin: User, admin_token: str):
        resp = await client.put(
            "/api/admin/users/some-id/role",
            params={"role": "super_admin"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 403

    async def test_super_admin_can_change_roles(self, client: AsyncClient, super_admin: User, super_admin_token: str):
        resp = await client.put(
            "/api/admin/users/nonexistent/role",
            params={"role": "admin"},
            headers=auth_header(super_admin_token),
        )
        assert resp.status_code in (400, 404)

    async def test_admin_cannot_deactivate_self(self, client: AsyncClient, test_admin: User, admin_token: str):
        resp = await client.put(
            f"/api/admin/users/{test_admin.id}/status",
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 400
