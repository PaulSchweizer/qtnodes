# --------------------------------------------------------------------
# --- FLOWPIPE GRAPH ---------------
# --------------------------------------------------------------------

import sys
sys.path.append("C:\\PROJECTS\\flowpipe")

from flowpipe.graph import Graph
from flowpipe.node import Node


@Node(outputs=["baked_script"])
def Bake(settings):
    pass


@Node(outputs=["rendered_sequence", "output2", "output3"])
def Render(nuke_script):
    pass


@Node(outputs=["transcode_id"])
def Transcode(image_sequence):
    pass


@Node(outputs=["version_id"])
def Update(data):
    pass


graph = Graph()
bake = Bake(graph=graph)
render = Render(graph=graph)
transcode = Transcode(graph=graph)
update = Update(graph=graph)

bake.outputs["baked_script"] >> render.inputs["nuke_script"]
render.outputs["rendered_sequence"] >> transcode.inputs["image_sequence"]
render.outputs["rendered_sequence"] >> update.inputs["data"]

print graph


# --------------------------------------------------------------------
# --- UI ---------------
# --------------------------------------------------------------------


from PySide import QtGui
from qtnodes import (Header, Node, InputKnob,
                     OutputKnob, NodeGraphWidget)


class FlowpipeUINode(Node):

    def __init__(self, node):
        super(FlowpipeUINode, self).__init__()
        self.addHeader(Header(node=self, text=node.name))
        for input_plug in node.inputs.values():
            self.addKnob(InputKnob(name=input_plug.name))
        for output_plug in node.outputs.values():
            self.addKnob(OutputKnob(name=output_plug.name))


app = QtGui.QApplication([])
ui_graph = NodeGraphWidget()
ui_graph.registerNodeClass(FlowpipeUINode)

# Create Nodes
#
x = 0
ui_nodes = {}
for column in graph.evaluation_matrix:
    y = 0
    x_diff = 0
    for row, node in enumerate(column):
        ui_node = FlowpipeUINode(node)
        ui_graph.addNode(ui_node)
        ui_nodes[node.name] = ui_node

        x_diff = (ui_node.boundingRect().left() - ui_node.boundingRect().x() + 4 if
                  ui_node.boundingRect().left() - ui_node.boundingRect().x() + 4 > x_diff else x_diff)

        y += ui_node.boundingRect().right() - ui_node.boundingRect().y()

        ui_node.moveBy(x*75, y)

    x += x_diff

# Connect them / Add egdes
#
for node in graph.nodes:
    ui_node = ui_nodes[node.name]
    for input_plug in node.inputs.values():
        if input_plug.connections:
            upstream_plug = input_plug.connections[0]
            upstream_ui_node = ui_nodes[upstream_plug.node.name]

            upstream_ui_node.knob(upstream_plug.name).connectTo(ui_node.knob(input_plug.name))

ui_graph.show()

app.exec_()
