"""
Test script to verify API config routes are loaded
"""
from app.main import app

print("=" * 60)
print("ROUTE VERIFICATION TEST")
print("=" * 60)

# Get all routes
all_routes = [(route.path, list(route.methods) if hasattr(route, 'methods') else []) for route in app.routes]

# Filter API config routes
api_config_routes = [(path, methods) for path, methods in all_routes if 'api-config' in path]

print(f"\nTotal routes in app: {len(all_routes)}")
print(f"API Config routes: {len(api_config_routes)}")
print("\n" + "=" * 60)
print("API CONFIGURATION ROUTES:")
print("=" * 60)

if api_config_routes:
    for path, methods in api_config_routes:
        methods_str = ', '.join(methods) if methods else 'N/A'
        print(f"{methods_str:20} {path}")
    print("\n[SUCCESS] API Configuration routes are loaded!")
else:
    print("\n[ERROR] No API Configuration routes found!")
    print("\nAll available routes:")
    for path, methods in all_routes[:10]:
        methods_str = ', '.join(methods) if methods else 'N/A'
        print(f"{methods_str:20} {path}")

print("=" * 60)
