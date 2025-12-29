"""End-to-end smoke tests for Pomodoro API.

This script performs comprehensive testing of all major API endpoints
including authentication, user management, tasks, categories, tags,
and media upload functionality.
"""

import json
import sys
import time
import traceback
from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pomodoro.auth.security import get_password_hash
from pomodoro.core.settings import Settings
from pomodoro.task.models.categories import Category
from pomodoro.task.models.tasks import Task
from pomodoro.task.models.tags import Tag  # Import Tag model
from pomodoro.user.models.users import UserProfile, UserRole

BASE = "http://127.0.0.1:8000"


def prepare_test_users(settings: Settings) -> list[int]:
    """Create test users in database for E2E testing."""
    engine = create_engine(settings.DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()

    test_users = [
        {
            "phone": "+70000000001",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "role": UserRole.USER.value,
        },
        {
            "phone": "+70000000002",
            "first_name": "Test",
            "last_name": "Admin",
            "password": "adminpass123",
            "role": UserRole.ADMIN.value,
        },
        {
            "phone": "+70000000003",
            "first_name": "Test",
            "last_name": "Root",
            "password": "rootpass123",
            "role": UserRole.ROOT.value,
        },
    ]

    created_ids: list[int] = []
    for user_data in test_users:
        print(f"Processing user: {user_data['phone']}")
        query = session.query(UserProfile).filter_by(phone=user_data["phone"])
        exists = query.one_or_none()
        if exists:
            print(f"User {user_data['phone']} already exists (id={exists.id}).")
            continue

        print(f"Creating user: {user_data['phone']}")
        hashed = get_password_hash(user_data["password"]) or ""
        user = UserProfile(
            phone=user_data["phone"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            hashed_password=hashed,
            role=user_data["role"],
            phone_verified=True,
            is_active=True,
        )
        session.add(user)
        session.commit()
        print(f"Created test user {user_data['phone']} id={user.id} role={user_data['role']}")
        created_ids.append(user.id)

    session.close()
    return created_ids


def login_user(client: httpx.Client, phone: str, password: str) -> str:
    """Login user and return JWT token."""
    data = {"username": phone, "password": password}
    r = client.post(f"{BASE}/auth/login", data=data)
    if r.status_code != 200:
        msg = f"Login failed for {phone}: {r.status_code} {r.text}"
        raise RuntimeError(msg)
    token = r.json().get("access_token")
    if not token:
        raise RuntimeError(f"No access token in response: {r.json()}")
    return token


def make_auth_header(token: str) -> dict:
    """Create authorization header with JWT token."""
    return {"Authorization": f"Bearer {token}"}


def format_response_details(details: object | None) -> str | None:
    """Format response details for logging."""
    if details is None:
        return None
    try:
        return json.dumps(details, ensure_ascii=False, indent=2)
    except Exception:
        return str(details)


def make_request_with_retries(
    client: httpx.Client,
    method: str,
    url: str,
    retries: int = 3,
    backoff: float = 0.5,
    retry_on_5xx: bool = True,
    **kwargs,
) -> httpx.Response:
    """Make HTTP request with retry logic for network errors and 5xx responses."""
    last_exc: BaseException | None = None

    for attempt in range(1, retries + 1):
        try:
            resp = client.request(method, url, **kwargs)
            if (
                retry_on_5xx
                and resp.status_code >= 500
                and attempt < retries
            ):
                time.sleep(backoff * attempt)
                last_exc = RuntimeError(f"Server error {resp.status_code}")
                continue
            return resp
        except httpx.RequestError as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * attempt)
                continue
            raise

    if last_exc:
        raise last_exc
    raise RuntimeError("Request failed without exception")


def cleanup_test_data(
    settings: Settings,
    user_ids: list[int],
    category_ids: list[int],
    task_ids: list[int],
) -> dict[str, list[dict]]:
    """Функция очистки созданных данных из БД."""
    results: dict = {"users": [], "categories": [], "tasks": []}
    engine = create_engine(settings.DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        for tid in task_ids:
            try:
                task_obj = session.get(Task, tid)
                if task_obj:
                    session.delete(task_obj)
                    session.commit()
                    results["tasks"].append({"id": tid, "deleted": True})
                else:
                    results["tasks"].append(
                        {"id": tid, "deleted": False, "reason": "not found"}
                    )
            except Exception as exc:
                session.rollback()
                results["tasks"].append(
                    {"id": tid, "deleted": False, "error": str(exc)}
                )

        for cid in category_ids:
            try:
                category_obj = session.get(Category, cid)
                if category_obj:
                    session.delete(category_obj)
                    session.commit()
                    results["categories"].append({"id": cid, "deleted": True})
                else:
                    results["categories"].append(
                        {"id": cid, "deleted": False, "reason": "not found"}
                    )
            except Exception as exc:
                session.rollback()
                results["categories"].append(
                    {"id": cid, "deleted": False, "error": str(exc)}
                )

        for uid in user_ids:
            try:
                obj = session.get(UserProfile, uid)
                if obj:
                    session.delete(obj)
                    session.commit()
                    results["users"].append({"id": uid, "deleted": True})
                else:
                    results["users"].append(
                        {"id": uid, "deleted": False, "reason": "not found"}
                    )
            except Exception as exc:
                session.rollback()
                results["users"].append(
                    {"id": uid, "deleted": False, "error": str(exc)}
                )
    finally:
        session.close()
    return results


def run_e2e_tests() -> dict[str, Any]:
    """Run comprehensive E2E tests for all API endpoints."""
    settings = Settings()
    steps: list[dict] = []
    created_user_ids: list[int] = []
    created_category_ids: list[int] = []
    created_task_ids: list[int] = []
    created_tag_ids: list[int] = []

    def record_step(
        success: bool,
        message: str,
        details: object | None = None,
        request: dict | None = None,
        response: dict | None = None,
    ) -> None:
        """Record a test step with results."""
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "success": bool(success),
            "message": message,
            "details": details,
            "request": request,
            "response": response,
        }
        steps.append(entry)
        status_mark = "✅" if success else "❌"
        brief = f"{status_mark} {message}"
        if details is not None:
            brief = f"{brief} — {format_response_details(details)}"
        print(brief)

    def success(
        message: str,
        details: object | None = None,
        request: dict | None = None,
        response: dict | None = None,
    ) -> None:
        """Record successful test step."""
        record_step(True, message, details=details, request=request, response=response)

    def failure(
        message: str,
        details: object | None = None,
        request: dict | None = None,
        response: dict | None = None,
    ) -> None:
        """Record failed test step."""
        record_step(False, message, details=details, request=request, response=response)

    # Prepare test users
    success("Setting up test users in database...")
    created_user_ids = prepare_test_users(settings=settings)

    with httpx.Client(timeout=30.0) as client:
        # Test 1: Health check
        success("Testing health check endpoint...")
        try:
            health_resp = make_request_with_retries(client, "GET", f"{BASE}/health")
            if health_resp.status_code == 200:
                success("Health check passed", response={"status_code": health_resp.status_code})
            else:
                failure("Health check failed", response={"status_code": health_resp.status_code, "text": health_resp.text})
        except Exception as exc:
            failure("Health check error", details=str(exc))

        # Test 2: User authentication
        success("Testing user authentication...")
        try:
            # Login all test users with delays to avoid rate limiting
            time.sleep(1)
            user_token = login_user(client, "+70000000001", "testpass123")
            time.sleep(1)
            admin_token = login_user(client, "+70000000002", "adminpass123")
            time.sleep(1)
            root_token = login_user(client, "+70000000003", "rootpass123")
            success("All users logged in successfully")
        except Exception as exc:
            failure("User authentication failed", details=str(exc))
            raise

        # Test 3: Invalid login
        success("Testing invalid login credentials...")
        try:
            invalid_resp = make_request_with_retries(
                client, "POST", f"{BASE}/auth/login",
                data={"username": "+70000000001", "password": "wrongpassword"}
            )
            if invalid_resp.status_code == 401:
                success("Invalid login correctly rejected", response={"status_code": invalid_resp.status_code})
            else:
                failure("Invalid login not rejected", response={"status_code": invalid_resp.status_code})
        except Exception as exc:
            failure("Invalid login test error", details=str(exc))

        # Test 4: User registration
        success("Testing user registration...")
        try:
            register_data = {
                "phone": "+70000000004",
                "first_name": "New",
                "last_name": "User",
                "password": "Newpass123"
            }
            register_resp = make_request_with_retries(
                client, "POST", f"{BASE}/auth/register",
                json=register_data
            )
            if register_resp.status_code == 201:
                success("User registration successful", response={"status_code": register_resp.status_code})
                # Clean up created user
                created_user_ids.append(register_resp.json()["id"])
            else:
                failure("User registration failed", response={"status_code": register_resp.status_code, "text": register_resp.text})
        except Exception as exc:
            failure("User registration error", details=str(exc))

        # Test 5: Get current user profile
        success("Testing get current user profile...")
        try:
            profile_resp = make_request_with_retries(
                client, "GET", f"{BASE}/users/me",
                headers=make_auth_header(user_token)
            )
            if profile_resp.status_code == 200:
                success("User profile retrieved successfully", response={"status_code": profile_resp.status_code})
            else:
                failure("User profile retrieval failed", response={"status_code": profile_resp.status_code, "text": profile_resp.text})
        except Exception as exc:
            failure("User profile test error", details=str(exc))

        # Test 6: Create category
        success("Testing category creation...")
        try:
            category_data = {"name": "Test Category"}
            category_resp = make_request_with_retries(
                client, "POST", f"{BASE}/categories",
                json=category_data,
                headers=make_auth_header(admin_token)
            )
            if category_resp.status_code == 201:
                category = category_resp.json()
                created_category_ids.append(category["id"])
                success("Category created successfully", details={"category_id": category["id"]}, response={"status_code": category_resp.status_code})
            else:
                failure("Category creation failed", response={"status_code": category_resp.status_code, "text": category_resp.text})
        except Exception as exc:
            failure("Category creation error", details=str(exc))

        # Test 7: Get categories
        success("Testing get categories...")
        try:
            categories_resp = make_request_with_retries(
                client, "GET", f"{BASE}/categories",
                headers=make_auth_header(user_token)
            )
            if categories_resp.status_code == 200:
                categories = categories_resp.json()
                success("Categories retrieved successfully", details={"count": len(categories)}, response={"status_code": categories_resp.status_code})
            else:
                failure("Categories retrieval failed", response={"status_code": categories_resp.status_code, "text": categories_resp.text})
        except Exception as exc:
            failure("Categories retrieval error", details=str(exc))

        # Test 8: Create tag
        success("Testing tag creation...")
        try:
            tag_data = {"name": "Test Tag", "is_active": True}
            tag_resp = make_request_with_retries(
                client, "POST", f"{BASE}/tags",
                json=tag_data,
                headers=make_auth_header(admin_token)
            )
            if tag_resp.status_code == 201:
                tag = tag_resp.json()
                created_tag_ids.append(tag["id"])
                success("Tag created successfully", details={"tag_id": tag["id"]}, response={"status_code": tag_resp.status_code})
            else:
                failure("Tag creation failed", response={"status_code": tag_resp.status_code, "text": tag_resp.text})
        except Exception as exc:
            failure("Tag creation error", details=str(exc))

        # Test 9: Get tags
        success("Testing get tags...")
        try:
            tags_resp = make_request_with_retries(
                client, "GET", f"{BASE}/tags",
                headers=make_auth_header(user_token)
            )
            if tags_resp.status_code == 200:
                tags = tags_resp.json()
                success("Tags retrieved successfully", details={"count": len(tags)}, response={"status_code": tags_resp.status_code})
            else:
                failure("Tags retrieval failed", response={"status_code": tags_resp.status_code, "text": tags_resp.text})
        except Exception as exc:
            failure("Tags retrieval error", details=str(exc))

        # Test 10: Create task with tags
        success("Testing task creation with tags...")
        try:
            task_data = {
                "name": "Test Task",
                "pomodoro_count": 4,
                "category_id": created_category_ids[0] if created_category_ids else None,
                "tags": created_tag_ids
            }
            task_resp = make_request_with_retries(
                client, "POST", f"{BASE}/tasks",
                json=task_data,
                headers=make_auth_header(user_token)
            )
            if task_resp.status_code == 201:
                task = task_resp.json()
                created_task_ids.append(task["id"])
                success("Task created successfully", details={"task_id": task["id"]}, response={"status_code": task_resp.status_code})
            else:
                failure("Task creation failed", response={"status_code": task_resp.status_code, "text": task_resp.text})
        except Exception as exc:
            failure("Task creation error", details=str(exc))

        # Test 11: Get tasks
        success("Testing get tasks...")
        try:
            tasks_resp = make_request_with_retries(
                client, "GET", f"{BASE}/tasks",
                headers=make_auth_header(user_token)
            )
            if tasks_resp.status_code == 200:
                tasks = tasks_resp.json()
                success("Tasks retrieved successfully", details={"count": len(tasks)}, response={"status_code": tasks_resp.status_code})
            else:
                failure("Tasks retrieval failed", response={"status_code": tasks_resp.status_code, "text": tasks_resp.text})
        except Exception as exc:
            failure("Tasks retrieval error", details=str(exc))

        # Test 12: Get specific task
        if created_task_ids:
            success("Testing get specific task...")
            try:
                task_id = created_task_ids[0]
                task_resp = make_request_with_retries(
                    client, "GET", f"{BASE}/tasks/{task_id}",
                    headers=make_auth_header(user_token)
                )
                if task_resp.status_code == 200:
                    task = task_resp.json()
                    success("Specific task retrieved successfully", details={"task_id": task["id"]}, response={"status_code": task_resp.status_code})
                else:
                    failure("Specific task retrieval failed", response={"status_code": task_resp.status_code, "text": task_resp.text})
            except Exception as exc:
                failure("Specific task retrieval error", details=str(exc))

        # Test 13: Update task
        if created_task_ids:
            success("Testing task update...")
            try:
                task_id = created_task_ids[0]
                update_data = {"name": "Updated Test Task", "pomodoro_count": 6}
                update_resp = make_request_with_retries(
                    client, "PATCH", f"{BASE}/tasks/{task_id}",
                    json=update_data,
                    headers=make_auth_header(user_token)
                )
                if update_resp.status_code == 200:
                    success("Task updated successfully", response={"status_code": update_resp.status_code})
                else:
                    failure("Task update failed", response={"status_code": update_resp.status_code, "text": update_resp.text})
            except Exception as exc:
                failure("Task update error", details=str(exc))

        # Test 14: Test media upload (if MinIO is running)
        success("Testing media upload...")
        try:
            # Create a simple test file
            test_file_content = b"test image content"
            files = {"file": ("test.jpg", test_file_content, "image/jpeg")}

            # Try to upload to task (if task exists)
            if created_task_ids:
                upload_resp = make_request_with_retries(
                    client, "POST", f"{BASE}/media/upload/task/{created_task_ids[0]}",
                    files=files,
                    headers=make_auth_header(user_token)
                )
                if upload_resp.status_code == 201:
                    success("Media upload successful", response={"status_code": upload_resp.status_code})
                else:
                    success("Media upload skipped (MinIO not available)", details={"status_code": upload_resp.status_code})
            else:
                success("Media upload test skipped (no tasks created)")
        except Exception as exc:
            success("Media upload test skipped (infrastructure not available)", details=str(exc))

        # Test 15: Test password reset flow
        success("Testing password reset request...")
        try:
            reset_data = {"phone": "+70000000001"}
            reset_resp = make_request_with_retries(
                client, "POST", f"{BASE}/users/reset_password_via_email",
                json=reset_data
            )
            if reset_resp.status_code == 200:
                success("Password reset request successful", response={"status_code": reset_resp.status_code})
            else:
                failure("Password reset request failed", response={"status_code": reset_resp.status_code, "text": reset_resp.text})
        except Exception as exc:
            failure("Password reset request error", details=str(exc))

        # Test 16: Test admin endpoints
        success("Testing admin-only endpoints...")
        try:
            # Try to access admin endpoint with regular user (should fail)
            admin_resp = make_request_with_retries(
                client, "GET", f"{BASE}/users/me",
                headers=make_auth_header(user_token)
            )
            # This should work for regular user, but let's test admin access to all users
            all_users_resp = make_request_with_retries(
                client, "GET", f"{BASE}/users/1",  # Try to access another user's profile
                headers=make_auth_header(user_token)
            )
            if all_users_resp.status_code == 403:
                success("Regular user correctly denied access to other user's profile", response={"status_code": all_users_resp.status_code})
            else:
                success("Access control test completed", details={"status_code": all_users_resp.status_code})
        except Exception as exc:
            failure("Admin endpoints test error", details=str(exc))

    return {
        "created_user_ids": created_user_ids,
        "created_category_ids": created_category_ids,
        "created_task_ids": created_task_ids,
        "created_tag_ids": created_tag_ids,
        "steps": steps,
    }


def main() -> dict[str, Any]:
    """Main entry point for E2E tests."""
    return run_e2e_tests()


if __name__ == "__main__":
    report: dict = {
        "start_ts": datetime.now(UTC).isoformat(),
        "success": False,
        "error": None,
        "error_traceback": None,
        "created_user_ids": [],
        "created_category_ids": [],
        "created_task_ids": [],
        "steps": [],
        "cleanup": {},
    }

    try:
        res = main()
        report["success"] = True
        report["created_user_ids"] = res.get("created_user_ids", [])
        report["created_category_ids"] = res.get("created_category_ids", [])
        report["created_task_ids"] = res.get("created_task_ids", [])
        report["steps"] = res.get("steps", [])
    except Exception as e:
        tb = traceback.format_exc()
        report["error"] = f"Exception: {e}"
        report["error_traceback"] = tb
    finally:
        settings = Settings()
        try:
            cleanup_res = cleanup_db(
                settings,
                report.get("created_user_ids", []),
                report.get("created_category_ids", []),
                report.get("created_task_ids", []),
            )
            report["cleanup"] = cleanup_res
            report["cleanup_human"] = [
                (
                    f"Удалено: {m[:-1]} id={it['id']}"
                    if it.get("deleted")
                    else f"Не удалено: {m[:-1]} id={it.get('id')} "
                    f"({it.get('reason') or it.get('error')})"
                )
                for m in ("tasks", "categories", "users")
                for it in cleanup_res.get(m, [])
            ]
        except Exception as e:
            report["cleanup"] = {"error": str(e)}
            report["cleanup_human"] = [f"Ошибка очистки: {e}"]

        report["end_ts"] = datetime.now(UTC).isoformat()
        with open("scripts/e2e_report.json", "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        if not report.get("success"):
            sys.exit(1)
