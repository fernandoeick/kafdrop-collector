#!/bin/bash
nohup java --add-opens=java.base/sun.nio.ch=ALL-UNNAMED -jar kafdrop.jar --kafka.brokerConnect=b-1.demo-cluster.yjztqg.c14.kafka.us-east-1.amazonaws.com:9094,b-4.demo-cluster.yjztqg.c14.kafka.us-east-1.amazonaws.com:9094,b-3.demo-cluster.yjztqg.c14.kafka.us-east-1.amazonaws.com:9094 &
