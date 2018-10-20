import os

env = os.environ.get("APP_ENV", "dev")

# Common settings
MONGO_MATCHES_COLLECTION = "matches"

if env == "dev":
    # Development settings
    MONGODB_HOST = os.environ.get("MONGO_HOST", "127.0.0.1")
    MONGODB_PORT = int(os.environ.get("MONGO_PORT", 27017))
    MONGODB_DB = "apiestas"
elif env == "prod":
    # Production settings
    MONGODB_HOST = os.getenv('MONGO_HOST')
    MONGODB_PORT = int(os.getenv('MONGO_PORT'))
    MONGODB_DB = os.getenv('MONGO_DB')
else:
    raise EnvironmentError("{} is not a valid APP_ENV".format(env))




