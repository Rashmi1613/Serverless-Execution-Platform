import time

def track_execution(fn):
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = fn(*args, **kwargs)
            duration = time.time() - start
            log_metrics(duration, success=True)
            return result
        except Exception as e:
            duration = time.time() - start
            log_metrics(duration, success=False, error=str(e))
            raise e
    return wrapper
