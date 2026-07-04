_cache = {
    "system_tree_summary": None,
    "likely_next": [],
    "warm_context": {}
}


def store_prediction(key, value):
    _cache[key] = value


def get_prediction(key):
    return _cache.get(key)


def clear_predictions():
    _cache["likely_next"] = []
    _cache["warm_context"] = {}
