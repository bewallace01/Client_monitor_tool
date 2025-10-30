from app.api.routes import auth

print('Auth router imported successfully')
print(f'Router has {len(auth.router.routes)} routes')
for route in auth.router.routes:
    methods = getattr(route, 'methods', 'N/A')
    print(f'  - {route.path} [{methods}]')
