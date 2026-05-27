def load_config(path):
    """Load configuration from a JSON file."""
    import json

    with open(path) as f:
        return json.load(f)


def get_db_url(config):
    return f"postgres://{config['user']}:{config['pass']}@{config['host']}/{config['db']}"


def init_db(config):
    """Initialize the database connection pool."""
    url = get_db_url(config)
    return {"url": url, "pool_size": 10, "connected": True}


def run_migration(migration_name, db):
    print(f"Running migration: {migration_name}")
    return True


def rollback_migration(migration_name, db):
    print(f"Rolling back: {migration_name}")
    return True
