#!/bin/bash
java --add-opens=java.base/sun.nio.ch=ALL-UNNAMED -jar /usr/local/bin/kafdrop/kafdrop.jar --kafka.brokerConnect=b-2.demo-cluster.o3pz5h.c2.kafka.us-east-2.amazonaws.com:9094,b-3.demo-cluster.o3pz5h.c2.kafka.us-east-2.amazonaws.com:9094,b-4.demo-cluster.o3pz5h.c2.kafka.us-east-2.amazonaws.com:9094
