const BASE = "http://127.0.0.1:8000";

// const BASE ="";

// const BASE = "https://claim-backend-4xum.onrender.com";


export async function register(
  phone,
  name,
  password,
  confirmPassword
) {

  const res = await fetch(
    `${BASE}/auth/register`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        phone_number: phone,
        name,
        password,
        confirm_password: confirmPassword
      })
    }
  );

  const data = await res.json();

  return data;
}

export async function login(
  phone,
  password
) {

  const res = await fetch(
    `${BASE}/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        phone_number: phone,
        password: password
      })
    }
  );

  const data = await res.json();

  return data;
}

export async function createCase(data) {
  const res = await fetch(`${BASE}/cases/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  return res.json();
}

export async function getCases(userId) {
  const res = await fetch(`${BASE}/cases/${userId}`);
  return res.json();
}

export async function getInterviewDetails(caseId, subcategory) {
  // ✅ FIX 10: API CALL SAFETY
  if (!caseId) return [];

  let url = `${BASE}/interview/by-case/${caseId}`;

  if (subcategory) {
    url += `?subcategory=${encodeURIComponent(subcategory)}`;
  }

  const res = await fetch(url);
  return res.json();
}

export async function getVideos(caseId, subcategory) {
  // ✅ API CALL SAFETY
  if (!caseId) return [];

  let url = `${BASE}/videos/${caseId}`;

  if (subcategory) {
    url += `?subcategory=${encodeURIComponent(subcategory)}`;
  }

  const res = await fetch(url);
  return res.json();
}

// 📄 DOCUMENT APIs

export async function uploadDocument(formData) {
  const res = await fetch(`${BASE}/documents/upload`, {
    method: "POST",
    body: formData
  });

  return res.json();
}

export async function getDocuments(caseId, subcategory) {
  let url = `${BASE}/documents/${caseId}`;

  if (subcategory) {
    url += `?subcategory=${encodeURIComponent(subcategory)}`;
  }

  const res = await fetch(url);
  return res.json();
}

export async function getAllCases(params = {}) {
  let url = `${BASE}/cases/all`;

  const query = new URLSearchParams();

  if (params.claim_type) {
    query.append("claim_type", params.claim_type);
  }

  if (query.toString()) {
    url += `?${query.toString()}`;
  }

  const res = await fetch(url);
  return res.json();
}


export async function uploadExcel(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE}/admin/upload-excel`, {
    method: "POST",
    body: formData
  });

  return res.json();
}


export async function updateCase(caseId, data) {
  const res = await fetch(`${BASE}/cases/update/${caseId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  return res.json();
}


export async function getCaseById(caseId) {
  const res = await fetch(`${BASE}/cases/by-id/${caseId}`);
  return res.json();
}

export async function updateInterview(interviewId, data) {
  const res = await fetch(`${BASE}/interview/update/${interviewId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  return res.json();
}


export async function getCaseLogs(caseId, subcategory) {
  let url = `${BASE}/cases/logs/${caseId}`;

  if (subcategory) {
    url += `?subcategory=${encodeURIComponent(subcategory)}`;
  }

  const res = await fetch(url);
  return res.json();
}

export async function reassignCase(caseId, user_id) {
  const res = await fetch(`${BASE}/cases/reassign/${caseId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id })
  });
  return res.json();
}

export async function getUsers() {
  const res = await fetch(`${BASE}/cases/users`);
  return res.json();
}


export async function getStatusReport(caseId) {
  if (!caseId) return [];

  const res = await fetch(`${BASE}/cases/status-report/${caseId}`);
  return res.json();
}


export async function addRemark(caseId, data) {
  const res = await fetch(`${BASE}/cases/${caseId}/remarks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function getRemarks(caseId) {
  const res = await fetch(`${BASE}/cases/${caseId}/remarks`);
  return res.json();
}

export async function updateRemark(remarkId, data) {
  const res = await fetch(`${BASE}/cases/remarks/${remarkId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function analyzeStatement(documentId) {

  const res = await fetch(
    `${BASE}/statement-analysis/analyze/${documentId}`,
    {
      method: "POST"
    }
  );

  return res.json();
}


// export async function sendOtp(phone) {
//   const res = await fetch(`${BASE}/auth/send-otp`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ phone_number: phone })
//   });
//   return res.json();
// }

// export async function verifyOtp(phone, otp) {
//   const res = await fetch(`${BASE}/auth/verify-otp`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ phone_number: phone, otp })
//   });
//   return res.json();
// }