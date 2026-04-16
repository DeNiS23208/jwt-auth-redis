from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


password = "123456"

hashed = hash_password(password)
print("Хеш пароля:")
print(hashed)
print()
print("Проверка правильного пароля:")
print(verify_password("123456", hashed))
print()

print("Проверка неправильного пароля:")
print(verify_password("000000", hashed))
print()

access_token = create_access_token(user_id=1, role="role1")
print("Access token:")
print(access_token)
print()

decoded_access = decode_token(access_token)
print("Декодированный access token:")
print(decoded_access)
print()

refresh_token = create_refresh_token(user_id=1, role="role1")
print("Refresh token:")
print(refresh_token)
print()

decoded_refresh = decode_token(refresh_token)
print("Декодированный refresh token:")
print(decoded_refresh)
