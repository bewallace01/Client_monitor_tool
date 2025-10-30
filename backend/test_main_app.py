from app.main import app

print(f'App has {len(app.routes)} routes total')
print('\nAll routes:')
for route in app.routes:
    path = getattr(route, 'path', 'N/A')
    methods = getattr(route, 'methods', set())
    print(f'  - {path} [{methods}]')

print('\nAuth routes:')
auth_routes = [r for r in app.routes if 'auth' in str(getattr(r, 'path', ''))]
if auth_routes:
    for route in auth_routes:
        path = getattr(route, 'path', 'N/A')
        methods = getattr(route, 'methods', set())
        print(f'  - {path} [{methods}]')
else:
    print('  NO AUTH ROUTES FOUND!')
