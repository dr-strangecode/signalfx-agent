<!--- GENERATED BY gomplate from scripts/docs/monitor-page.md.tmpl --->

# gitlab-sidekiq

This monitor scrapes the Gitlab Sidekiq Prometheus Exporter.  See the [Gitlab monitor](gitlab.md) for more information.


Monitor Type: `gitlab-sidekiq`

[Monitor Source Code](https://github.com/signalfx/signalfx-agent/tree/master/internal/monitors/gitlab)

**Accepts Endpoints**: **Yes**

**Multiple Instances Allowed**: Yes

## Configuration

| Config option | Required | Type | Description |
| --- | --- | --- | --- |
| `host` | **yes** | `string` | Host of the exporter |
| `port` | **yes** | `integer` | Port of the exporter |
| `username` | no | `string` | Basic Auth username to use on each request, if any. |
| `password` | no | `string` | Basic Auth password to use on each request, if any. |
| `useHTTPS` | no | `bool` | If true, the agent will connect to the exporter using HTTPS instead of plain HTTP. (**default:** `false`) |
| `skipVerify` | no | `bool` | If useHTTPS is true and this option is also true, the exporter's TLS cert will not be verified. (**default:** `false`) |
| `metricPath` | no | `string` | Path to the metrics endpoint on the exporter server, usually `/metrics` (the default). (**default:** `/metrics`) |
| `sendAllMetrics` | no | `bool` | Send all the metrics that come out of the Prometheus exporter without any filtering.  This option has no effect when using the prometheus exporter monitor directly since there is no built-in filtering, only when embedding it in other monitors. (**default:** `false`) |




## Metrics

The following table lists the metrics available for this monitor. Metrics that are marked as Included are standard metrics and are monitored by default.

| Name | Type | Included | Description |
| ---  | ---  | ---    | ---         |
| `gitlab_cache_misses_total` | cumulative |  |  |
| `gitaly_controller_action_duration_seconds_bucket` | cumulative |  |  |
| `gitaly_controller_action_duration_seconds_count` | cumulative |  |  |
| `gitaly_controller_action_duration_seconds` | cumulative |  |  |
| `gitlab_cache_operation_duration_seconds_bucket` | cumulative |  |  |
| `gitlab_cache_operation_duration_seconds_count` | cumulative |  |  |
| `gitlab_cache_operation_duration_seconds` | cumulative |  |  |
| `gitlab_repository_archive_clean_up_real_duration_seconds_bucket` | cumulative |  |  |
| `gitlab_repository_archive_clean_up_real_duration_seconds_count` | cumulative |  |  |
| `gitlab_repository_archive_clean_up_real_duration_seconds` | cumulative |  |  |
| `gitlab_sql_duration_seconds_bucket` | cumulative |  |  |
| `gitlab_sql_duration_seconds_count` | cumulative |  |  |
| `gitlab_sql_duration_seconds` | cumulative |  |  |
| `gitlab_transaction_sidekiq_queue_duration_total` | gauge | ✔ |  |
| `gitlab_transaction_cache_read_hit_count_total` | cumulative |  |  |
| `gitlab_transaction_cache_read_miss_count_total` | cumulative |  |  |
| `gitlab_transaction_duration_seconds_bucket` | cumulative |  |  |
| `gitlab_transaction_duration_seconds_count` | cumulative |  |  |
| `gitlab_transaction_duration_seconds` | cumulative |  |  |


To specify custom metrics you want to monitor, add a `metricsToInclude` filter
to the agent configuration, as shown in the code snippet below. The snippet
lists all available custom metrics. You can copy and paste the snippet into
your configuration file, then delete any custom metrics that you do not want
sent.

Note that some of the custom metrics require you to set a flag as well as add
them to the list. Check the monitor configuration file to see if a flag is
required for gathering additional metrics.

```yaml

metricsToInclude:
  - metricNames:
    - gitlab_cache_misses_total
    - gitaly_controller_action_duration_seconds_bucket
    - gitaly_controller_action_duration_seconds_count
    - gitaly_controller_action_duration_seconds
    - gitlab_cache_operation_duration_seconds_bucket
    - gitlab_cache_operation_duration_seconds_count
    - gitlab_cache_operation_duration_seconds
    - gitlab_repository_archive_clean_up_real_duration_seconds_bucket
    - gitlab_repository_archive_clean_up_real_duration_seconds_count
    - gitlab_repository_archive_clean_up_real_duration_seconds
    - gitlab_sql_duration_seconds_bucket
    - gitlab_sql_duration_seconds_count
    - gitlab_sql_duration_seconds
    - gitlab_transaction_cache_read_hit_count_total
    - gitlab_transaction_cache_read_miss_count_total
    - gitlab_transaction_duration_seconds_bucket
    - gitlab_transaction_duration_seconds_count
    - gitlab_transaction_duration_seconds
    monitorType: gitlab-sidekiq
```




