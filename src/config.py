from .constants import LAUNCH_TIME
from .exceptions.config import (
    ConfigNotFoundError,
    InvalidConfigError,
    InvalidOffsetValueError,
    InvalidReleaseDateError,
)
from .file_operations.file_manager import FileManager
from .utils import compile_regex, get_monthrange


class Config:
    def __init__(self, config_file_name) -> None:
        self.config_file_name = config_file_name
        self._load_config()
        self._parse_config()
        self._calculate_totals()

    def _load_config(self) -> None:
        try:
            self.config = FileManager.safe_yaml_file(self.config_file_name)
        except FileNotFoundError:
            raise ConfigNotFoundError from None

    def _parse_config(self) -> None:
        try:
            self.offset_bool = self.config["offset"]["offset"]
            self.offset_value = self._validate_offset(self.config["offset"]["value"])
            self.release_date_bool = self.config["release_date"]["release_date"]
            self.release_date = self._validate_release_date(
                self.config["release_date"]["years"]
            )
            self.websites = self.config["websites"]
            self.exceptions = self.config["exceptions"]
            self.login_regex = compile_regex(
                self.config["for_advanced_users"]["login_regex"]
            )
            self.password_regex = compile_regex(
                self.config["for_advanced_users"]["password_regex"]
            )
        except (KeyError, TypeError) as e:
            raise InvalidConfigError(e) from None

    def _validate_offset(self, value: any) -> int:
        if not self.offset_bool:
            return 1

        if not (isinstance(value, int) and 2 <= value <= 250):
            raise InvalidOffsetValueError(offset_value=value)

        return value

    def _validate_release_date(self, values: list[any]) -> list[int] | None:
        if not self.release_date_bool:
            return None

        for value in values:
            if not (isinstance(value, int) and 0 <= value <= LAUNCH_TIME.year):
                raise InvalidReleaseDateError(release_date=value)

        return values

    def _calculate_totals(self) -> None:
        self.total_months = (
            LAUNCH_TIME.month
            if self.release_date_bool and self.release_date == [LAUNCH_TIME.year]
            else 12
        )
        self.total_days = (
            sum(get_monthrange(month) for month in range(1, self.total_months + 1))
            if self.total_months != 12
            else 366
        )
        self.total_urls = len(self.websites) * self.offset_value * self.total_days
