import { useEffect, useState } from "react";

import ForceGraph2D from "react-force-graph-2d";


export default function AttackGraph() {

    const [graphData, setGraphData] = useState({
        nodes: [],
        links: []
    });

    const [selectedNode, setSelectedNode] = useState(null);

    useEffect(() => {

        fetch("http://127.0.0.1:8000/api/graph")
            .then(res => res.json())
            .then(data => {

                setGraphData({

                    nodes: data.nodes,

                    links: data.edges
                });
            });

    }, []);

    // -----------------------------------
    // NODE COLORING
    // -----------------------------------
    const getNodeColor = (node) => {

        const label = node.label;

        if (
            label === "external_transfer"
        ) {
            return "#ff4d4f";
        }

        if (
            label === "usb_insert"
        ) {
            return "#fa8c16";
        }

        if (
            label === "bulk_file_access"
        ) {
            return "#722ed1";
        }

        if (
            label === "archive_creation"
        ) {
            return "#eb2f96";
        }

        if (
            label === "email_sent"
        ) {
            return "#1890ff";
        }

        return "#52c41a";
    };

    // -----------------------------------
    // NODE SIZE
    // -----------------------------------
    const getNodeSize = (node) => {

        return Math.max(
            4,
            node.risk_score * 1.5
        );
    };

    // -----------------------------------
    // EDGE COLOR
    // -----------------------------------
    const getEdgeColor = (link) => {

        if (
            link.edge_type === "temporal"
        ) {
            return "#999";
        }

        if (
            link.edge_type === "correlated"
        ) {
            return "#ff7875";
        }

        return "#69c0ff";
    };

    return (

        <div className="w-full">

            {/* ----------------------------------- */}
            {/* GRAPH */}
            {/* ----------------------------------- */}
            <div className="border rounded-xl overflow-hidden">

                <ForceGraph2D

                    graphData={graphData}

                    width={1400}

                    height={800}

                    backgroundColor="#0f172a"

                    nodeLabel={node => `
                        ${node.label}

                        User: ${node.user || "N/A"}

                        Time:
                        ${node.timestamp || "N/A"}
                    `}

                    nodeColor={getNodeColor}

                    nodeVal={getNodeSize}

                    linkColor={getEdgeColor}

                    linkWidth={link =>
                        Math.max(
                            1,
                            link.weight / 2
                        )
                    }

                    linkDirectionalParticles={2}

                    linkDirectionalParticleSpeed={0.003}

                    cooldownTicks={100}

                    onNodeClick={(node) => {

                        setSelectedNode(node);
                    }}
                />

            </div>

            {/* ----------------------------------- */}
            {/* SIDE PANEL */}
            {/* ----------------------------------- */}
            {
                selectedNode && (

                    <div className="mt-4 p-4 border rounded-xl bg-white shadow">

                        <h2 className="text-xl font-bold mb-3">
                            Event Details
                        </h2>

                        <div className="space-y-2">

                            <p>
                                <strong>Event:</strong>
                                {" "}
                                {selectedNode.label}
                            </p>

                            <p>
                                <strong>User:</strong>
                                {" "}
                                {selectedNode.user}
                            </p>

                            <p>
                                <strong>Timestamp:</strong>
                                {" "}
                                {selectedNode.timestamp}
                            </p>

                            <p>
                                <strong>Device:</strong>
                                {" "}
                                {selectedNode.device || "N/A"}
                            </p>

                            <p>
                                <strong>Resource:</strong>
                                {" "}
                                {selectedNode.resource || "N/A"}
                            </p>

                            <p>
                                <strong>Risk Score:</strong>
                                {" "}
                                {selectedNode.risk_score}
                            </p>

                        </div>

                    </div>
                )
            }

        </div>
    );
}