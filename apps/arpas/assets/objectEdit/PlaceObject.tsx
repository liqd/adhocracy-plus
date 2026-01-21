import { Matrix4 } from "@react-three/fiber";
import { useHitTest } from "@react-three/xr";
import React, { ComponentProps } from "react";
import { type Mesh } from "three";
import { Gltf } from "@react-three/drei";
import { OBJECT_SCALES, useDraftStorage } from "../storage";

function PlaceObject() {
    const { draft, setDraft } = useDraftStorage();
    const [relativeRotation, setRelativeRotation] = React.useState(0);

    const boxRef = React.useRef<Mesh>(null);
    useHitTest((hitMatrix, hit) => {
        if (boxRef.current && draft.placeObjectUrl) {
            hitMatrix.decompose(
                boxRef.current.position,
                boxRef.current.quaternion,
                boxRef.current.scale
            );
            boxRef.current.scale.multiplyScalar(
                OBJECT_SCALES[draft.placeObjectUrl] || 1
            );

            boxRef.current.rotation.y += relativeRotation;
        }
    });

    if (!draft.placeObjectUrl) {
        return null;
    }

    return (
        <Gltf
            ref={boxRef}
            src={draft.placeObjectUrl}
            onClick={() => {
                if (boxRef.current) {
                    setDraft({
                        ...draft,
                        objects: [
                            ...(draft.objects || []),
                            {
                                url: draft.placeObjectUrl!,
                                position: boxRef.current.position,
                                scale: boxRef.current.scale,
                                rotation: boxRef.current.rotation,
                            },
                        ],
                        placeObjectUrl: undefined,
                    });
                }
            }}
            onPointerDown={() => {
                console.log("pointer down");

                let currentRelativeRotation = relativeRotation;
                const onPointerMove = (event: PointerEvent) => {
                    const dx = event.movementX || 0;

                    const newRelativeRotation =
                        currentRelativeRotation + dx * 0.01;
                    setRelativeRotation(newRelativeRotation);
                    currentRelativeRotation = newRelativeRotation;
                };

                document.addEventListener("pointerup", () => {
                    document.removeEventListener("pointermove", onPointerMove);
                });

                document.addEventListener("pointermove", onPointerMove);
            }}
            onPointerUp={() => {
                console.log("pointer up");
            }}
        />
    );
}

export default PlaceObject;
