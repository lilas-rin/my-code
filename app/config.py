from functools import lru_cache
from urllib.parse import quote_plus
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    database_driver: str | None = Field(default=None, alias="DATABASE_DRIVER")
    database_host: str | None = Field(default=None, alias="DATABASE_HOST")
    database_port: int | None = Field(default=None, alias="DATABASE_PORT", gt=0, le=65535)
    database_name: str | None = Field(default=None, alias="DATABASE_NAME")
    database_user: str | None = Field(default=None, alias="DATABASE_USER")
    database_password: SecretStr | None = Field(default=None, alias="DATABASE_PASSWORD")

    jwt_secret_key: SecretStr = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(..., alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES", gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator(
        "database_url",
        "database_driver",
        "database_host",
        "database_name",
        "database_user",
        "jwt_algorithm",
    )
    @classmethod
    def validate_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("must contain at least 32 characters")
        return value

    @model_validator(mode="after")
    def validate_database_settings(self) -> "Settings":
        if self.database_url:
            return self

        required_fields = {
            "DATABASE_DRIVER": self.database_driver,
            "DATABASE_HOST": self.database_host,
            "DATABASE_PORT": self.database_port,
            "DATABASE_NAME": self.database_name,
            "DATABASE_USER": self.database_user,
            "DATABASE_PASSWORD": self.database_password,
        }
        missing_fields = [
            env_name
            for env_name, value in required_fields.items()
            if value is None or (isinstance(value, str) and not value.strip())
        ]

        if missing_fields:
            raise ValueError(
                "set DATABASE_URL or set all database connection variables: "
                + ", ".join(missing_fields)
            )

        return self

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        username = quote_plus(self.database_user or "")
        password = quote_plus((self.database_password or SecretStr("")).get_secret_value())
        return (
            f"{self.database_driver}://{username}:{password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def jwt_secret(self) -> str:
        return self.jwt_secret_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()
