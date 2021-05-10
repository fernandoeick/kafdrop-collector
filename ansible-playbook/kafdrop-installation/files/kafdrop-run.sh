#!/bin/bash
/usr/lib/jvm/java-11-amazon-corretto.x86_64/bin/java --add-opens=java.base/sun.nio.ch=ALL-UNNAMED -jar /usr/local/bin/kafdrop/kafdrop.jar --kafka.brokerConnect=b-1.demo-cluster.ore1bz.c2.kafka.us-east-2.amazonaws.com:9094,b-2.demo-cluster.ore1bz.c2.kafka.us-east-2.amazonaws.com:9094 &> /var/log/kafdrop/kafdrop.log --topic.deleteEnabled=false --topic.createEnabled=false

#Makes kafdrop.service sent the following parameters to improve this script:
#$1 -> kafdrop_executable_location
#$2 -> msk_brokers
#$3 -> kafdrop_logs_location
#$4 -> kafdrop_enable_edition
#This parameters are already defined in defaults/main.yml
#usr/lib/jvm/java-11-amazon-corretto.x86_64/bin/java --add-opens=java.base/sun.nio.ch=ALL-UNNAMED -jar $1/kafdrop.jar --kafka.brokerConnect=$2 &> $3/kafdrop.log --topic.deleteEnabled=$4 --topic.createEnabled=$4