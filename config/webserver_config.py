# Webserver configuration for Airflow - No Authentication
# Completely disable authentication for development

# Disable CSRF for easier development
WTF_CSRF_ENABLED = False
SECRET_KEY = 'dev-secret-key'

# Disable all authentication
AUTH_TYPE = 'NONE'
AUTH_ROLE_PUBLIC = 'Admin'
AUTH_USER_DB = None

# No security restrictions
FAB_SECURITY_ALLOW_UNSAFE_URLS = True
FAB_ADD_SECURITY_API = False
FAB_ADD_SECURITY_VIEWS = False

# Session settings
PERMANENT_SESSION_LIFETIME = 3600

# No rate limiting
RATELIMIT_ENABLED = False