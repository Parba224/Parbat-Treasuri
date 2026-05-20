import bcrypt

password = "parbat2026"

hashed = bcrypt.hashpw(
    password.encode(),
    bcrypt.gensalt()
)

print(hashed.decode())