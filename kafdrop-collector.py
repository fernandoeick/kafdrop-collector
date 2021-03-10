import requests
import json
import sys

Kafdrop = sys.argv[1]

topicPartitionsDict = {}
topicReplicasDict = {}
topicDict = {}

def readAllBrokers():
    brokers = requests.get(Kafdrop + "broker")
    allBrokers = json.loads(brokers.text)
    if allBrokers:
        for idx, broker in enumerate(allBrokers):
            brokerId = str(broker['id'])
            if brokerId:
                requestURL = Kafdrop + "broker/" + brokerId
                brokersJson = requests.get(requestURL, headers={'accept': 'application/json'})
                brokersText = json.loads(brokersJson.text)
                topicReplicasDict.update({brokerId : 0})
                topicPartitionsDict.update({brokerId : 0})
                topicDict.update({brokerId : 0})
    else:
        print("No brokers were found!")

def readTopicsAndPartitions():
    topics = requests.get(Kafdrop +  "topic")
    allTopics = json.loads(topics.text)
    if allTopics:
        for topic in allTopics:
            leaderId = ""
            topicName = str(topic['name'])
            if not(topicName.startswith("__")):
                requestURL = Kafdrop +  "topic/" + topicName
                topicDetails = requests.get(requestURL, headers={'accept': 'application/json'})
                topicDetailsResult = json.loads(topicDetails.text)
                partitions = topicDetailsResult['partitions']

                for partition in partitions:
                    partitionId = str(partition['id'])
                    leader = partition['leader']
                    leaderId = str(leader['id'])   
                    replicas = partition['replicas']
                    topicPartitionsDict.update({leaderId : topicPartitionsDict[leaderId]+1})
                    for replica in replicas:
                        brokerId = str(replica['id'])
                        topicReplicasDict.update({brokerId : topicReplicasDict[brokerId]+1})

                    topicDict.update({leaderId : topicPartitionsDict[leaderId]+1})
    else:
        print("No topics were found!")

def printReplicasByBroker():
    for key, value in topicReplicasDict.items():
        metricExpression = "aws.kafka.kafdrop.topic_replicas: "
        metricExpression = metricExpression + str(value) + "; broker_id: " + key + ", cluster_name: " + "xpto" + ", env: " + "xpto" + ", region: " + "xpto" + ", availability_zone: " + "xpto"
        print(metricExpression)

def printPartitionsByBroker():
    for key, value in topicPartitionsDict.items():
        metricExpression = "aws.kafka.kafdrop.topic_partitions: "
        metricExpression = metricExpression + str(value) + "; broker_id: " + key + ", cluster_name: " + "xpto" + ", env: " + "xpto" + ", region: " + "xpto" + ", availability_zone: " + "xpto"
        print(metricExpression)

def printTopicsByBroker():
    for key, value in topicDict.items():
        metricExpression = "aws.kafka.kafdrop.broker_topics: "
        metricExpression = metricExpression + str(value) + "; broker_id: " + key + ", cluster_name: " + "xpto" + ", env: " + "xpto" + ", region: " + "xpto" + ", availability_zone: " + "xpto"
        print(metricExpression)

def printMessagesByTopic():
    topics = requests.get(Kafdrop +  "topic")
    allTopics = json.loads(topics.text)
    for topic in allTopics:
        topicName = str(topic['name'])
        if not(topicName.startswith("__")):
            metricExpression = "aws.kafka.kafdrop.topic_messages: "
            topicName = str(topic['name'])
            requestURL = Kafdrop +  "topic/" + topicName + "/messages"
            messagesJson = requests.get(requestURL, headers={'accept': 'application/json'})
            messagesText = json.loads(messagesJson.text)
            lastOffSet = messagesText[0]['lastOffset']
            metricExpression = metricExpression + str(lastOffSet)  + "; topic_name: " + topicName + ", cluster_name: " + "xpto" + ", env: " + "xpto" + ", region: " + "xpto" + ", availability_zone: " + "xpto"
            print(metricExpression)

def main():
    readAllBrokers()
    readTopicsAndPartitions()
    printReplicasByBroker()
    printPartitionsByBroker()
    printTopicsByBroker()
    printMessagesByTopic()

if __name__ == "__main__":
    main()
