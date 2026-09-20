from tenacity import retry,wait_exponential_jitter,stop_after_attempt,retry_if_exception_type

from src.utils.exceptions import TransientIngestionError,FatalSchemaError,RateLimitError,ServiceUnavailableError


fintech_retry=retry(
    retry=retry_if_exception_type(TransientIngestionError),
    wait=wait_exponential_jitter(initial=1,max=60),
    stop=stop_after_attempt(3),
    reraise=True
)

@fintech_retry
def raise_error(status_code:int)->str:
    if status_code == 429:
       raise RateLimitError("HTTP 429: Rate limit exceeded")
    if status_code == 503:
       raise ServiceUnavailableError("HTTP 503: Service temporarily unavailable")
    return "error"
