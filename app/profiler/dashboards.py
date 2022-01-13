from .metrics import Metric
from typing import List


class Dashboard(object):
    def __init__(self):
        self.metrics = []

    def add_metrics(self, metric: List[Metric]):
        if isinstance(metric, list):
            self.metrics.extend(metric)
        elif isinstance(metric, Metric):
            self.metrics.append(metric)
        else:
            raise ValueError("Please pass either a Metric of a list of Metrics")

    def calculate_all_metrics(self):
        for m in self.metrics:
            m()

    def calculate_dashboard(self):
        """
        can be overridden for specific dashboard types' requirements
        """
        self.calculate_all_metrics()

    def print_all_results(self):
        for m in self.metrics:
            print(m.get_result())


class StandardDashboard(Dashboard):
    """
    Each type of dashboard is defined as a specific set of metrics. Each metric must have a specific return type (eg table, single integer, )
    """

    def __init__(
        self,
        column_views: Metric,
        data_rules: Metric,
        anomaly_detect: Metric,
        extract_bad_postcode: Metric,
        ml_address: Metric,
        headline_metrics: List[Metric],
        ml_client_notes: Metric,
    ):
        super().__init__()
        self.headline_metrics = headline_metrics
        self.column_views = column_views
        self.anomaly_detect = anomaly_detect
        self.extract_bad_postcode = extract_bad_postcode
        self.ml_address = ml_address
        self.ml_client_notes = ml_client_notes
        self.data_rules = data_rules
        self.add_metrics(
            [
                column_views,
                data_rules,
                anomaly_detect,
                extract_bad_postcode,
                ml_address,
                *headline_metrics,
                ml_client_notes,
            ]
        )
        self.headline_metric_labels = []
        self.headline_metric_icons = []
        self.headline_metric_results = []
        self.headline_metric_colours = []

    def populate_headline_metrics(self):
        for m in self.headline_metrics:
            label = m.get_label()
            icon = m.get_icon()
            colour = m.get_colour()
            result = m.get_result()
            if isinstance(label, list):
                self.headline_metric_labels.extend(label)
                self.headline_metric_icons.extend(icon)
                self.headline_metric_results.extend(result)
                self.headline_metric_colours.extend(colour)
            else:
                self.headline_metric_labels.append(label)
                self.headline_metric_icons.append(icon)
                self.headline_metric_colours.append(colour)
                self.headline_metric_results.append(result)
        if not (
            len(self.headline_metric_labels)
            == len(self.headline_metric_results)
            == len(self.headline_metric_icons)
            == len(self.headline_metric_colours)
        ):
            raise ValueError("labels,results and icons lists should be the same length")

    def prepare_column_views(self):
        self.column_names = self.column_views.data_source.get_column_names()

    def get_column_names(self):
        return self.column_names

    def calculate_dashboard(self):
        self.calculate_all_metrics()
        self.populate_headline_metrics()
        self.prepare_column_views()

    def get_headline_metrics(self):
        return (
            self.headline_metric_results,
            self.headline_metric_labels,
            self.headline_metric_icons,
            self.headline_metric_colours,
        )

    def get_columnwise_view(self, col_name):
        return self.column_views.get_result_for_column(col_name)

    def get_tabular_view(self):
        return self.column_views.get_tabular_view()

    def get_targets_view(self):
        return self.column_views.get_targets_view()

    def get_anomaly_view(self):
        return self.anomaly_detect.get_result()

    def get_ml_address_view(self):
        return self.ml_address.get_result()

    def get_postcode_view(self):
        return self.extract_bad_postcode.get_result()

    def get_data_rules_view(self):
        return self.data_rules.get_result()

    def get_client_notes_view(self):
        return self.ml_client_notes.get_result()
