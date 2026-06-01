  aws cloudwatch get-metric-data \
    --region us-east-1 \
    --start-time "2026-04-23T14:12:00Z" \
    --end-time "2026-04-23T14:16:00Z" \
    --metric-data-queries '[
      {
        "Id": "java_mem_max",
        "MetricStat": {
          "Metric": {
            "Namespace": "mestrado-etl",
            "MetricName": "mem_used_percent",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-07d9247870bc7b12e"}]
          },
          "Period": 60,
          "Stat": "Maximum"
        },
        "Label": "java mem max"
      },
      {
        "Id": "java_mem_avg",
        "MetricStat": {
          "Metric": {
            "Namespace": "mestrado-etl",
            "MetricName": "mem_used_percent",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-07d9247870bc7b12e"}]
          },
          "Period": 60,
          "Stat": "Average"
        },
        "Label": "java mem avg"
      },
      {
        "Id": "java_cpu_avg",
        "MetricStat": {
          "Metric": {
            "Namespace": "AWS/EC2",
            "MetricName": "CPUUtilization",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-07d9247870bc7b12e"}]
          },
          "Period": 60,
          "Stat": "Average"
        },
        "Label": "java cpu avg"
      },
      {
        "Id": "java_net_in_avg",
        "MetricStat": {
          "Metric": {
            "Namespace": "AWS/EC2",
            "MetricName": "NetworkIn",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-07d9247870bc7b12e"}]
          },
          "Period": 60,
          "Stat": "Average"
        },
        "Label": "java net in avg"
      },
      {
        "Id": "java_net_out_avg",
        "MetricStat": {
          "Metric": {
            "Namespace": "AWS/EC2",
            "MetricName": "NetworkOut",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-07d9247870bc7b12e"}]
          },
          "Period": 60,
          "Stat": "Average"
        },
        "Label": "java net out avg"
      },
      {
        "Id": "haskell_mem_max",
        "MetricStat": {
          "Metric": {
            "Namespace": "mestrado-etl",
            "MetricName": "mem_used_percent",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-0c54cef44d7ac9941"}]
          },
          "Period": 60,
          "Stat": "Maximum"
        },
        "Label": "haskell mem max"
      },
      {
        "Id": "haskell_mem_avg",
        "MetricStat": {
          "Metric": {
            "Namespace": "mestrado-etl",
            "MetricName": "mem_used_percent",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-0c54cef44d7ac9941"}]
          },
          "Period": 60,
          "Stat": "Average"
        },
        "Label": "haskell mem avg"
      },
      {
        "Id": "haskell_cpu_avg",
        "MetricStat": {
          "Metric": {
            "Namespace": "AWS/EC2",
            "MetricName": "CPUUtilization",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-0c54cef44d7ac9941"}]
          },
          "Period": 60,
          "Stat": "Average"
        },
        "Label": "haskell cpu avg"
      },
      {
        "Id": "haskell_net_in_avg",
        "MetricStat": {
          "Metric": {
            "Namespace": "AWS/EC2",
            "MetricName": "NetworkIn",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-0c54cef44d7ac9941"}]
          },
          "Period": 60,
          "Stat": "Average"
        },
        "Label": "haskell net in avg"
      },
      {
        "Id": "haskell_net_out_avg",
        "MetricStat": {
          "Metric": {
            "Namespace": "AWS/EC2",
            "MetricName": "NetworkOut",
            "Dimensions": [{"Name": "InstanceId", "Value": "i-0c54cef44d7ac9941"}]
          },
          "Period": 60,
          "Stat": "Average"
        },
        "Label": "haskell net out avg"
      }
    ]'