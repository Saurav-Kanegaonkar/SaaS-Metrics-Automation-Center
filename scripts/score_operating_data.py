import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
SRC = ROOT / "src"
random.seed(17)


def clamp(value, low, high):
    return max(low, min(high, value))


def money(value):
    return int(round(value, 0))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


segments = {
    "SMB": {"arr": 42000, "flows": 6, "runs": 950},
    "Mid-Market": {"arr": 135000, "flows": 13, "runs": 2200},
    "Enterprise": {"arr": 360000, "flows": 27, "runs": 5200},
    "Strategic": {"arr": 780000, "flows": 46, "runs": 9800},
}

industries = [
    "Ecommerce",
    "Financial operations",
    "SaaS operations",
    "Healthcare operations",
    "Manufacturing",
    "Retail supply chain",
]
regions = ["North America", "EMEA", "APAC"]
stages = ["Onboarding", "Adoption", "Scale", "Renewal"]
maturity = ["Starter", "Managed", "Optimized"]
systems = ["ERP", "CRM", "Data warehouse", "Commerce", "Support", "Finance"]
flow_names = [
    "order to cash",
    "usage to warehouse",
    "case to renewal",
    "invoice to ERP",
    "lead to opportunity",
    "inventory to commerce",
    "subscription to finance",
    "ticket to health score",
]

accounts = []
for i in range(1, 46):
    segment = random.choices(
        list(segments), weights=[0.23, 0.35, 0.27, 0.15], k=1
    )[0]
    profile = segments[segment]
    maturity_level = random.choices(maturity, weights=[0.27, 0.43, 0.30], k=1)[0]
    arr = profile["arr"] * random.uniform(0.72, 1.42)
    accounts.append(
        {
            "account_id": f"ACC{i:03d}",
            "account_name": f"Account {i:03d}",
            "segment": segment,
            "industry": random.choice(industries),
            "region": random.choice(regions),
            "arr": money(arr),
            "lifecycle_stage": random.choice(stages),
            "owner_team": random.choice(["Revenue", "Product", "Customer Success", "Operations"]),
            "implementation_maturity": maturity_level,
            "primary_system": random.choice(systems),
            "base_flows": profile["flows"] + random.randint(-2, 5),
            "base_runs": profile["runs"] + random.randint(-250, 500),
            "risk_bias": random.uniform(-0.025, 0.045),
            "adoption_bias": random.uniform(-0.18, 0.22),
        }
    )

incident_accounts = {"ACC007", "ACC014", "ACC026", "ACC038", "ACC041"}
growth_accounts = {"ACC003", "ACC011", "ACC020", "ACC029", "ACC044"}
start = date(2026, 1, 1)
days = 90
daily_rows = []
events = []

for day_index in range(days):
    current = start + timedelta(days=day_index)
    weekday_factor = 0.88 if current.weekday() >= 5 else 1.0
    seasonality = 1 + 0.05 * math.sin(day_index / 9)
    for account in accounts:
        flow_base = account["base_flows"]
        run_base = account["base_runs"]
        active_flows = max(2, int(random.gauss(flow_base, 2)))
        successful_runs = max(100, int(random.gauss(run_base * weekday_factor * seasonality, run_base * 0.08)))
        incident_lift = 0.035 if account["account_id"] in incident_accounts and day_index > 48 else 0
        error_rate = clamp(
            0.014
            + account["risk_bias"]
            + incident_lift
            + random.gauss(0, 0.009),
            0.002,
            0.155,
        )
        failed_runs = int(successful_runs * error_rate / max(0.01, 1 - error_rate))
        p95_runtime = clamp(random.gauss(42 + error_rate * 430, 12), 18, 145)
        adoption_lift = 0.24 if account["account_id"] in growth_accounts and day_index > 35 else 0
        product_events = int(
            successful_runs
            * clamp(0.16 + account["adoption_bias"] + adoption_lift + random.gauss(0, 0.035), 0.04, 0.54)
        )
        dashboard_views = max(
            1,
            int(
                random.gauss(
                    9 + active_flows * 0.7 + (product_events / 650),
                    5,
                )
            ),
        )
        support_tickets = max(0, int(random.gauss(error_rate * 42 + failed_runs / 1700, 1.4)))
        data_quality_score = clamp(96 - error_rate * 230 - support_tickets * 1.9 + random.gauss(0, 3.5), 42, 99)
        freshness_hours = clamp(random.gauss(4 + error_rate * 80 + support_tickets * 1.5, 2.2), 1, 36)
        certified_coverage = clamp(
            78
            + (8 if account["implementation_maturity"] == "Optimized" else 0)
            - error_rate * 180
            + random.gauss(0, 5),
            38,
            98,
        )
        arr_at_risk = account["arr"] * clamp(error_rate * 1.7 + support_tickets * 0.012, 0, 0.42)
        expansion_signal = account["arr"] * clamp((product_events / max(1, successful_runs)) * 0.18, 0, 0.12)
        daily_rows.append(
            {
                "date": current.isoformat(),
                "account_id": account["account_id"],
                "active_flows": active_flows,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "error_rate": round(error_rate, 4),
                "p95_runtime_sec": round(p95_runtime, 1),
                "dashboard_views": dashboard_views,
                "product_events": product_events,
                "open_support_tickets": support_tickets,
                "arr_at_risk": money(arr_at_risk),
                "expansion_signal": money(expansion_signal),
                "data_quality_score": round(data_quality_score, 1),
                "metric_freshness_hours": round(freshness_hours, 1),
                "certified_metric_coverage": round(certified_coverage, 1),
            }
        )
        if random.random() < error_rate * 0.55:
            severity = random.choices(["Low", "Medium", "High"], weights=[0.55, 0.32, 0.13], k=1)[0]
            events.append(
                {
                    "event_id": f"EV{len(events) + 1:04d}",
                    "event_date": current.isoformat(),
                    "account_id": account["account_id"],
                    "flow_name": random.choice(flow_names),
                    "event_type": random.choice(
                        ["schema drift", "mapping exception", "late extract", "volume spike", "stakeholder request"]
                    ),
                    "severity": severity,
                    "estimated_impact": money(account["arr"] * random.uniform(0.006, 0.045)),
                    "status": random.choice(["Open", "Monitoring", "Resolved"]),
                }
            )

