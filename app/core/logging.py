import logging
import sys

from app.core.request_context import get_trace_id, get_user_id


# 日志过滤器：给每条日志注入 trace_id 和 user_id
class RequestContextFilter(logging.Filter):
    # 从 ContextVar 取出链路信息并写入日志记录
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        record.user_id = get_user_id()
        return True


# 初始化日志：配置格式、处理器和过滤器
def setup_logging():
    logger = logging.getLogger()

    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | "
            "trace_id=%(trace_id)s | user_id=%(user_id)s | "
            "%(name)s:%(lineno)d | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    handler.addFilter(RequestContextFilter())

    logger.addHandler(handler)


# 按模块名获取 logger
def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
