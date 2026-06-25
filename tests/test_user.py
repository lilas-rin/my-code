from app import models, oauth2, utils


def test_create_user(client, user_data):
    new_user = user_data["new_user"]
    response = client.post(
        "/users/",
        json=new_user,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == new_user["email"]
    assert "id" in data
    assert "password" not in data


def test_get_users(client, test_user):
    response = client.get("/users/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": test_user.id,
            "email": test_user.email,
        }
    ]


def test_get_user_by_id(client, test_user):
    response = client.get(f"/users/{test_user.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": test_user.id,
        "email": test_user.email,
    }


def test_get_user_by_id_not_found(client):
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User with id 999 was not found"


def test_login_user(client, test_user, user_data):
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": user_data["existing_user"]["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert oauth2.verify_access_token(data["access_token"]) == str(test_user.id)


def test_login_user_with_wrong_password(client, test_user, user_data):
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": user_data["wrong_password"],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid credentials"


def test_delete_user(client, test_user, db_session):
    user_id = test_user.id

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == 204
    assert db_session.get(models.User, user_id) is None


def test_delete_user_not_found(client):
    response = client.delete("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User with id 999 was not found"


def test_update_password(client, test_user, db_session, user_data):
    password_update = user_data["password_update"]
    response = client.put(
        f"/users/{test_user.id}/password",
        json={
            "old_password": user_data["existing_user"]["password"],
            "new_password": password_update["new_password"],
            "confirm_password": password_update["new_password"],
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Password updated successfully"}

    db_session.refresh(test_user)
    assert utils.verify(password_update["new_password"], test_user.password)


def test_update_password_with_wrong_old_password(client, test_user, user_data):
    password_update = user_data["password_update"]
    response = client.put(
        f"/users/{test_user.id}/password",
        json={
            "old_password": user_data["wrong_password"],
            "new_password": password_update["new_password"],
            "confirm_password": password_update["new_password"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Old password is incorrect"


def test_update_password_with_mismatched_confirmation(client, test_user, user_data):
    password_update = user_data["password_update"]
    response = client.put(
        f"/users/{test_user.id}/password",
        json={
            "old_password": user_data["existing_user"]["password"],
            "new_password": password_update["new_password"],
            "confirm_password": password_update["mismatched_confirm_password"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The two new passwords do not match"
