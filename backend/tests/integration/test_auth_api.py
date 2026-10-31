def test_customer_registration_success(client):
    payload = {
        "full_name": "Bob Builder",
        "email": "bob@build.test",
        "password": "StrongPassword#2026",
        "company_name": "Bob Contracting",
        "phone": "+1987654321",
        "address": "456 Build Way",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "bob@build.test"
    assert data["role"] == "customer"
    assert data["is_active"] is True
    assert data["customer_profile"]["company_name"] == "Bob Contracting"
    assert "password_hash" not in data


def test_customer_registration_weak_password_rejected(client):
    payload = {
        "full_name": "Weak User",
        "email": "weak@user.test",
        "password": "weak",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_customer_registration_duplicate_email(client, seeded_customer):
    payload = {
        "full_name": "Duplicate Alice",
        "email": "alice@customer.test",
        "password": "NewStrongPassword#2026",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client, seeded_customer):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@customer.test", "password": "AliceSecure#2026"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "alice@customer.test"


def test_login_wrong_password(client, seeded_customer):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@customer.test", "password": "WrongPassword#2026"},
    )
    assert response.status_code == 401


def test_get_current_user_me(client, seeded_customer):
    response = client.get("/api/v1/auth/me", headers=seeded_customer["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "alice@customer.test"
    assert data["role"] == "customer"
    assert data["customer_profile"]["company_name"] == "Acme Corp"


def test_get_current_user_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_update_current_user_profile(client, seeded_customer):
    response = client.put(
        "/api/v1/auth/me",
        headers=seeded_customer["headers"],
        json={"company_name": "Updated Acme Global", "phone": "+999888777"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["customer_profile"]["company_name"] == "Updated Acme Global"
    assert data["customer_profile"]["phone"] == "+999888777"


def test_admin_create_staff_success(client, seeded_admin):
    payload = {
        "full_name": "New Staff Member",
        "email": "new.staff@brightloop.test",
        "password": "StaffSecret#2026",
    }
    response = client.post("/api/v1/staff", headers=seeded_admin["headers"], json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new.staff@brightloop.test"
    assert data["role"] == "staff"


def test_customer_cannot_create_staff(client, seeded_customer):
    payload = {
        "full_name": "Rogue Staff",
        "email": "rogue.staff@brightloop.test",
        "password": "RogueSecret#2026",
    }
    response = client.post("/api/v1/staff", headers=seeded_customer["headers"], json=payload)
    assert response.status_code == 403


def test_user_listing_permissions(client, seeded_admin, seeded_staff, seeded_customer):
    # Admin can list
    admin_res = client.get("/api/v1/users", headers=seeded_admin["headers"])
    assert admin_res.status_code == 200
    assert len(admin_res.json()) >= 3

    # Staff can list
    staff_res = client.get("/api/v1/users", headers=seeded_staff["headers"])
    assert staff_res.status_code == 200

    # Customer cannot list
    cust_res = client.get("/api/v1/users", headers=seeded_customer["headers"])
    assert cust_res.status_code == 403


def test_admin_cannot_deactivate_self(client, seeded_admin):
    admin_id = str(seeded_admin["user"].id)
    response = client.patch(
        f"/api/v1/users/{admin_id}/status",
        headers=seeded_admin["headers"],
        json={"is_active": False},
    )
    assert response.status_code == 400
    assert "cannot deactivate their own account" in response.json()["detail"]


def test_password_reset_lifecycle(client, seeded_customer):
    # 1. Request reset token
    forgot_res = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "alice@customer.test"},
    )
    assert forgot_res.status_code == 200
    raw_token = forgot_res.json().get("reset_token_preview")
    assert raw_token is not None

    # 2. Reset password
    new_password = "BrandNewPassword#2026"
    reset_res = client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "new_password": new_password},
    )
    assert reset_res.status_code == 200

    # 3. Old password should fail
    fail_login = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@customer.test", "password": "AliceSecure#2026"},
    )
    assert fail_login.status_code == 401

    # 4. New password should succeed
    succ_login = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@customer.test", "password": new_password},
    )
    assert succ_login.status_code == 200

    # 5. Token reuse should fail
    reuse_res = client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "new_password": "AnotherPassword#2026"},
    )
    assert reuse_res.status_code == 400
