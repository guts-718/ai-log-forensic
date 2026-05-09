import { useEffect, useState } from "react";

import ForceGraph2D from "react-force-graph-2d";


export default function AttackGraph() {

    const [graphData, setGraphData] = useState({
        nodes: [],
        links: []
    });

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

    return (

        <div className="w-full h-[800px] border rounded">
            <div>this is the beginning of the attack graph</div>
            <ForceGraph2D

                graphData={graphData}

                nodeLabel={node => `
                    ${node.label}
                    ${node.user || ""}
                `}

                nodeAutoColorBy="type"

                linkDirectionalParticles={2}

                linkDirectionalParticleSpeed={0.003}

                linkWidth={link =>
                    Math.max(
                        1,
                        link.weight / 3
                    )
                }

                cooldownTicks={100}

                onNodeClick={(node) => {

                    console.log(node);
                }}
            />

        </div>
    );
}