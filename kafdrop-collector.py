import requests
import json
import sys

kafdropAddress = sys.argv[1]
brokerMetrics = {}

def readAllBrokers():
    brokers = requests.get(kafdropAddress + "broker")
    allBrokers = json.loads(brokers.text)
    
    if allBrokers:
        for idx, broker in enumerate(allBrokers):
            brokerId = str(broker['id'])
            if brokerId:
                requestURL = kafdropAddress + "broker/" + brokerId
                brokersJson = requests.get(requestURL, headers={'accept': 'application/json'})
                brokersText = json.loads(brokersJson.text)
                brokerMetric = ({"brokerId": brokerId, "topicsName": [], "partitionIds": {}, "topicPartitions" : 0, "partitionsReplicas" : 0, "host" : broker['host'], "rack" : broker['rack']})
                brokerMetrics[idx] = brokerMetric
    else:
        print("No brokers were found!")

def readTopicsAndPartitions():
    topics = requests.get(kafdropAddress +  "topic")
    allTopics = json.loads(topics.text)

    if allTopics:
        for topic in allTopics:
            topicName = str(topic['name'])

            #if not(topicName.startswith("__")):
            requestURL = kafdropAddress +  "topic/" + topicName
            topicDetails = requests.get(requestURL, headers={'accept': 'application/json'})
            topicDetailsResult = json.loads(topicDetails.text)
            partitions = topicDetailsResult['partitions']

            for partition in partitions:
                partitionId = str(partition['id'])
                leader = partition['leader']
                leaderId = str(leader['id'])   
                    
                idx = getIdx(leaderId)
                brokerMetrics[idx]["topicPartitions"] = brokerMetrics[idx]["topicPartitions"] + 1
                lastPartitionPosition = len(brokerMetrics[idx]["partitionIds"])
                brokerMetrics[idx]["partitionIds"][lastPartitionPosition] = partitionId
                
                if(topicName not in brokerMetrics[idx]["topicsName"]):
                    lastTopicNamePosition = len(brokerMetrics[idx]["topicsName"])
                    brokerMetrics[idx]["topicsName"].insert(lastTopicNamePosition, topicName)

                replicas = partition['replicas']
                for replica in replicas:
                    brokerId = str(replica['id'])
                    idx = getIdx(brokerId)
                    brokerMetrics[idx]["partitionsReplicas"] = brokerMetrics[idx]["partitionsReplicas"] + 1

    else:
        print("No topics were found!")

def getIdx(brokerIdToFind):
    for idx, metricDict in brokerMetrics.items():
        brokerId = brokerMetrics[idx]["brokerId"]
        if(brokerId == brokerIdToFind):
            return idx

def printMetrics():
    for idx, metricDict in brokerMetrics.items():
        brokerId = brokerMetrics[idx]["brokerId"]
        topicNames = brokerMetrics[idx]["topicsName"]
        host = brokerMetrics[idx]["host"]
        rack = brokerMetrics[idx]["rack"]

        metricExpression = "aws.kafka.kafdrop.broker_topics: "
        metricExpression = metricExpression + str(len(topicNames)) + "; broker_id: " + brokerId + ", cluster_hostname: " + host + ", availability_zone: " + rack
        print(metricExpression)

    for idx, metricDict in brokerMetrics.items():
        brokerId = brokerMetrics[idx]["brokerId"]
        topicPartitions = brokerMetrics[idx]["topicPartitions"]
        host = brokerMetrics[idx]["host"]
        rack = brokerMetrics[idx]["rack"]

        metricExpression = "aws.kafka.kafdrop.broker_partition: "
        metricExpression = metricExpression + str(topicPartitions) + "; broker_id: " + brokerId + ", cluster_hostname: " + host + ", availability_zone: " + rack
        print(metricExpression)


    for idx, metricDict in brokerMetrics.items():
        brokerId = brokerMetrics[idx]["brokerId"]
        partitionsReplicas = brokerMetrics[idx]["partitionsReplicas"]
        host = brokerMetrics[idx]["host"]
        rack = brokerMetrics[idx]["rack"]

        metricExpression = "aws.kafka.kafdrop.broker_partition_replicas: "
        metricExpression = metricExpression + str(partitionsReplicas) + "; broker_id: " + brokerId + ", cluster_hostname: " + host + ", availability_zone: " + rack
        print(metricExpression)

def printMessagesByTopicMetric():
    topics = requests.get(kafdropAddress +  "topic")
    allTopics = json.loads(topics.text)
    for topic in allTopics:
        topicName = str(topic['name'])
        if not(topicName.startswith("__")):
            metricExpression = "aws.kafka.kafdrop.topic_messages: "
            topicName = str(topic['name'])
            requestURL = kafdropAddress +  "topic/" + topicName + "/messages"
            messagesJson = requests.get(requestURL, headers={'accept': 'application/json'})
            messagesText = json.loads(messagesJson.text)
            lastOffSet = messagesText[0]['lastOffset']

            metricExpression = "aws.kafka.kafdrop.topic_messages: "
            metricExpression = metricExpression + str(lastOffSet) + "; topic_name: " + topicName + ", cluster_hostname: " + "" + ", availability_zone: " + ""
            print(metricExpression)

def main():
    readAllBrokers()
    readTopicsAndPartitions()
    printMetrics()
    printMessagesByTopicMetric()
    
if __name__ == "__main__":
    main()
