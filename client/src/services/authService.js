const API_URL = "http://localhost:8000/api/auth";

export async function register({ name, email, password }) {
  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Registration failed");
  return await res.json();
}

export async function login({ email, password }) {
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
  return await res.json();
} 

export async function connectGmail() {
  // User clicks "Connect Gmail"
  // Your app redirects to Google (using YOUR OAuth credentials)
  // User authorizes your app to send emails from their Gmail
  // Google sends back tokens to your app
  // User can now send emails from their own Gmail address
  const res = await fetch(`${API_URL}/connect-gmail`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Gmail connection failed");
  return await res.json();
}