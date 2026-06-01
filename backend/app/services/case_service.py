from app.db.supabase_client import supabase

from app.services.case_log_service import log_case_event

MOTOR_SUBCATEGORIES = [
    "insured",
    "driver",
    "claimant",
    "accident spot",
    "hospital",
    "police station",
    "eye witnesses",
    "others"
]


def create_case(user_id, case_id, claim_type, category=None, investigator_name=None):

    # check existing cases
    query = supabase.table("cases") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("case_id", case_id) \
        .eq("claim_type", claim_type)

    if claim_type == "motor" and category:
        query = query.eq("category", category)

    existing = query.execute()

    if existing.data:
        return {"error": "Case already exists"}

    # insert new case
    result = supabase.table("cases").insert({
    "user_id": user_id,
    "case_id": case_id,
    "claim_type": claim_type,
    "category": category,
    "investigator_name": investigator_name  # ✅ FIX
}).execute()
    
    case = result.data[0]

    log_case_event(
        case["id"],
        "CASE_CREATED",
        f"Case {case['case_id']} created",
        investigator_name
    )

    return case

    


def get_cases(user_id):

    print("GET CASES CALLED FOR:", user_id)

    # 🔹 OLD CASES (manual created)
    old_cases = supabase.table("cases") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    # 🔹 NEW CASES (Excel assigned)
    new_cases = supabase.table("cases") \
        .select("*") \
        .eq("assigned_user_id", user_id) \
        .execute()

    # 🔹 MERGE BOTH
    combined = []

    if old_cases.data:
        combined.extend(old_cases.data)

    if new_cases.data:
        combined.extend(new_cases.data)

    print("OLD:", old_cases.data)
    print("NEW:", new_cases.data)
    print("COMBINED:", combined)

    return combined


def get_case(case_uuid):

    result = supabase.table("cases")\
        .select("*")\
        .eq("id", case_uuid)\
        .execute()

    return result.data[0]


def auto_assign_cases_to_user(user_id: str, user_name: str):
    """
    Assign unassigned cases to user based on investigator_name match.
    Safe: does not override existing assignments.
    """

    try:
        # 🔹 Normalize name (case-insensitive match)
        name = user_name.strip().lower()

        # 🔹 Fetch matching unassigned cases
        response = supabase.table("cases") \
            .select("id, investigator_name") \
            .is_("assigned_user_id", None) \
            .execute()

        if not response.data:
            return

        updated_count = 0

        for case in response.data:
            inv_name = case.get("investigator_name")

            if not inv_name:
                continue

            if inv_name.strip().lower() == name:
                supabase.table("cases") \
                    .update({"assigned_user_id": user_id}) \
                    .eq("id", case["id"]) \
                    .execute()

                updated_count += 1

        print(f"✅ AUTO-ASSIGNED CASES: {updated_count}")

    except Exception as e:
        print("❌ AUTO ASSIGN ERROR:", e)

def get_status_report(case_id: str):

    # 🔹 STEP 1: GET UUID
    case = supabase.table("cases") \
        .select("id, claim_type") \
        .eq("case_id", case_id) \
        .limit(1) \
        .execute()

    if not case.data:
        return []

    case_uuid = case.data[0]["id"]
    claim_type = case.data[0]["claim_type"]

    # 🔹 ONLY MOTOR
    if claim_type != "motor":
        return []

    # 🔹 STEP 2: FETCH DATA
    interviews = supabase.table("interviews") \
        .select("subcategory") \
        .eq("case_id", case_uuid) \
        .execute()

    videos = supabase.table("videos") \
        .select("subcategory") \
        .eq("case_id", case_uuid) \
        .execute()

    documents = supabase.table("documents") \
        .select("subcategory") \
        .eq("case_id", case_uuid) \
        .execute()

    # 🔹 STEP 3: BUILD SET
    completed = set()

    def normalize(value):
        if not value:
            return None
        return value.strip().lower()

    for row in (interviews.data or []):
        val = normalize(row.get("subcategory"))
        if val:
            completed.add(val)

    for row in (videos.data or []):
        val = normalize(row.get("subcategory"))
        if val:
            completed.add(val)

    for row in (documents.data or []):
        val = normalize(row.get("subcategory"))
        if val:
            completed.add(val)

    # 🔹 STEP 4: BUILD RESPONSE
    report = []

    for sub in MOTOR_SUBCATEGORIES:
        report.append({
            "subcategory": sub,
            "status": "completed" if sub in completed else "pending"
        })

    return report