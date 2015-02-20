# diags.py

import copy
import json
from pprint import pprint

# data_file_name = "data/tlv3_data.json"
# data_file_name = "data/small_data.json"
data_file_name = "data/compressed_data.json"
# data_file_name = "data/large_data.json"
# data_file_name = "data/shapes_data.json"

#
# Load force layout data.
#
def load_data():
    json_data = open(data_file_name)
    loadedData = json.load(json_data)
    json_data.close()
    dump_data(loadedData)
    return loadedData

def dump_data(dataset):
    print("NODES +++++++++++++++++++++++++")
    for record in dataset["nodes"]:
        print(record["name"] + " is of type " + record["type"])
    print("LINKS +++++++++++++++++++++++++")
    for record in dataset["links"]:
        print(record["source"] + " has a " + record["type"] + " relationship with " + record["target"])
    print("PATHS +++++++++++++++++++++++++")
    for record in dataset["paths"]:
        print("SOURCE=" + record["source"] + " TARGET=" + record["target"])


fullDataset = load_data()


#
# Return the nodes and links associated with the compressed path identified
# by the start and end nodes.
#
def get_expanded_path(start, end):
    print("get_expanded_path() : start=" + start + " end=" + end)
    for record in fullDataset["paths"]:
        if ( (record["source"] == start) and (record["target"] == end) ):
            return record

    return fullDataset


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

    for testNode in resultData["nodes"]:
        if testNode["id"] == focus:
            testNode["focus"] = "true"
        else:
            testNode["focus"] = "false"

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

    nodeIds = []

    for link in links:
        if link["source"] not in nodeIds:
            nodeIds.append(link["source"])
        if link["target"] not in nodeIds:
            nodeIds.append(link["target"])

    for node in nodes:
        if node["id"] in nodeIds:
            result["filteredNodes"].append(node)
        else:
            result["remainderNodes"].append(node)

    return result
