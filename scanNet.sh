#!/bin/bash
#To install lib. use-- sudo apt-get install parallel
#To change mode file to execute -- chmod +x scanNet.sh
#To run .sh -- ./scanNet.sh


ip_base="192.168.1"
port_range_start=1
port_range_end=1024

export -f check_service() {
  response="$1"
  if [[ $response == *"HTTP"* ]]; then
    echo "HTTP"
  elif [[ $response == *"SSH"* ]]; then
    echo "SSH"
  elif [[ $response == *"SMTP"* ]]; then
    echo "SMTP"
  else
    echo "Unknown"
  fi
}

export -f scan_ip_port() {
  ip="$1"
  port="$2"
  response=$(echo -e "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n" | nc -w 1 ${ip_base}.${ip} $port 2>/dev/null)
  
  if [ ! -z "$response" ]; then
    service=$(check_service "$response")
    echo "IP: ${ip_base}.${ip}, Port: $port, Service: $service"
  fi
}

export -f check_service
export -f scan_ip_port

parallel -j 100% --eta scan_ip_port {1} {2} ::: $(seq 1 254) ::: $(seq $port_range_start $port_range_end)
