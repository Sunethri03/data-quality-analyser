from supabase import create_client

url = "https://mkwbogowtaihgofsnxgb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1rd2JvZ293dGFpaGdvZnNueGdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3MzEzNDgsImV4cCI6MjA4OTMwNzM0OH0.HCBhcFM4nKobmwzooNyAXNt8K70G8YT8W-hDobFeanU"

supabase = create_client(url, key)


def add_user(username, password):
    data = {"username": username, "password": password}

    response = supabase.table("users").insert(data).execute()
    print(response)


# ✅ Get all users (THIS WAS MISSING ❗)
def get_all_users():
    response = supabase.table("users").select("*").execute()
    return response.data
