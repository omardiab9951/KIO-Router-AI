"""Route valid predictions to a simulated agent."""

from .agents import sales_agent, support_agent


def dispatch(message, router):
    output = router.predict(message)
    if output.label == "support":
        return output, support_agent(message)
    if output.label == "sales":
        return output, sales_agent(message)
    return output, None

