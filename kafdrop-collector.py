import requests
import json
import sys

Kafdrop = sys.argv[1]
brokersSize = {}
brokersTopics = {}

def setBrokers():
    brokers = requests.get(Kafdrop + "broker")
    allBrokers = json.loads(brokers.text)
    
    if allBrokers:
        for broker in allBrokers:
            brokerId = str(broker['id'])
            if brokerId:
                requestURL = Kafdrop + "broker/" + brokerId
                brokerDetails = requests.get(requestURL, headers={'accept': 'application/json'})
                brokerDetailsResult = json.loads(brokerDetails.text)
                brokersSize[brokerId] = 0
                brokersTopics[brokerId] = ""
    else:
        print("No brokers were found!")

def getTopicsPartitionsByBroker():
    topics = requests.get(Kafdrop +  "topic")
    allTopics = json.loads(topics.text)

    if allTopics:
        for topic in allTopics:
            partitionsbyBrokerMetric = ""
            metricExpression = ""

            topicName = str(topic['name'])
            metricExpression = metricExpression + "topicName:" + topicName + ";"

            if not(topicName.startswith("__")):
                requestURL = Kafdrop +  "topic/" + topicName
                topicDetails = requests.get(requestURL, headers={'accept': 'application/json'})
                topicDetailsResult = json.loads(topicDetails.text)

                partitions = topicDetailsResult['partitions']
                for partition in partitions:
                    partitionId = str(partition['id'])
                    leader = partition['leader']
                    leaderId = str(leader['id'])   

                    metricExpression = metricExpression + "partitionId:" + partitionId + ";leaderId:" + leaderId + ";"

                    replicas = partition['replicas']
                    for replica in replicas:
                        broker = str(replica['id'])
                        brokersSize[broker] += 1; #Fix: é i ID do broker aqui e não a posição do array
                        brokersTopics[broker] += topicName + ";";
                        metricExpression = metricExpression + "brokerId:" + broker + ";"

                print(metricExpression)

    else:
        print("No topics were found!")

def getPartitionsByBroker():
    metricExpression = ""
    
    for broker, value in brokersSize.items():
        print("brokerId:" + broker + ";" + "partitions:" + str(value))

    print(metricExpression)

def getMessagesByTopic():
    topics = requests.get(Kafdrop +  "topic")
    allTopics = json.loads(topics.text)

    metricExpression = ""

    for topic in allTopics:
        topicName = str(topic['name'])
        requestURL = Kafdrop +  "topic/" + topicName + "/messages"
        messages = requests.get(requestURL, headers={'accept': 'application/json'})
        messagesResult = json.loads(messages.text)
        lastOffSet = messagesResult[0]['lastOffset']
        metricExpression = "topicName:" + topicName + ";messagesCount:" + str(lastOffSet) + ";"
        print(metricExpression)
    

def main():
    setBrokers()
    getTopicsPartitionsByBroker()
    getPartitionsByBroker()
    getMessagesByTopic()

if __name__ == "__main__":
    main()
