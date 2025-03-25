import os
import datetime
import inspect
import json


class BaseLogging:
    def __init__(self, log_file="app.log"):
        self.log_file = log_file
        self._cleanup_old_logs()
    
    def _write_log(self, level, message: str = "", exception: Exception = None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        frame = inspect.stack()[3]
        file_name = os.path.abspath(frame.filename)
        line_number = frame.lineno

        log_entry = {
            "timestamp": timestamp,
            "level": level.upper(),
            "file": file_name,
            "line": line_number,
            "message": message or None,
            "exception": str(type(exception).__name__) if exception else None
        }

        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def _write_info_log(self, level, message: str = ""):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = {
            "timestamp": timestamp,
            "level": level.upper(),
            "message": message or None
        }

        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def info(self, message):
        self._write_info_log("info", message=message)
    
    def error(self, exception, message: str = ""):
        self._write_log("error", exception=exception, message=message)
    
    def all(self, message):
        self._write_log("all", message)
    
    def _cleanup_old_logs(self):
        if not os.path.exists(self.log_file):
            return

        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                lines = file.readlines()

            three_months_ago = datetime.datetime.now() - datetime.timedelta(days=90)
            filtered_lines = []

            for line in lines:
                try:
                    log_entry = json.loads(line.strip())  # Читаем строку как JSON
                    log_time = datetime.datetime.strptime(log_entry["timestamp"], "%Y-%m-%d %H:%M:%S")
                    if log_time >= three_months_ago:
                        filtered_lines.append(line)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue  # Пропускаем некорректные строки

            with open(self.log_file, "w", encoding="utf-8") as file:
                file.writelines(filtered_lines)

        except Exception as e:
            print(f"Ошибка при очистке логов: {e}")
