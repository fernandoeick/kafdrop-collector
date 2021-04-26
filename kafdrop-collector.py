import requests
import json
import sys
import logging
from datadog import initialize, statsd
import time

kafdropAddress = sys.argv[1]
clusterName = sys.argv[2]

brokerMetrics = {}
options = {
    'statsd_host':'127.0.0.1',
    'statsd_port':8125
}

initialize(**options)
now = int(time.time())

def defineLogConfiguration():
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.INFO)

def loadTopicMessagesMetric():
    metricName = "tr.taxprof.kafkaadmin.topic.messages"
    try:
        topics = requests.get(kafdropAddress +  "topic")
        allTopics = json.loads(topics.text)

        if allTopics:
            for topic in allTopics:
                topicName = str(topic['name'])
                requestURL = kafdropAddress +  "topic/" + topicName
                topicDetails = requests.get(requestURL, headers={'accept': 'application/json'})
                topicDetailsStr = json.loads(topicDetails.text)
                partitions = topicDetailsStr['partitions']

                if partitions:
                    for partition in partitions:
                        requestURL = kafdropAddress +  "topic/" + topicName + "/messages"
                        messages = requests.get(requestURL, headers={'accept': 'application/json'})
                        messagesStr = json.loads(messages.text)
                        lastOffSet = messagesStr[0]['lastOffset']

                        brokerId = str(partition['leader']['id'])
                        partitionId = str(partition['id'])
                        lastOffSet = str(lastOffSet)
                        underReplicated = str(partition['underReplicated'])

                        metricTags = [
                            "broker_id:"+brokerId,
                            "partition_id:"+partitionId,
                            "is_under_replicated:"+underReplicated,
                            "cluster_name:"+clusterName,
                            "topic_name:"+topicName
                        ]

                        statsd.gauge(metricName, lastOffSet, tags=metricTags)
                        logging.info(
                            "metricName: " + metricName + 
                            " - metricValue: " + lastOffSet + 
                            " - metricTags[" +
                            "broker_id:"+brokerId+",partition_id:"+partitionId+",is_under_replicated:"+underReplicated+
                            ",cluster_name:"+clusterName+",topic_name:"+topicName+"]")
                else:
                    logging.warning("No partitions were found in topic " + topicName)
        else:
            logging.warning("No topics were found!")

    except:
        logging.error("It was not possible to connect with the MSK cluster.")
        exit()

def loadTopicConsumersMetric():
    metricName = "tr.taxprof.kafkaadmin.consumer.lag"
    try:
        topics = requests.get(kafdropAddress +  "topic")
        allTopics = json.loads(topics.text)

        if allTopics:
            for topic in allTopics:
                topicName = str(topic['name'])
                requestURL = kafdropAddress +  "topic/" + topicName + "/consumers"
                consumers = requests.get(requestURL, headers={'accept': 'application/json'})
                consumersStr = json.loads(consumers.text)

                if consumersStr:
                    for consumer in consumersStr:
                        groupId = str(consumer['groupId'])
                        consumerTopics = consumer['topics']

                        if consumerTopics:
                            for consumerTopic in consumerTopics:
                                if consumerTopic:
                                    consumerLag = str(consumerTopic['lag'])
                                    consumerTopicsPartitions = consumerTopic['partitions']

                                    for topicPartition in consumerTopicsPartitions:
                                        topicPartitionLag = str(topicPartition['lag'])
                                        topicPartitionOffSet = str(topicPartition['offset'])
                                        partitionId = str(topicPartition['partitionId'])

                                        metricTags = [
                                            "last_topic_offset:"+topicPartitionOffSet,
                                            "consumer_group_id:"+groupId,
                                            "cluster_name:"+clusterName,
                                            "topic_name:"+topicName,
                                            "partition_id:"+partitionId
                                        ]

                                        statsd.gauge(metricName, consumerLag, tags=metricTags)
                                        logging.info(
                                            "metricName: " + metricName + 
                                            " - metricValue: " + consumerLag + 
                                            " - metricTags[" +
                                            "last_topic_offset:"+topicPartitionOffSet+",consumer_group_id:"+groupId+",cluster_name:"+clusterName+
                                            ",topic_name:"+topicName+",partition_id:"+partitionId+"]")
        else:
            logging.warning("No topics were found!")
    
    except:
        logging.error("It was not possible to connect with the MSK cluster.")
        exit()


def main():
    defineLogConfiguration()
    loadTopicMessagesMetric()
    loadTopicConsumersMetric()
    
if __name__ == "__main__":
    main()
