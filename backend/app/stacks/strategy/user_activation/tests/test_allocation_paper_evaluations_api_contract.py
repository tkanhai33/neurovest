from backend.app.stacks.strategy.user_activation import api


def test_paper_evaluations_route_is_authenticated_get_only():
    path = (
        "/api/v1/strategy-library/"
        "allocation-proposals/paper-evaluations"
    )

    route = next(
        route
        for route in api.router.routes
        if route.path == path
    )

    assert route.methods == {"GET"}
    assert route.endpoint.__name__ == "get_allocation_paper_evaluations"
