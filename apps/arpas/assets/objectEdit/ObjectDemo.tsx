import React, { Suspense, useEffect, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, useGLTF, Box, Gltf } from "@react-three/drei";
import * as THREE from "three";

const SpinningModel = ({ url }: { url: string }) => {
  const modelRef = useRef<THREE.Group>();
  const { scene } = useGLTF(url);
  const [scale, setScale] = React.useState(1);

  useEffect(() => {
    if (modelRef.current && scale === 1) {
      const box = new THREE.Box3().setFromObject(scene);
      const size = new THREE.Vector3();
      box.getSize(size);
      const maxDim = Math.max(size.x, size.y, size.z);
      const desiredSize = 3;
      const scale = desiredSize / maxDim;
      setScale(scale);
    }
  }, [scale, scene]);

  useFrame(() => {
    if (modelRef.current) {
      modelRef.current.rotation.y += 0.01; // Adjust the speed of rotation here
    }
  });

  return (
    <group scale={[scale, scale, scale]}>
      <primitive object={scene} ref={modelRef} />
    </group>
  );
};

function ObjectDemo({ url }: { url: string }) {
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />
      <pointLight position={[-10, -10, -10]} />
      <Suspense fallback={null}>
        <SpinningModel url={url} />
      </Suspense>
      <OrbitControls />
    </Canvas>
  );
}

export default ObjectDemo;
