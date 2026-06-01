#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <number-of-data-lines>" >&2
  exit 1
fi

line_count="$1"

if ! [[ "$line_count" =~ ^[0-9]+$ ]] || [[ "$line_count" -lt 1 ]]; then
  echo "Error: <number-of-data-lines> must be a positive integer." >&2
  exit 1
fi

output_file="/Users/mathiasnikkel/Documents/UTFPR/dissertacao/projetos-etl/file.csv"
header='name,datetime,tempmax,tempmin,temp,feelslikemax,feelslikemin,feelslike,dew,humidity,precip,precipprob,precipcover,preciptype,snow,snowdepth,windgust,windspeed,winddir,sealevelpressure,cloudcover,visibility,solarradiation,solarenergy,uvindex,severerisk,sunrise,sunset,moonphase,conditions,description,icon,stations'
data_line='"-25.4607,-49.2785",2026-02-16,85.9,66.6,72.9,89.1,66.6,73.5,67,84.2,0.226,100,50,rain,0,0,16.8,14.3,335.7,1018.5,68.7,8.3,240.4,20.7,10,30,2026-02-16T06:03:39,2026-02-16T18:58:26,0.97,"Rain, Partially cloudy",Partly cloudy throughout the day with storms possible.,rain,"SBBI,SBCT"'

{
  printf '%s\n' "$header"
  for ((i = 0; i < line_count; i++)); do
    printf '%s\n' "$data_line"
  done
} > "$output_file"

scp -i ~/.ssh/etl-aws "$output_file" ssm-user@3.83.11.14:/home/ssm-user/projetos-etl/java-etl/test.csv
scp -i ~/.ssh/etl-aws "$output_file" ssm-user@3.93.40.45:/home/ssm-user/projetos-etl/haskell-etl/test.csv
