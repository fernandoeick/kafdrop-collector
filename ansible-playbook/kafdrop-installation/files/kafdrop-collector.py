import requests
import json
import sys
import logging
from datadog import initialize, statsd
import time

kafdropAddress = sys.argv[1]
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
    topicMessagesMetricName = "tr.taxprof.kafkaadmin.topic.messages"
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
                        clusterName = "my_cluster"

                        topicMessagesMetricTags = [
                            "broker_id:"+brokerId,
                            "partition_id:"+partitionId,
                            "last_offset:"+lastOffSet,
                            "is_under_replicated:"+underReplicated,
                            "cluster_name:"+clusterName
                        ]

                        statsd.increment(topicMessagesMetricName, tags=topicMessagesMetricTags)
                        logging.info("metricName: " + topicMessagesMetricTags + "metricTags: " + topicMessagesMetricTags)
                else:
                    logging.warning("No partitions were found in topic " + topicName)
        else:
            logging.warning("No topics were found!")

    except:
        logging.error("It was not possible to connect with the MSK cluster.")
        exit()

def main():
    defineLogConfiguration()
    loadTopicMessagesMetric()
    
if __name__ == "__main__":
    main()
