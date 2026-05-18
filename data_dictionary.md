# Data Dictionary

## `entities.csv`

- `account_id`: Synthetic account key.
- `segment`: SMB, mid-market, enterprise, or strategic.
- `arr`: Modeled annual recurring revenue.
- `owner_team`: Team accountable for the account signal.
- `implementation_maturity`: Starter, managed, or optimized operating maturity.

## `daily_metrics.csv`

- `active_flows`: Count of active integration or automation flows.
- `successful_runs`: Successful daily flow executions.
- `failed_runs`: Failed daily flow executions.
- `error_rate`: Failed runs divided by total runs.
- `p95_runtime_sec`: Modeled p95 execution runtime.
- `dashboard_views`: Daily self serve reporting usage.
- `product_events`: Daily product usage events.
- `open_support_tickets`: Daily support friction count.
- `arr_at_risk`: Modeled revenue exposure tied to reliability and support friction.
- `expansion_signal`: Modeled upside tied to adoption depth.
- `data_quality_score`: Composite source quality score from 0 to 100.
- `metric_freshness_hours`: Hours since the reporting metric was refreshed.
- `certified_metric_coverage`: Share of account facing metrics with certified definitions.

## `metric_definitions.csv`

- `status`: Certified, draft, or needs owner.
- `freshness_sla_hours`: Maximum acceptable data age for the metric.
- `quality_score`: Modeled quality score for the metric contract.
- `certification_blocker`: Reason the metric is not ready for broad self serve use.

## `reporting_requests.csv`

- `manual_hours`: Analyst hours currently spent per cycle.
- `dashboard_reuse_score`: How much the request can reuse governed dashboard logic.
- `ai_assist_fit`: Suitability for AI assisted SQL, narrative, or QA draft work.
- `automation_readiness`: Composite score used to rank reporting automation candidates.
