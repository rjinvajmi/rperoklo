---
# 0.5 - API
# 2 - Release
# 3 - Contributing
# 5 - Template Page
# 10 - Default
search:
  boost: 10
---

# Prometheus

[**Prometheus**](https://prometheus.io/){.external-link target="_blank"} is an open-source monitoring and alerting toolkit originally built at SoundCloud.
With a focus on reliability, robustness, and easy scalability, **Prometheus** allows users to collect metrics,
scrape data from various sources, store them efficiently, and query them in real-time. Its flexible data model,
powerful query language, and seamless integration with [**Grafana**](https://grafana.com/){.external-link target="_blank"} make it a popular choice for monitoring the health
and performance of systems and applications.

### FastStream Metrics

To add a metrics to your broker, you need to:

1. Install `FastStream` with `prometheus-client`

    ```shell
    pip install faststream[prometheus]
    ```

2. Add `PrometheusMiddleware` to your broker

{!> includes/getting_started/prometheus/1.md !}

### Exposing the `/metrics` endpoint
The way Prometheus works requires the service to expose an HTTP endpoint for analysis.
By convention, this is a GET endpoint, and its path is usually `/metrics`.

FastStream's built-in **ASGI** support allows you to expose endpoints in your application.

A convenient way to serve this endpoint is to use `make_asgi_app` from `prometheus_client`,
passing in the registry that was passed to `PrometheusMiddleware`.

{!> includes/getting_started/prometheus/2.md !}

---

### Exported metrics

{% set received_messages_total_description = 'The metric is incremented each time the application receives a message.<br/><br/>This is necessary to count messages that the application has received but has not yet started processing.' %}
{% set received_messages_size_bytes_description = 'The metric is filled with the sizes of received messages. When a message is received, the size of its body in bytes is calculated and written to the metric.<br/><br/>Useful for analyzing the sizes of incoming messages, also in cases when the application receives messages of unexpected sizes.' %}
{% set received_messages_in_process_description = 'The metric is incremented when the message processing starts and decremented when the processing ends.<br/><br/>It is necessary to count the number of messages that the application processes.<br/><br/>Such a metric will help answer the question: _`is there a need to scale the service?`_' %}
{% set received_processed_messages_total_description = 'The metric is incremented after a message is processed, regardless of whether the processing ended with a success or an error.<br/><br/>This metric allows you to analyze the number of processed messages and their statuses.' %}
{% set received_processed_messages_duration_seconds_description = 'The metric is filled with the message processing time regardless of whether the processing ended with a success or an error.<br/><br/>Time stamps are recorded just before and immediately after the processing.<br/><br/>Then the metric is filled with their difference (in seconds).' %}
{% set received_processed_messages_exceptions_total_description = 'The metric is incremented if any exception occurred while processing a message (except `AckMessage`, `NackMessage`, `RejectMessage` and `SkipMessage`).<br/><br/>It can be used to draw conclusions about how many and what kind of exceptions occurred while processing messages.' %}
{% set published_messages_total_description = 'The metric is incremented when messages are sent, regardless of whether the sending was successful or not.' %}
{% set published_messages_duration_seconds_description = 'The metric is filled with the time the message was sent, regardless of whether the sending was successful or failed.<br/><br/>Timestamps are written immediately before and immediately after sending.<br/><br/>Then the metric is filled with their difference (in seconds).' %}
{% set published_messages_exceptions_total_description = 'The metric increases if any exception occurred while sending a message.<br/><br/>You can draw conclusions about how many and what exceptions occurred while sending messages.' %}


| Metric                                           | Type          | Description                                                    | Labels                                                |
|--------------------------------------------------|---------------|----------------------------------------------------------------|-------------------------------------------------------|
| **received_messages_total**                      | **Counter**   | {{ received_messages_total_description }}                      | `app_name`, `broker`, `handler`                       |
| **received_messages_size_bytes**                 | **Histogram** | {{ received_messages_size_bytes_description }}                 | `app_name`, `broker`, `handler`                       |
| **received_messages_in_process**                 | **Gauge**     | {{ received_messages_in_process_description }}                 | `app_name`, `broker`, `handler`                       |
| **received_processed_messages_total**            | **Counter**   | {{ received_processed_messages_total_description }}            | `app_name`, `broker`, `handler`, `status`             |
| **received_processed_messages_duration_seconds** | **Histogram** | {{ received_processed_messages_duration_seconds_description }} | `app_name`, `broker`, `handler`                       |
| **received_processed_messages_exceptions_total** | **Counter**   | {{ received_processed_messages_exceptions_total_description }} | `app_name`, `broker`, `handler`, `exception_type`     |
| **published_messages_total**                     | **Counter**   | {{ published_messages_total_description }}                     | `app_name`, `broker`, `destination`, `status`         |
| **published_messages_duration_seconds**          | **Histogram** | {{ published_messages_duration_seconds_description }}          | `app_name`, `broker`, `destination`                   |
| **published_messages_exceptions_total**          | **Counter**   | {{ published_messages_exceptions_total_description }}          | `app_name`, `broker`, `destination`, `exception_type` |

### Labels

| Label                             | Description                                                     | Values                                            |
|-----------------------------------|-----------------------------------------------------------------|---------------------------------------------------|
| app_name                          | The name of the application, which the user can specify himself | `faststream` by default                           |
| broker                            | Broker name                                                     | `kafka`, `rabbit`, `nats`, `redis`                |
| handler                           | Where the message came from                                     |                                                   |
| status (while receiving)          | Message processing status                                       | `acked`, `nacked`, `rejected`, `skipped`, `error` |
| exception_type (while receiving)  | Exception type when processing message                          |                                                   |
| status (while publishing)         | Message publishing status                                       | `success`, `error`                                |
| destination                       | Where the message is sent                                       |                                                   |
| exception_type (while publishing) | Exception type when publishing message                          |                                                   |

### Grafana dashboard

You can import the [**Grafana dashboard**](https://grafana.com/grafana/dashboards/22130-faststream-metrics/){.external-link target="_blank"} to visualize the metrics collected by middleware.

Enter the dashboard **URL** `https://grafana.com/grafana/dashboards/22130-faststream-metrics/` (or just the **ID**, `22130`), and click on **Load**.

![HTML-page](../../../assets/img/import-dashboard.png){ .on-glb loading=lazy }
`Import dashboard`

An [example](https://github.com/draincoder/faststream-monitoring){.external-link target="_blank"} application with configured **metrics**, **Prometheus** and **Grafana**.

![HTML-page](../../../assets/img/grafana-dashboard.png){ .on-glb loading=lazy }
`Grafana dashboard`
