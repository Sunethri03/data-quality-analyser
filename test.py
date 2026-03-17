from db import add_user, get_all_users

# 🔥 Add user (this should go to Supabase)
add_user("sunet", "123")

# 🔥 Fetch users
users = get_all_users()

print("USERS:", users)
