from app.profiler.data_sources import InMemoryDataSource
from app.profiler.tabular_readers import CSVReader
from app.profiler.metrics import (
    BasicProfile,
    TotalBlankCells,
    TotalRowsCols,
    DuplicateRows,
    DetectBadAddress,
    ExtractBadPostcode,
    GroupedZScore,
    SupervisedAnomalyDetection,
    ExtractDataRules,
    ExtractPIIAttributes,
    ClassifyClientNotes,
)
from app.profiler.dashboards import Dashboard, StandardDashboard


# Below script used for debugging/development. Users would run the code via web interface
if __name__ == "__main__":
    # Define data source type and data source - in this example we use an in-memory data source type derived from a csv
    bcm_data_source = InMemoryDataSource(
        CSVReader(r"app/files", "mortgage_data_v4.csv")
    )

    # Build dashboard object (which contains a collection of metrics)
    dashboard = StandardDashboard(
        BasicProfile(bcm_data_source),
        ExtractDataRules(bcm_data_source),
        GroupedZScore(
            bcm_data_source,
            {
                "id_col": "user_id",
                "group_key": "card_type",
                "group_value": "credit_rate",
            },
        ),
        ExtractBadPostcode(
            bcm_data_source, {"id_col": "user_id", "postcd_col": "PostCode"}
        ),
        DetectBadAddress(
            bcm_data_source, {"id_col": "user_id", "address_col": ["address", "city"]}
        ),
        [
            TotalBlankCells(bcm_data_source, {"pc": True}),
            TotalRowsCols(bcm_data_source),
            DuplicateRows(bcm_data_source),
            ExtractPIIAttributes(bcm_data_source),
        ],
        ClassifyClientNotes(
            bcm_data_source, {"id_col": "user_id", "notes_col": "client_notes"}
        ),
    )

    # calculate all the metrics on the dashboard
    dashboard.calculate_all_metrics()

    # print outputs (for debugging)
    dashboard.print_all_results()
