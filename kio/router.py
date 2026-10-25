"""Route valid predictions to a simulated agent."""

from .agents import sales_agent, support_agent


def dispatch(message, router):
    if isinstance(router, str):
        if router == "ml":
            from .ml_router import MLRouter
            router = MLRouter()
        elif router == "clef":
            from .clef_router import ClefRouter
            router = ClefRouter()
        else:
            raise ValueError(f"Unknown router choice: {router}")
    output = router.predict(message)
    if output.label == "support":
        return output, support_agent(message)
    if output.label == "sales":
        return output, sales_agent(message)
    return output, None

