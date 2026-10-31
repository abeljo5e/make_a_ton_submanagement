import uuid
from decimal import Decimal


def test_api_product_and_variant_crud(client):
    # 1. Test validation error on negative price
    bad_res = client.post("/api/v1/products", json={"name": "Bad", "sales_price": "-10.00"})
    assert bad_res.status_code == 422

    # 2. Test validation error on empty name
    bad_res_name = client.post("/api/v1/products", json={"name": "   ", "sales_price": "10.00"})
    assert bad_res_name.status_code == 422

    # 3. Create valid product
    create_res = client.post(
        "/api/v1/products",
        json={
            "name": "Business Suite",
            "type": "software",
            "sales_price": "2000.00",
            "cost_price": "800.00",
            "currency": "INR",
            "variants": [{"name": "Standard License", "additional_price": "0.00"}],
        },
    )
    assert create_res.status_code == 201
    prod = create_res.json()
    assert prod["status"] == "active"
    assert prod["sales_price"] == "2000.00"
    prod_id = prod["id"]
    variant_id = prod["variants"][0]["id"]

    # 4. Read product
    get_res = client.get(f"/api/v1/products/{prod_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Business Suite"

    # 5. Patch product
    patch_res = client.patch(f"/api/v1/products/{prod_id}", json={"sales_price": "2100.00"})
    assert patch_res.status_code == 200
    assert patch_res.json()["sales_price"] == "2100.00"

    # 6. Add Variant
    add_var_res = client.post(
        f"/api/v1/products/{prod_id}/variants",
        json={"name": "Enterprise License", "additional_price": "500.00"},
    )
    assert add_var_res.status_code == 201
    new_var_id = add_var_res.json()["id"]

    # 7. Update variant via standalone endpoint
    update_var_res = client.patch(f"/api/v1/variants/{new_var_id}", json={"additional_price": "550.00"})
    assert update_var_res.status_code == 200
    assert update_var_res.json()["additional_price"] == "550.00"

    # 8. Deactivate product
    deact_res = client.post(f"/api/v1/products/{prod_id}/deactivate")
    assert deact_res.status_code == 200
    assert deact_res.json()["status"] == "inactive"


def test_api_plan_crud_and_catalogue(client):
    # Create product for bundling
    prod_res = client.post(
        "/api/v1/products",
        json={"name": "Hosting Service", "sales_price": "500.00"},
    )
    prod_id = prod_res.json()["id"]

    # 1. Reject invalid billing frequency
    bad_freq_res = client.post(
        "/api/v1/plans",
        json={"name": "Bad Plan", "price": "100.00", "billing_frequency": "hourly"},
    )
    assert bad_freq_res.status_code == 422

    # 2. Reject non-existent product in bundle
    bad_bundle_res = client.post(
        "/api/v1/plans",
        json={
            "name": "Bad Bundle",
            "price": "100.00",
            "products": [{"product_id": str(uuid.uuid4()), "quantity": 1}],
        },
    )
    assert bad_bundle_res.status_code == 422

    # 3. Create valid subscription plan
    plan_res = client.post(
        "/api/v1/plans",
        json={
            "name": "Startup Monthly",
            "price": "600.00",
            "billing_frequency": "monthly",
            "products": [{"product_id": prod_id, "quantity": 1}],
        },
    )
    assert plan_res.status_code == 201
    plan = plan_res.json()
    plan_id = plan["id"]
    assert plan["price"] == "600.00"
    assert len(plan["products"]) == 1

    # 4. List plans (customer catalogue query)
    cat_res = client.get("/api/v1/plans?available_only=true&is_active=true")
    assert cat_res.status_code == 200
    assert any(p["id"] == plan_id for p in cat_res.json())

    # 5. Add products to plan
    bundle_res = client.post(
        f"/api/v1/plans/{plan_id}/products",
        json=[{"product_id": prod_id, "quantity": 3}],
    )
    assert bundle_res.status_code == 200
    assert bundle_res.json()["products"][0]["quantity"] == 3

    # 6. Deactivate plan
    deact_plan_res = client.post(f"/api/v1/plans/{plan_id}/deactivate")
    assert deact_plan_res.status_code == 200
    assert deact_plan_res.json()["is_active"] is False

    # 7. 404 test on missing plan
    res_404 = client.get(f"/api/v1/plans/{uuid.uuid4()}")
    assert res_404.status_code == 404