account_fields = [
    "account_id",
    "account_name",
    "segment",
    "industry",
    "region",
    "arr",
    "lifecycle_stage",
    "owner_team",
    "implementation_maturity",
    "primary_system",
]
write_csv(DATA / "entities.csv", [{k: row[k] for k in account_fields} for row in accounts], account_fields)

daily_fields = [
    "date",
    "account_id",
    "active_flows",
    "successful_runs",
    "failed_runs",
    "error_rate",
    "p95_runtime_sec",
    "dashboard_views",
    "product_events",
    "open_support_tickets",
    "arr_at_risk",
    "expansion_signal",
    "data_quality_score",
    "metric_freshness_hours",
    "certified_metric_coverage",
]
write_csv(DATA / "daily_metrics.csv", daily_rows, daily_fields)
write_csv(
    DATA / "source_events.csv",
    events,
    ["event_id", "event_date", "account_id", "flow_name", "event_type", "severity", "estimated_impact", "status"],
)

metric_rows = [
    ["Net ARR retention", "Revenue", "Finance Analytics", "Certified", 8, "contracts, invoices, subscriptions"],
    ["Expansion pipeline sourced", "Revenue", "GTM Analytics", "Draft", 12, "opportunities, product usage"],
    ["Active integration flows", "Product", "Product Analytics", "Certified", 4, "flow executions, account map"],
    ["Flow success rate", "Operations", "Data Engineering", "Certified", 2, "flow executions, exception logs"],
    ["AI assist adoption", "Product", "Product Analytics", "Draft", 12, "agent actions, user events"],
    ["Dashboard freshness SLA", "Analytics Ops", "Analytics", "Certified", 6, "dashboard runs, warehouse jobs"],
    ["Customer health risk", "Customer", "Customer Success Ops", "Needs owner", 12, "tickets, ARR, usage"],
    ["Support deflection", "Operations", "Support Ops", "Draft", 24, "cases, knowledge events"],
    ["Implementation maturity", "Customer", "Professional Services", "Certified", 24, "project milestones"],
    ["Self serve adoption", "Analytics Ops", "Analytics", "Certified", 12, "BI views, stakeholder map"],
    ["Data quality incident rate", "Analytics Ops", "Data Engineering", "Certified", 4, "test results, incidents"],
    ["Recurring reporting toil", "Analytics Ops", "Analytics", "Draft", 24, "requests, report catalog"],
]
metric_definitions = []
for name, domain, owner, status, sla, source_tables in metric_rows:
    quality = clamp(random.gauss(90 if status == "Certified" else 78, 8), 55, 99)
    freshness = clamp(random.gauss(sla * 0.85 if status == "Certified" else sla * 1.35, 4), 1, 42)
    blocker = "None"
    if status == "Draft":
        blocker = random.choice(["Needs grain decision", "Needs owner approval", "Needs edge case QA"])
    if status == "Needs owner":
        blocker = "Owner and definition conflict"
    metric_definitions.append(
        {
            "metric_name": name,
            "domain": domain,
            "owner": owner,
            "status": status,
            "freshness_sla_hours": sla,
            "current_freshness_hours": round(freshness, 1),
            "quality_score": round(quality, 1),
            "source_tables": source_tables,
            "certification_blocker": blocker,
        }
    )
