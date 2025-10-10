import React from "react";
import { useDraftStorage } from "./storage";
import { Gltf } from "@react-three/drei";

function Objects() {
  const { draft, setDraft } = useDraftStorage();

  console.log(JSON.stringify(draft, null, 2));

  return (
    <>
      {draft.objects.map((object, index) => (
        <Gltf
          key={index}
          src={object.url}
          position={object.position}
          scale={object.scale}
          rotation={object.rotation}
        />
      ))}
    </>
  );
}

export default Objects;
