# diags.py

import copy
import json
from pprint import pprint

#data_file_name = "data/tlv3_data.json"
#data_file_name = "data/small_data.json"
data_file_name = "data/large_data.json"

#
# Load force layout data.
#
def load_data():
    json_data = open(data_file_name)
    loadedData = json.load(json_data)
    json_data.close()
    return loadedData

def dump_data(dataset):
    print("NODES +++++++++++++++++++++++++")
    for record in dataset["nodes"]:
        print(record["name"] + " is of type " + record["type"])
    print("LINKS +++++++++++++++++++++++++")
    for record in dataset["links"]:
        print(record["source"] + " has a " + record["type"] + " relationship with " + record["target"])

#
# Load tree layout data.
#
def load_flare_data():
    flare_json_data = open("data/flare.json")
    loadedFlareData = json.load(flare_json_data)
    flare_json_data.close()
    return loadedFlareData


fullDataset = load_data()
flareDataset = load_flare_data()


#
# Return the full tree dataset.
#
def get_flare_data():
    return flareDataset

#
# Produce a subset of the data.
# All nodes will be within <span> connections of the focus.
#
def filter_data(focus, spanCount):
    if (spanCount=="0") or (spanCount=="all"):
        return fullDataset

    queryDataset = copy.deepcopy(fullDataset)
    
    return get_span(focus, int(spanCount), queryDataset)


def get_span(focus, spanIndex, dataset):
    resultData = {}
    resultData["links"] = []
    resultData["nodes"] = []

    linkFilterResult = get_links_for_node(dataset["links"], focus)
    nodeFilterResult = get_nodes_for_links(dataset["nodes"], linkFilterResult["filteredLinks"])

    resultData["links"] = linkFilterResult["filteredLinks"]
    resultData["nodes"] = nodeFilterResult["filteredNodes"]

    newQueryDataset = {}
    newQueryDataset["links"] = linkFilterResult["remainderLinks"]
    newQueryDataset["nodes"] = dataset["nodes"]

    if (spanIndex > 1):
        for nextNode in copy.deepcopy( nodeFilterResult["filteredNodes"] ):
            nodeResultData = get_span(nextNode["id"], (spanIndex - 1), newQueryDataset)
            resultData["links"] = resultData["links"] + nodeResultData["links"]
            for node in nodeResultData["nodes"]:
                for resultNode in resultData["nodes"]:
                    if node["id"] == resultNode["id"]:
                        break;
                else:
                    resultData["nodes"].append(node)

    return resultData


#
# Get all the links which have the given node as one of the endpoints.
#
def get_links_for_node(links, node):
    result = {}
    result["filteredLinks"] = []
    result["remainderLinks"] = []

    for link in links:
        if (node == link["source"]) or (node == link["target"]):
            result["filteredLinks"].append(link)
        else:
            result["remainderLinks"].append(link)

    return result    


#
# Get all the nodes referenced by any of the listed links.
#
def get_nodes_for_links(nodes, links):
    result = {}
    result["filteredNodes"] = []
    result["remainderNodes"] = []

    nodeNames = []

    for link in links:
        if link["source"] not in nodeNames:
            nodeNames.append(link["source"])
        if link["target"] not in nodeNames:
            nodeNames.append(link["target"])

    for node in nodes:
        if node["id"] in nodeNames:
            result["filteredNodes"].append(node)
        else:
            result["remainderNodes"].append(node)

    return result