write_csv(
    DATA / "metric_definitions.csv",
    metric_definitions,
    [
        "metric_name",
        "domain",
        "owner",
        "status",
        "freshness_sla_hours",
        "current_freshness_hours",
        "quality_score",
        "source_tables",
        "certification_blocker",
    ],
)

report_names = [
    "Weekly executive KPI digest",
    "Renewal risk packet",
    "Product usage expansion scan",
    "Integration error summary",
    "Finance ARR variance review",
    "Customer health exception list",
    "Implementation readiness readout",
    "Support friction review",
    "Self serve adoption digest",
    "AI assist adoption pulse",
    "Flow reliability escalation list",
    "Data quality incident review",
    "GTM account movement tracker",
    "Enterprise onboarding update",
    "Pipeline source reconciliation",
    "Dashboard freshness followup",
    "Metric ownership change log",
    "Operations SLA watchlist",
]
reporting_requests = []
for i, name in enumerate(report_names, 1):
    team = random.choice(["Executive Staff", "Revenue", "Product", "Customer Success", "Operations", "Finance"])
    manual_hours = round(random.uniform(1.5, 8.5), 1)
    reuse = round(random.uniform(42, 96), 1)
    quality = round(random.uniform(58, 97), 1)
    visibility = random.choice(["High", "Medium", "Low"])
    fit = round(clamp(manual_hours * 9 + reuse * 0.35 + quality * 0.25 + (18 if visibility == "High" else 6), 25, 100), 1)
    reporting_requests.append(
        {
            "request_id": f"REQ{i:03d}",
            "stakeholder_team": team,
            "report_name": name,
            "cadence": random.choice(["Weekly", "Biweekly", "Monthly"]),
            "manual_hours": manual_hours,
            "dashboard_reuse_score": reuse,
            "data_quality_score": quality,
            "executive_visibility": visibility,
            "ai_assist_fit": fit,
            "automation_readiness": round(clamp(fit * 0.55 + quality * 0.30 + reuse * 0.15, 20, 100), 1),
        }
    )
write_csv(
    DATA / "reporting_requests.csv",
    reporting_requests,
    [
        "request_id",
        "stakeholder_team",
        "report_name",
        "cadence",
        "manual_hours",
        "dashboard_reuse_score",
        "data_quality_score",
        "executive_visibility",
        "ai_assist_fit",
        "automation_readiness",
    ],
)

last_30 = [row for row in daily_rows if row["date"] >= (start + timedelta(days=60)).isoformat()]
by_account = defaultdict(list)
for row in last_30:
    by_account[row["account_id"]].append(row)

account_lookup = {row["account_id"]: row for row in accounts}
priority_queue = []
for account_id, rows in by_account.items():
    account = account_lookup[account_id]
    avg_error = sum(row["error_rate"] for row in rows) / len(rows)
    avg_quality = sum(row["data_quality_score"] for row in rows) / len(rows)
    avg_freshness = sum(row["metric_freshness_hours"] for row in rows) / len(rows)
    total_arr_risk = sum(row["arr_at_risk"] for row in rows)
    total_expansion = sum(row["expansion_signal"] for row in rows)
    total_tickets = sum(row["open_support_tickets"] for row in rows)
    avg_coverage = sum(row["certified_metric_coverage"] for row in rows) / len(rows)
    risk_score = clamp(avg_error * 620 + total_tickets * 0.18 + avg_freshness * 1.3, 0, 100)
    opportunity_score = clamp((total_expansion / max(1, account["arr"])) * 130 + avg_coverage * 0.38, 0, 100)
    trust_gap = clamp(100 - avg_quality + max(0, avg_freshness - 8) * 1.7 + max(0, 82 - avg_coverage) * 0.5, 0, 100)
    priority_score = clamp(risk_score * 0.45 + opportunity_score * 0.30 + trust_gap * 0.25, 0, 100)
    priority_queue.append(
        {
            "account_id": account_id,
            "segment": account["segment"],
            "owner_team": account["owner_team"],
            "avg_error_rate": round(avg_error, 4),
            "avg_quality_score": round(avg_quality, 1),
            "avg_freshness_hours": round(avg_freshness, 1),
            "certified_metric_coverage": round(avg_coverage, 1),
            "arr_at_risk": money(total_arr_risk),
            "expansion_signal": money(total_expansion),
            "risk_score": round(risk_score, 1),
            "opportunity_score": round(opportunity_score, 1),
            "trust_gap_score": round(trust_gap, 1),
            "priority_score": round(priority_score, 1),
        }
    )
