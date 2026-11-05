from backend.app.stacks.strategy.user_activation import api


def test_allocation_proposals_route_is_authenticated_read_only():
    routes = {}

    for route in api.router.routes:
        routes.setdefault(route.path, set()).update(
            route.methods or set()
        )

    path = "/api/v1/strategy-library/allocation-proposals"

    assert routes[path] == {"GET"}

    endpoint = next(
        route.endpoint
        for route in api.router.routes
        if route.path == path
    )

    assert endpoint.__name__ == "get_allocation_proposals"
