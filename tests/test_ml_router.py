import json

from kio.agents import sales_agent, support_agent
from kio.base import RouterOutput
from kio.ml_router import MLRouter
from kio.router import dispatch


def test_ml_router_support_and_sales():
    router = MLRouter()
    support = router.predict("My existing internet service is broken.")
    sales = router.predict("I want to buy a new family package.")
    assert support.status == "ok" and support.label == "support" and support.flag == 0
    assert sales.status == "ok" and sales.label == "sales" and sales.flag == 1
    assert 0 <= support.confidence <= 1
    assert set(json.loads(support.raw)["probabilities"]) == {"support", "sales"}


def test_label_flag_mapping():
    router = MLRouter()
    assert router.predict("Please repair my current service.").flag == 0
    assert router.predict("What is the price of a new plan?").flag == 1


def test_empty_and_missing_model_are_invalid(tmp_path):
    assert MLRouter(tmp_path / "missing.joblib").predict("").status == "empty_message"
    result = MLRouter(tmp_path / "missing.joblib").predict("Please help with my account.")
    assert result.label == "invalid" and result.flag is None and result.status.startswith("missing_model")


class StubRouter:
    def __init__(self, label):
        self.label = label

    def predict(self, message):
        flag = {"support": 0, "sales": 1}[self.label]
        return RouterOutput(self.label, flag, 1.0, self.label, 0.0, "ok", "stub")


def test_dispatch_routes_both_labels():
    support, support_name = dispatch("existing problem", StubRouter("support"))
    sales, sales_name = dispatch("new purchase", StubRouter("sales"))
    assert support.flag == 0 and support_name == "support_agent"
    assert sales.flag == 1 and sales_name == "sales_agent"


def test_saved_ml_results_regression():
    import pandas as pd
    from kio.data import get_test

    expected = pd.read_csv("results/ml_results.csv").set_index("ID")
    router = MLRouter()
    test = get_test(i_am_the_final_evaluation=True)
    for row in test.itertuples(index=False):
        output = router.predict(row.Message)
        assert output.label == expected.loc[row.ID, "predicted label"]
