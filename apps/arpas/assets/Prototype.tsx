import {
    VRButton,
    ARButton,
    XR,
    Controllers,
    Hands,
    RayGrab,
    Interactive,
    useXR,
} from "@react-three/xr";
import { Canvas } from "@react-three/fiber";
import { Text, Gltf, Clouds, Cloud } from "@react-three/drei";
import * as THREE from "three";

import React from "react";
import { DraftStorageProvider } from "./storage";
import ObjectSelector from "./objectEdit/ObjectSelector";
import PlaceObject from "./objectEdit/PlaceObject";
import Objects from "./Objects";

function Prototype() {
    return (
        <div
            style={{
                height: "30vh",
                width: "100%",
                position: "relative",
            }}
        >
            <DraftStorageProvider>
                <ObjectSelector />

                <ARButton />
                <Canvas
                    style={{
                        height: "100%",
                        width: "100%",
                    }}
                    dpr={[1, 2]}
                    gl={{ antialias: true }}
                >
                    <XR>
                        <ambientLight />

                        <Controllers />
                        <Hands />

                        <PlaceObject />
                        <Objects />
                    </XR>
                </Canvas>
            </DraftStorageProvider>
        </div>
    );
}

export default Prototype;
