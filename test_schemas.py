from pydantic import ValidationError

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.schemas.content import ContentResponse


print("Проверка импорта схем...")
print(RegisterRequest)
print(LoginRequest)
print(TokenResponse)
print(UserResponse)
print(ContentResponse)
print("Импорт схем прошел успешно!")


print("Проверка валидных данных")
register_data = RegisterRequest(
    email="denis@example.com",
    password="12345",
    role_id=100,
)
print('RegisterRequest валиден:', register_data)


login_data = LoginRequest(
    email="denis@example.com",
    password="12345",
)
print('LoginRequest валиден:', login_data)


token_data = TokenResponse(
    access_token="access123",
    refresh_token="refresh123",
)
print('TokenResponse валиден:', token_data)


user_data = UserResponse(
    id=1,
    email="denis@example.com",
    is_active=True,
    role_id=1,
)
print('UserResponse валиден:', user_data)


content_data = ContentResponse(
    id=1,
    title="Общая новость",
    body="Это общая новость для всех пользователей.",
    access_level="common",
)
print('ContentResponse валиден:', content_data)
print()

print("Проверка невалидных данных")
try:
    bad_login = LoginRequest(
        email="denis@examplecom",
        password="12345",
    )
    print(bad_login)
except ValidationError as error:
    print("Ошибка валидации поймана успешно:")
    print(error)