#!/usr/bin/env python3
"""Clean E2E script (spaces only).

Run this directly: python3 scripts/e2e.py
"""
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional
import time

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import Settings
from app.auth.security import get_password_hash
from app.user.models.users import UserProfile, UserRole
from app.task.models.tasks import Task
from app.task.models.categories import Category


BASE = "http://127.0.0.1:8000"


def prepare_users(settings: Settings) -> List[int]:
    engine = create_engine(settings.DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()

    users = [
        {
            "phone": "+70000000001",
            "first_name": "Normal",
            "last_name": "User",
            "password": "password1",
            "role": UserRole.USER.value,
        },
        {
            "phone": "+70000000002",
            "first_name": "Admin",
            "last_name": "User",
            "password": "password2",
            "role": UserRole.ADMIN.value,
        },
        {
            "phone": "+70000000003",
            "first_name": "Root",
            "last_name": "User",
            "password": "password3",
            "role": UserRole.ROOT.value,
        },
    ]

    created_ids: List[int] = []
    for u in users:
        query = session.query(UserProfile).filter_by(phone=u["phone"])
        exists = query.one_or_none()
        if exists:
            print(f"User {u['phone']} already exists (id={exists.id}).")
            continue
        hashed = get_password_hash(u["password"]) or ""
        user = UserProfile(
            phone=u["phone"],
            first_name=u["first_name"],
            last_name=u["last_name"],
            hashed_password=hashed,
            role=u["role"],
            phone_verified=True,
            is_active=True,
        )
        session.add(user)
        session.commit()
        print(f"Created user {u['phone']} id={user.id} role={u['role']}")
        created_ids.append(user.id)

    session.close()
    return created_ids


def login(client: httpx.Client, phone: str, password: str) -> str:
    data = {"username": phone, "password": password}
    r = client.post(f"{BASE}/users/login", data=data)
    if r.status_code != 200:
        msg = f"Login failed for {phone}: {r.status_code} {r.text}"
        raise RuntimeError(msg)
    token = r.json().get("access_token")
    return token


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _format_details(details: Optional[object]) -> Optional[str]:
    if details is None:
        return None
    try:
        return json.dumps(details, ensure_ascii=False)
    except Exception:
        return str(details)


def request_with_retries(
    client: httpx.Client,
    method: str,
    url: str,
    retries: int = 3,
    backoff: float = 0.5,
    retry_on_status: bool = True,
    **kwargs,
) -> httpx.Response:
    """Выполняет запрос с простыми правилами повторов при сетевых ошибках.

    Повторяет при httpx.RequestError и (опционально) при статусах >=500.
    Возвращает последний ответ или перебрасывает последнее исключение.
    """
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.request(method, url, **kwargs)
            if (
                retry_on_status
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


def cleanup_db(
    settings: Settings,
    user_ids: List[int],
    category_ids: List[int],
    task_ids: List[int],
) -> Dict[str, List[Dict]]:
    results = {"users": [], "categories": [], "tasks": []}
    engine = create_engine(settings.DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        for tid in task_ids:
            try:
                obj = session.get(Task, tid)
                if obj:
                    session.delete(obj)
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
                obj = session.get(Category, cid)
                if obj:
                    session.delete(obj)
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


def main() -> Dict[str, List[int]]:
    settings = Settings()
    steps: List[Dict] = []

    def record_step(
        ok_flag: bool,
        msg: str,
        details: Optional[object] = None,
        request: Optional[Dict] = None,
        response: Optional[Dict] = None,
    ) -> None:
        entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "ok": bool(ok_flag),
            "message": msg,
            "details": details,
            "request": request,
            "response": response,
        }
        steps.append(entry)
        mark = "✓" if ok_flag else "✗"
        brief = f"{mark} {msg}"
        if details is not None:
            brief = f"{brief} — {_format_details(details)}"
        print(brief)

    def ok(
        msg: str,
        details: Optional[object] = None,
        request: Optional[Dict] = None,
        response: Optional[Dict] = None,
    ) -> None:
        record_step(
            True, msg, details=details, request=request, response=response
        )

    def fail(
        msg: str,
        details: Optional[object] = None,
        request: Optional[Dict] = None,
        response: Optional[Dict] = None,
    ) -> None:
        record_step(
            False, msg, details=details, request=request, response=response
        )

    ok("Подготовка пользователей в БД...")
    created_user_ids = prepare_users(settings=settings)
    created_category_ids: List[int] = []
    created_task_ids: List[int] = []

    with httpx.Client(timeout=10.0) as client:
        # Логиним трёх тестовых пользователей
        try:
            normal_token = login(client, "+70000000001", "password1")
            admin_token = login(client, "+70000000002", "password2")
            root_token = login(client, "+70000000003", "password3")
            ok("Успешный вход всех трёх пользователей")
        except Exception as exc:
            fail("Не удалось выполнить вход пользователей", details=str(exc))
            raise

        # Негативный кейс: неверный логин
        bad_data = {"username": "+70000000001", "password": "wrong"}
        try:
            r_bad = request_with_retries(
                client, "POST", f"{BASE}/users/login", data=bad_data
            )
            if r_bad.status_code != 200:
                ok(
                    "Вход с неверными учётными данными отклонён (ожидаемо)",
                    details={"status_code": r_bad.status_code},
                    request={"url": f"{BASE}/users/login", "data": bad_data},
                    response={
                        "status_code": r_bad.status_code,
                        "text": r_bad.text,
                    },
                )
            else:
                fail(
                    "Вход с неверными учётными данными прошёл (неожиданно)",
                    request={"url": f"{BASE}/users/login", "data": bad_data},
                    response={
                        "status_code": r_bad.status_code,
                        "text": r_bad.text,
                    },
                )
        except Exception as exc:
            fail(
                "Ошибка при проверке неверного входа",
                details=str(exc),
                request={"url": f"{BASE}/users/login", "data": bad_data},
            )

        # Создаём категории root/admin через API, чтобы далее тестировать дубли и переименования
        try:
            r = request_with_retries(
                client,
                "POST",
                f"{BASE}/categories/",
                json={"name": "root-cat", "is_active": True},
                headers=auth_header(root_token),
            )
            if r.status_code == 201:
                root_cat = r.json()
                created_category_ids.append(root_cat.get("id"))
                ok(
                    "Root создал категорию",
                    details={"id": root_cat.get("id")},
                    request={
                        "url": f"{BASE}/categories/",
                        "json": {"name": "root-cat"},
                    },
                    response={"status_code": r.status_code},
                )
            else:
                fail(
                    "Root не смог создать категорию",
                    details={"status_code": r.status_code, "text": r.text},
                    request={
                        "url": f"{BASE}/categories/",
                        "json": {"name": "root-cat"},
                    },
                    response={"status_code": r.status_code, "text": r.text},
                )
        except Exception as exc:
            fail("Ошибка при создании root-категории", details=str(exc))
            raise

        try:
            r = request_with_retries(
                client,
                "POST",
                f"{BASE}/categories/",
                json={"name": "admin-cat", "is_active": True},
                headers=auth_header(admin_token),
            )
            if r.status_code == 201:
                admin_cat = r.json()
                created_category_ids.append(admin_cat.get("id"))
                ok(
                    "Admin создал категорию",
                    details={"id": admin_cat.get("id")},
                )
            else:
                fail(
                    "Admin не смог создать категорию",
                    details={"status_code": r.status_code, "text": r.text},
                )
        except Exception as exc:
            fail("Ошибка при создании admin-категории", details=str(exc))

        # Попытка создать категорию с дублирующимся именем (ожидаем отклонение)
        dup_payload = {"name": "root-cat", "is_active": True}
        try:
            r_dup = request_with_retries(
                client,
                "POST",
                f"{BASE}/categories/",
                json=dup_payload,
                headers=auth_header(root_token),
            )
            if r_dup.status_code >= 400:
                ok(
                    "Создание категории с уже существующим именем отклонено (ожидаемо)",
                    request={
                        "url": f"{BASE}/categories/",
                        "json": dup_payload,
                    },
                    response={
                        "status_code": r_dup.status_code,
                        "text": r_dup.text,
                    },
                )
            else:
                cat = r_dup.json()
                if isinstance(cat, dict) and cat.get("id"):
                    created_category_ids.append(cat["id"])
                    fail(
                        "Сервер разрешил дублирование категории (неожиданно)",
                        request={
                            "url": f"{BASE}/categories/",
                            "json": dup_payload,
                        },
                        response={"id": cat["id"]},
                    )
        except Exception as exc:
            fail(
                "Ошибка при запросе создания дублирующейся категории",
                details=str(exc),
                request={"url": f"{BASE}/categories/", "json": dup_payload},
            )

        # Попытка переименовать admin_cat в имя root-cat (должно провалиться)
        try:
            rename_payload = {"name": "root-cat"}
            r_rename = request_with_retries(
                client,
                "PATCH",
                f"{BASE}/categories/?category_id={admin_cat['id']}",
                json=rename_payload,
                headers=auth_header(admin_token),
            )
            if r_rename.status_code >= 400:
                ok(
                    "Переименование категории на уже существующее имя отклонено (ожидаемо)",
                    request={
                        "url": f"{BASE}/categories/?category_id={admin_cat['id']}",
                        "json": rename_payload,
                    },
                    response={
                        "status_code": r_rename.status_code,
                        "text": r_rename.text,
                    },
                )
            else:
                fail(
                    "Переименование категории на дублирующее имя прошло (неожиданно)",
                    request={
                        "url": f"{BASE}/categories/?category_id={admin_cat['id']}",
                        "json": rename_payload,
                    },
                    response={
                        "status_code": r_rename.status_code,
                        "text": r_rename.text,
                    },
                )
        except Exception as exc:
            fail(
                "Ошибка при попытке переименования категории",
                details=str(exc),
                request={
                    "url": f"{BASE}/categories/?category_id={admin_cat['id']}",
                    "json": rename_payload,
                },
            )

        # Создадим по задаче от каждого пользователя
        tasks: Dict[str, Dict] = {}
        for token, phone in (
            (normal_token, "+70000000001"),
            (admin_token, "+70000000002"),
            (root_token, "+70000000003"),
        ):
            try:
                payload = {
                    "name": f"task-{phone}",
                    "pomodoro_count": 1,
                    "category_id": root_cat["id"],
                    "is_active": True,
                }
                r = request_with_retries(
                    client,
                    "POST",
                    f"{BASE}/tasks/",
                    json=payload,
                    headers=auth_header(token),
                )
                if r.status_code != 201:
                    fail(
                        "Не удалось создать задачу",
                        details={
                            "phone": phone,
                            "status_code": r.status_code,
                            "text": r.text,
                        },
                        request={"url": f"{BASE}/tasks/", "json": payload},
                    )
                    raise AssertionError("Create task failed")
                tasks[phone] = r.json()
                created_task_ids.append(tasks[phone]["id"])
                ok(
                    "Создана задача",
                    details={"phone": phone, "id": tasks[phone]["id"]},
                )
            except Exception as exc:
                fail(
                    "Ошибка при создании задачи",
                    details=str(exc),
                    request={"url": f"{BASE}/tasks/", "json": payload},
                )

        # Попытка создать задачу с дублирующимся именем
        try:
            dup_task_payload = {
                "name": tasks["+70000000001"]["name"],
                "pomodoro_count": 1,
                "category_id": root_cat["id"],
                "is_active": True,
            }
            r_dup_task = request_with_retries(
                client,
                "POST",
                f"{BASE}/tasks/",
                json=dup_task_payload,
                headers=auth_header(normal_token),
            )
            if r_dup_task.status_code >= 400:
                ok(
                    "Создание задачи с дублирующимся именем отклонено (ожидаемо)",
                    request={
                        "url": f"{BASE}/tasks/",
                        "json": dup_task_payload,
                    },
                    response={
                        "status_code": r_dup_task.status_code,
                        "text": r_dup_task.text,
                    },
                )
            else:
                t = r_dup_task.json()
                if isinstance(t, dict) and t.get("id"):
                    created_task_ids.append(t["id"])
                    fail(
                        "Сервер разрешил дублирование задач (неожиданно)",
                        request={
                            "url": f"{BASE}/tasks/",
                            "json": dup_task_payload,
                        },
                        response={"id": t["id"]},
                    )
        except Exception as exc:
            fail(
                "Ошибка при проверке дублирования задачи",
                details=str(exc),
                request={"url": f"{BASE}/tasks/", "json": dup_task_payload},
            )

        # Unauthorized checks
        try:
            r = request_with_retries(client, "GET", f"{BASE}/tasks/")
            if r.status_code == 200:
                ok("GET /tasks без авторизации работает (ожидаемо)")
            else:
                fail(
                    "GET /tasks без авторизации вернул ошибку",
                    details={"status_code": r.status_code},
                    response={"text": r.text},
                )
        except Exception as exc:
            fail(
                "Ошибка при проверке GET /tasks без авторизации",
                details=str(exc),
            )

        # Попытка зарегистрировать пользователя с существующим телефоном
        dup_user_payload = {
            "phone": "+70000000001",
            "first_name": "Dup",
            "last_name": "User",
            "password": "x",
        }
        try:
            r_dup_user = request_with_retries(
                client, "POST", f"{BASE}/users/", json=dup_user_payload
            )
            if r_dup_user.status_code >= 400:
                ok(
                    "Создание пользователя с существующим телефоном отклонено (ожидаемо)",
                    request={
                        "url": f"{BASE}/users/",
                        "json": dup_user_payload,
                    },
                    response={
                        "status_code": r_dup_user.status_code,
                        "text": r_dup_user.text,
                    },
                )
            else:
                fail(
                    "Сервер разрешил создание пользователя с дублирующимся телефоном (неожиданно)",
                    request={
                        "url": f"{BASE}/users/",
                        "json": dup_user_payload,
                    },
                    response={
                        "status_code": r_dup_user.status_code,
                        "text": r_dup_user.text,
                    },
                )
        except Exception as exc:
            fail(
                "Ошибка при проверке дублирования телефона",
                details=str(exc),
                request={"url": f"{BASE}/users/", "json": dup_user_payload},
            )

        # Слишком длинное имя категории
        try:
            long_name = "x" * 1025
            long_payload = {"name": long_name, "is_active": True}
            r_long = request_with_retries(
                client,
                "POST",
                f"{BASE}/categories/",
                json=long_payload,
                headers=auth_header(root_token),
            )
            if r_long.status_code >= 400:
                ok(
                    "Создание категории с очень длинным именем отклонено (ожидаемо)",
                    request={
                        "url": f"{BASE}/categories/",
                        "json": {"name_len": len(long_name)},
                    },
                    response={
                        "status_code": r_long.status_code,
                        "text": r_long.text,
                    },
                )
            else:
                cat = r_long.json()
                if isinstance(cat, dict) and cat.get("id"):
                    created_category_ids.append(cat["id"])
                    fail(
                        "Сервер разрешил слишком длинное имя категории (неожиданно)",
                        response={"id": cat["id"]},
                    )
        except Exception as exc:
            fail(
                "Ошибка при проверке длинного имени категории",
                details=str(exc),
            )

        ok("E2E: все проверки выполнены (частично).")

    return {
        "created_user_ids": created_user_ids,
        "created_category_ids": created_category_ids,
        "created_task_ids": created_task_ids,
        "steps": steps,
    }


if __name__ == "__main__":
    report: Dict = {
        "start_ts": datetime.utcnow().isoformat() + "Z",
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
                    else f"Не удалено: {m[:-1]} id={it.get('id')} ({it.get('reason') or it.get('error')})"
                )
                for m in ("tasks", "categories", "users")
                for it in cleanup_res.get(m, [])
            ]
        except Exception as e:
            report["cleanup"] = {"error": str(e)}
            report["cleanup_human"] = [f"Ошибка очистки: {e}"]

        report["end_ts"] = datetime.utcnow().isoformat() + "Z"
        with open("scripts/e2e_report.json", "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        if not report.get("success"):
            sys.exit(1)
