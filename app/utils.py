# 哈希加密
from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# 哈希密码
def hash(password: str):
    return pwd_context.hash(password)

# 校验密码（登录时使用）
def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