priority_queue.sort(key=lambda row: row["priority_score"], reverse=True)
write_csv(
    OUTPUTS / "priority_queue.csv",
    priority_queue,
    [
        "account_id",
        "segment",
        "owner_team",
        "avg_error_rate",
        "avg_quality_score",
        "avg_freshness_hours",
        "certified_metric_coverage",
        "arr_at_risk",
        "expansion_signal",
        "risk_score",
        "opportunity_score",
        "trust_gap_score",
        "priority_score",
    ],
)
write_csv(
    OUTPUTS / "metric_certification_queue.csv",
    sorted(metric_definitions, key=lambda row: (row["status"] == "Certified", row["quality_score"])),
    [
        "metric_name",
        "domain",
        "owner",
        "status",
        "freshness_sla_hours",
        "current_freshness_hours",
        "quality_score",
        "source_tables",
        "certification_blocker",
    ],
)
write_csv(
    OUTPUTS / "automation_queue.csv",
    sorted(reporting_requests, key=lambda row: row["automation_readiness"], reverse=True),
    [
        "request_id",
        "stakeholder_team",
        "report_name",
        "cadence",
        "manual_hours",
        "dashboard_reuse_score",
        "data_quality_score",
        "executive_visibility",
        "ai_assist_fit",
        "automation_readiness",
    ],
)

actions = []
for i, row in enumerate(priority_queue[:24], 1):
    if row["trust_gap_score"] > row["opportunity_score"]:
        action = "Certify metric grain and freshness before self serve rollout"
        domain = "Metric trust"
    elif row["risk_score"] > 55:
        action = "Escalate integration reliability review with Data Engineering"
        domain = "Operations"
    else:
        action = "Create expansion analysis packet for stakeholder review"
        domain = "Revenue and product"
    actions.append(
        {
            "action_id": f"ACT{i:03d}",
            "account_id": row["account_id"],
            "domain": domain,
            "action_type": action,
            "rationale": f"Priority {row['priority_score']} from risk {row['risk_score']}, trust gap {row['trust_gap_score']}, and opportunity {row['opportunity_score']}.",
            "expected_value": money(row["arr_at_risk"] * 0.18 + row["expansion_signal"] * 0.22),
            "effort_hours": round(random.uniform(4, 18), 1),
            "owner": row["owner_team"],
            "priority_score": row["priority_score"],
        }
    )
write_csv(
    DATA / "recommended_actions.csv",
    actions,
    [
        "action_id",
        "account_id",
        "domain",
        "action_type",
        "rationale",
        "expected_value",
        "effort_hours",
        "owner",
        "priority_score",
    ],
)

summary = {
    "accounts": len(accounts),
    "dailyRows": len(daily_rows),
    "events": len(events),
    "arrMonitored": sum(row["arr"] for row in accounts),
    "avgQuality": round(sum(row["data_quality_score"] for row in last_30) / len(last_30), 1),
    "avgErrorRate": round(sum(row["error_rate"] for row in last_30) / len(last_30), 4),
    "certifiedMetrics": sum(1 for row in metric_definitions if row["status"] == "Certified"),
    "automationCandidates": sum(1 for row in reporting_requests if row["automation_readiness"] >= 75),
    "manualHours": round(sum(row["manual_hours"] for row in reporting_requests), 1),
}

app_data = {
    "summary": summary,
    "priorityQueue": priority_queue[:8],
    "metricQueue": sorted(metric_definitions, key=lambda row: (row["status"] == "Certified", row["quality_score"]))[:8],
    "automationQueue": sorted(reporting_requests, key=lambda row: row["automation_readiness"], reverse=True)[:8],
    "actions": actions[:6],
    "findings": [
        f"{priority_queue[0]['account_id']} is the highest priority account because risk, metric trust, and revenue exposure converge.",
        f"{summary['certifiedMetrics']} of {len(metric_definitions)} core metrics are certified, which makes the remaining draft metrics the main blocker to broader self serve reporting.",
        f"{summary['automationCandidates']} recurring reports clear the readiness threshold for AI assisted draft generation and analyst review.",
    ],
}
SRC.mkdir(exist_ok=True)
(SRC / "data.js").write_text("window.artifactData = " + json.dumps(app_data, indent=2) + ";\n")

legacy_summary = [
    {
        "dataset": "accounts",
        "rows": len(accounts),
        "purpose": "Synthetic customer and segment grain for revenue, product, and operations reporting.",
    },
    {
        "dataset": "daily_metrics",
        "rows": len(daily_rows),
        "purpose": "Daily integration flow, usage, support, quality, freshness, risk, and expansion signals.",
    },
    {
        "dataset": "source_events",
        "rows": len(events),
        "purpose": "Modeled exceptions such as schema drift, mapping failures, late extracts, and stakeholder requests.",
    },
]
write_csv(DATA / "synthetic_operating_data.csv", legacy_summary, ["dataset", "rows", "purpose"])
print(json.dumps(summary, indent=2))
