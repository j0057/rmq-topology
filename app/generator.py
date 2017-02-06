import argparse
import json

import pygraphviz as pgv
from broker import Broker

def parse_args():
    ''' Get cli args '''
    parser = argparse.ArgumentParser(description='RabbitMQ topology generator')
    parser.add_argument('-i', '--infile',
                        type=argparse.FileType('r'),
                        required=True,
                        help='Broker definition file')
    parser.add_argument('-o', '--outfile',
                        type=argparse.FileType('w'),
                        required=True,
                        help='Output file')

    return parser.parse_args()

def gen():
    ''' Generator '''
    args = parse_args()
    broker = Broker(json.loads(args.infile.read()))

    # Create graph
    graph = pgv.AGraph(directed=True, strict=False, rankdir='LR')
    exchanges = [exchange.name for exchange in broker.exchanges()]
    queues = [queue.name for queue in broker.queues()]

    for exchange in exchanges:
        graph.add_node(exchange, shape='square')

    for queue in queues:
        graph.add_node(queue, shape='rectangle')

    for binding in broker.bindings():
        graph.add_edge(binding.source, binding.destination, label=binding.routing_key,
                       group=binding.source)

    for policy in broker.policies():
        if policy.pattern is not None and policy.definition.dead_letter_exchange is not None:
            graph.add_edge(policy.pattern, policy.definition.dead_letter_exchange,
                           label=policy.definition.dead_letter_routing_key, group=policy.pattern)

    # Sub graphs, disabled because can't get a nice layout with subgraphs.
    # graph.add_subgraph(exchanges, 'cluster_exchanges', label='exchanges')
    # graph.add_subgraph(queues, 'cluster_queues', label='queues')

    # graph.layout(prog='dot')
    # graph.write(args.outfile)
    graph.draw(args.outfile.name, prog='dot')

gen()
