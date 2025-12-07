#!/bin/sh

LOG_FILE="/var/log/container_stats.json"

echo "Starting monitoring..."

# Function to collect stats
collect_stats() {
    # Get stats for all running containers in JSON format
    # format: {"container":"{{.Name}}","cpu":"{{.CPUPerc}}","mem":"{{.MemUsage}}"}
    timestamp=$(date +%s)
    
    # We use docker stats --no-stream to get a snapshot
    # simple bash way: replace newline with comma using tr
    # We strip the trailing comma if present
    stats_array=$(echo "$stats" | tr '\n' ',' | sed 's/,$//')
    
    # Wrap in specific structure structure
    echo "{\"timestamp\": $timestamp, \"stats\": [$stats_array]}"
}

if [ "$1" = "live" ]; then
    echo "Check docker connection..."
    # Debug info
    # Debug info (keep it for now, valuable if it fails again)
    echo "--- Debug Info ---" > /var/log/debug.txt
    docker version >> /var/log/debug.txt 2>&1
    docker ps >> /var/log/debug.txt 2>&1
    
    echo "Starting monitoring loop..."

    while true; do
        # Collect raw stats using a robust format: Name|CPU|Mem
        # specific for parsing in Python. 
        # We write to a temp file then move to ensure atomicity.
        
        docker stats --no-stream --format "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}" > $LOG_FILE.tmp 2>>/var/log/debug.txt
        
        if [ -s $LOG_FILE.tmp ]; then
            mv $LOG_FILE.tmp $LOG_FILE
        else
            echo "$(date): Empty stats output" >> /var/log/debug.txt
        fi
        
        # Fast update for "Live" feel
        sleep 1
    done
else
    # One-off run
    docker stats --no-stream --format "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}"
fi
