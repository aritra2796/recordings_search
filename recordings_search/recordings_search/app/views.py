from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .db import get_connection
from .models import AppLog
import logging
from datetime import datetime, timedelta
import base64
import pymysql

logger = logging.getLogger("app")


# --------------------------------------------------
# Helper function to store logs in database
# --------------------------------------------------
def log_to_db(level, message, request=None):
    AppLog.objects.create(
        level=level,
        message=message,
        user=request.session.get("user") if request else None,
        ip_address=request.META.get("REMOTE_ADDR") if request else None
    )


# --------------------------------------------------
# API: Get Processes
# --------------------------------------------------
def get_processes(request):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT DISTINCT Campaign FROM REC_MASTER ORDER BY Campaign")
    rows = cursor.fetchall()
    conn.close()
    return JsonResponse([row["Campaign"] for row in rows], safe=False)


# --------------------------------------------------
# API: Get Sub Processes
# --------------------------------------------------
def get_subprocesses(request):
    campaign = request.GET.get("process", "").strip()
    if not campaign:
        return JsonResponse([], safe=False)

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT DISTINCT Sub_disposition_code
        FROM REC_MASTER
        WHERE Campaign=%s
          AND Sub_disposition_code IS NOT NULL
          AND Sub_disposition_code != ''
        ORDER BY Sub_disposition_code
    """, (campaign,))
    rows = cursor.fetchall()
    conn.close()
    return JsonResponse([row["Sub_disposition_code"] for row in rows], safe=False)


# --------------------------------------------------
# Search View
# --------------------------------------------------
def search_view(request):
    if "user" not in request.session:
        return redirect("login")

    today_str = datetime.today().strftime("%Y-%m-%d")

    page = int(request.GET.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page

    # ---------------- POST (redirect to GET)
    if request.method == "POST":
        process = request.POST.get("process", "").strip()
        sub_process = request.POST.get("sub_process", "").strip()
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")

        if not (process and sub_process and from_date and to_date):
            return HttpResponse("Mandatory fields missing")

        params = {
            "page": 1,
            "process": process,
            "sub_process": sub_process,
            "from_date": from_date,
            "to_date": to_date,
            "agent_id": request.POST.get("agent_id", "").strip(),
            "phone_number": request.POST.get("phone_number", "").strip(),
            "disposition": request.POST.get("disposition", "").strip(),
            "sub_disposition": request.POST.get("sub_disposition", "").strip(),
            "call_duration": request.POST.get("call_duration", "").strip(),
            "wrap_time": request.POST.get("wrap_time", "").strip(),
            "connid": request.POST.get("connid", "").strip(),
            "unique_id": request.POST.get("unique_id", "").strip(),
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items() if v])
        return redirect(f"/search/?{query_string}")

    # ---------------- GET (execute search)
    process = request.GET.get("process", "").strip()
    sub_process = request.GET.get("sub_process", "").strip()
    from_date_str = request.GET.get("from_date", today_str)
    to_date_str = request.GET.get("to_date", today_str)

    if not (process and sub_process and from_date_str and to_date_str):
        return render(request, "core/search.html", {"today": today_str})

    agent_id = request.GET.get("agent_id")
    phone_number = request.GET.get("phone_number")
    disposition = request.GET.get("disposition")
    sub_disposition = request.GET.get("sub_disposition")
    call_duration = request.GET.get("call_duration")
    wrap_time = request.GET.get("wrap_time")
    connid = request.GET.get("connid")
    unique_id = request.GET.get("unique_id")

    from_datetime = datetime.strptime(from_date_str, "%Y-%m-%d")
    to_datetime = datetime.strptime(to_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

    where_clauses = [
        "Campaign=%s",
        "Sub_disposition_code=%s",
        "StartTime BETWEEN %s AND %s"
    ]
    params = [process, sub_process, from_datetime, to_datetime]

    if agent_id:
        where_clauses.append("AgentId=%s")
        params.append(agent_id)

    if phone_number:
        where_clauses.append("PhoneNumber=%s")
        params.append(phone_number)

    if disposition:
        where_clauses.append("Disposition=%s")
        params.append(disposition)

    if sub_disposition:
        where_clauses.append("Sub_disposition_code=%s")
        params.append(sub_disposition)

    if call_duration:
        where_clauses.append("TIMESTAMPDIFF(SECOND, StartTime, EndTime) >= %s")
        params.append(call_duration)

    if wrap_time:
        where_clauses.append("WrapTime=%s")
        params.append(wrap_time)

    if connid:
        where_clauses.append("CONNID=%s")
        params.append(connid)

    if unique_id:
        where_clauses.append("UniqueId=%s")
        params.append(unique_id)

    where_sql = " AND ".join(where_clauses)

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Count
    cursor.execute(
        f"SELECT COUNT(*) AS total FROM REC_MASTER WHERE {where_sql}",
        params
    )
    total_records = cursor.fetchone()["total"]
    total_pages = (total_records + per_page - 1) // per_page

    # Data
    cursor.execute(f"""
        SELECT
            StartTime AS Date,
            PhoneNumber,
            CONNID AS ConnID,
            Campaign AS Process,
            Sub_disposition_code AS SubProcess,
            Disposition,
            AgentId AS AgentName,
            TIMESTAMPDIFF(SECOND, StartTime, EndTime) AS CallLength,
            CPath
        FROM REC_MASTER
        WHERE {where_sql}
        ORDER BY StartTime DESC
        LIMIT %s OFFSET %s
    """, params + [per_page, offset])

    results = cursor.fetchall()
    conn.close()

    for row in results:
        try:
            file_path = row["CPath"].replace("\\", "/")
            with open(file_path, "rb") as f:
                row["AudioBase64"] = base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            row["AudioBase64"] = ""
            logger.error("Audio file error", exc_info=True)
            log_to_db("ERROR", f"Audio file error: {row.get('CPath')}", request)

    logger.info(f"Search executed | {request.GET.dict()}")
    log_to_db("INFO", f"Search executed | {request.GET.dict()}", request)

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(request, "core/results.html", {
        "results": results,
        "page": page,
        "total_pages": total_pages,
        "pages": list(range(1, total_pages + 1)),
        "query_string": query_params.urlencode(),
    })


# --------------------------------------------------
# Login View
# --------------------------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            request.session["user"] = username
            logger.info(f"User logged in: {username}")
            log_to_db("INFO", f"User logged in: {username}", request)
            return redirect("search")
        else:
            logger.warning(f"Failed login attempt: {username}")
            log_to_db("WARNING", f"Failed login attempt: {username}", request)
            return HttpResponse("Invalid credentials")

    return render(request, "core/login.html")
