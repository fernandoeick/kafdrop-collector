#!/bin/bash
java --add-opens=java.base/sun.nio.ch=ALL-UNNAMED -jar /usr/local/bin/kafdrop/kafdrop.jar --kafka.brokerConnect=b-1.demo-cluster.ore1bz.c2.kafka.us-east-2.amazonaws.com:9094,b-2.demo-cluster.ore1bz.c2.kafka.us-east-2.amazonaws.com:9094 &> /var/log/kafdrop/kafdrop.log
