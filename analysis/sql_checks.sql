-- Account priority queue for a Snowflake style analytics mart.
with account_30d as (
  select
    account_id,
    avg(error_rate) as avg_error_rate,
    avg(data_quality_score) as avg_quality_score,
    avg(metric_freshness_hours) as avg_freshness_hours,
    avg(certified_metric_coverage) as certified_metric_coverage,
    sum(arr_at_risk) as arr_at_risk,
    sum(expansion_signal) as expansion_signal,
    sum(open_support_tickets) as support_ticket_days
  from analytics.daily_metrics
  where date >= dateadd(day, -30, current_date)
  group by 1
),
scored as (
  select
    account_id,
    avg_error_rate,
    avg_quality_score,
    avg_freshness_hours,
    certified_metric_coverage,
    arr_at_risk,
    expansion_signal,
    least(100, avg_error_rate * 620 + support_ticket_days * 0.18 + avg_freshness_hours * 1.3) as risk_score,
    least(100, (expansion_signal / nullif(arr_at_risk + expansion_signal, 0)) * 75 + certified_metric_coverage * 0.38) as opportunity_score,
    least(100, 100 - avg_quality_score + greatest(0, avg_freshness_hours - 8) * 1.7) as trust_gap_score
  from account_30d
)
select
  account_id,
  avg_error_rate,
  avg_quality_score,
  arr_at_risk,
  expansion_signal,
  risk_score,
  opportunity_score,
  trust_gap_score,
  risk_score * 0.45 + opportunity_score * 0.30 + trust_gap_score * 0.25 as priority_score
from scored
order by priority_score desc;

-- Metric certification contract for self serve reporting.
select
  metric_name,
  domain,
  owner,
  status,
  current_freshness_hours,
  freshness_sla_hours,
  quality_score,
  certification_blocker
from analytics.metric_definitions
where status != 'Certified'
   or current_freshness_hours > freshness_sla_hours
   or quality_score < 85
order by quality_score asc;

-- AI assisted report automation candidates.
select
  request_id,
  stakeholder_team,
  report_name,
  cadence,
  manual_hours,
  dashboard_reuse_score,
  data_quality_score,
  executive_visibility,
  ai_assist_fit,
  automation_readiness
from analytics.reporting_requests
where automation_readiness >= 75
order by automation_readiness desc;
