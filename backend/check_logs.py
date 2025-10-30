from app.database.connection import SessionLocal
from app.models.api_request_log import APIRequestLog
from app.models.circuit_breaker import CircuitBreaker

db = SessionLocal()

logs = db.query(APIRequestLog).order_by(APIRequestLog.created_at.desc()).all()
breakers = db.query(CircuitBreaker).all()

print(f'Total API request logs: {len(logs)}')
print(f'Total circuit breakers: {len(breakers)}')
print()

print('=== API REQUEST LOGS ===')
for i, log in enumerate(logs):
    print(f'\n{i+1}. Provider: {log.provider}')
    print(f'   Success: {log.success}')
    print(f'   Client: {log.client_name}')
    print(f'   Time: {log.created_at}')
    print(f'   Response time: {log.response_time_ms}ms')
    print(f'   Results: {log.results_count}')
    print(f'   Error type: {log.error_type}')
    print(f'   Error: {log.error_message[:150] if log.error_message else "None"}')

print('\n=== CIRCUIT BREAKERS ===')
for i, breaker in enumerate(breakers):
    print(f'\n{i+1}. API Config: {str(breaker.api_config_id)[:8]}...')
    print(f'   State: {breaker.state}')
    print(f'   Consecutive failures: {breaker.consecutive_failures}/{breaker.failure_threshold}')
    print(f'   Last failure: {breaker.last_failure_at}')
    print(f'   Manually disabled: {breaker.manually_disabled}')

db.close()
