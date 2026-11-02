import ast
from decimal import Decimal
from pathlib import Path
import unittest
from unittest.mock import MagicMock

import pandas as pd

from services.revenue_scenario import revenue_with_one_order

ROOT = Path(__file__).resolve().parents[1]


def load_function(path, name, namespace):
    tree = ast.parse((ROOT / path).read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), path, "exec"), namespace)
    return namespace[name]


class RevenueScenarioTests(unittest.TestCase):
    def test_empty_history_does_not_invent_revenue(self):
        self.assertEqual(revenue_with_one_order([]), Decimal("0"))

    def test_single_order_is_explicitly_repeated(self):
        self.assertEqual(revenue_with_one_order(["12.50"]), Decimal("25"))

    def test_two_orders_use_available_history(self):
        self.assertEqual(revenue_with_one_order(["10", "20"]), Decimal("45"))

    def test_only_latest_three_determine_extra_order(self):
        # Imported total 160; latest-three average 20; scenario 180.
        self.assertEqual(revenue_with_one_order(["30", "20", "10", "100"]), Decimal("180"))

    def test_decimal_precision(self):
        self.assertEqual(revenue_with_one_order(["0.10", "0.20"]), Decimal("0.45"))

    def test_nonfinite_values_are_rejected(self):
        for value in ["NaN", "Infinity", "-Infinity"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                revenue_with_one_order([value])

    def test_active_chart_displays_scenario_and_explains_assumption(self):
        st = MagicMock()
        st.columns.return_value = [MagicMock(), MagicMock()]
        chart = MagicMock()
        header = MagicMock()
        cards = MagicMock()
        render = load_function("dashboard/app.py", "render_forecast_intelligence", {
            "st": st, "pd": pd, "section_header": header,
            "render_static_bar_chart": chart, "render_metric_card": cards,
            "vertical_spacer": MagicMock(), "render_forecast_section_stable": MagicMock(),
            "render_executive_radar": MagicMock(),
        })
        render({"shopify_total_revenue": 160, "shopify_forecast_revenue": 180,
                "forecast_growth": 12.5, "shopify_best_category": "A",
                "shopify_risk_category": "B"})
        frame = chart.call_args.args[0]
        self.assertEqual(frame["vendas"].tolist(), [160, 180])
        self.assertEqual(frame["setor"].tolist(),
                         ["Imported revenue", "With one hypothetical order"])
        self.assertIn("not an AI forecast", header.call_args.args[2])
        self.assertIn("3 latest", header.call_args.args[2])

    def test_legacy_component_has_no_fabricated_months_or_growth(self):
        import math
        st = MagicMock()
        render = load_function("dashboard/sections/forecast_section.py",
                               "render_forecast_section", {"st": st, "math": math})
        self.assertIsNone(render(123, "A", "B", lambda v: f"R$ {v:.2f}"))
        st.metric.assert_called_once_with("Média de referência", "R$ 123.00")
        st.plotly_chart.assert_not_called()

    def test_missing_reference_is_not_presented_as_zero(self):
        import math
        for value in [None, "invalid", float("nan"), float("inf")]:
            with self.subTest(value=value):
                st = MagicMock()
                render = load_function("dashboard/sections/forecast_section.py",
                                       "render_forecast_section", {"st": st, "math": math})
                self.assertIsNone(render(value, "A", "B", str))
                st.metric.assert_not_called()
                st.info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
