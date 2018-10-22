import os

env = os.environ.get("APP_ENV", "dev")

# Common settings
MONGO_MATCHES_COLLECTION = "matches"

if env == "dev":
    # Development settings
    DEBUG = True
    MONGO_HOST = os.environ.get("MONGO_HOST", "127.0.0.1")
    MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
    MONGO_DBNAME = "apiestas"
elif env == "prod":
    # Production settings
    DEBUG = False
    MONGO_HOST = os.getenv('MONGO_HOST')
    MONGO_PORT = int(os.getenv('MONGO_PORT'))
    MONGO_DBNAME = os.getenv('MONGO_DBNAME')
else:
    raise EnvironmentError("{} is not a valid APP_ENV".format(env))

# Configure "matches" domain
matches = {
    "hateoas": False,
    "schema": {
        "tournament": {"type": "string", "nullable": False, "required": True},
        "date": {"type": "datetime", "nullable": False, "required": True},
        "team_1": {"type": "string", "nullable": False, "required": True},
        "team_2": {"type": "string", "nullable": False, "required": True},
        "bets" : {'type': 'list', 'schema': {
            "bookmaker": {"type": "string", "nullable": False, "required": True},
            "url": {"type": "string"}, "nullable": False, "required": True,
            "feed": {"type": "string", "nullable": False, "required": True},
            "date_extracted": {"type": "datetime", "nullable": False, "required": True},
            "results": {"type": "list", "schema": {
                "name": {"type": "string", "nullable": False, "required": True, "maxlength": 1},
                "odds": {"type": "float", "nullable": False, "required": True}
            }}
            }
        }
    }
}

DOMAIN = {'matches': matches}

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET']

# Enable reads (GET), edits (PATCH) and deletes of individual items
# (defaults to read-only item access).
ITEM_METHODS = ['GET']

