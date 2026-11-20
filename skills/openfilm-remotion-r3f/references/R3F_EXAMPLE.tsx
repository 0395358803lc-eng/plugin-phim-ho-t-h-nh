/** Reference TSX fragment, not a built or tested video. Requires a pinned
 * Remotion/R3F stack verified on the selected PC and user approval to run. */
import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {ThreeCanvas} from '@remotion/three';

const GardenContents: React.FC = () => {
  const frame = useCurrentFrame();
  const grow = interpolate(frame, [0, 150], [0.05, 1.9], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return <>
    <ambientLight intensity={0.7}/>
    <directionalLight position={[5, 8, 5]} intensity={2}/>
    <mesh scale={[grow, grow, grow]} position={[0, grow, 0]}>
      <sphereGeometry args={[0.8, 24, 24]}/>
      <meshStandardMaterial color="#93ffc2"/>
    </mesh>
  </>;
};

export const Garden3D: React.FC = () => (
  <AbsoluteFill>
    <ThreeCanvas width={1920} height={1080}
      camera={{position: [0, 3, 7], fov: 42}}>
      <GardenContents/>
    </ThreeCanvas>
  </AbsoluteFill>
);

// Config example (remotion.config.ts) when the pinned runtime supports it:
// import {Config} from '@remotion/cli/config';
// Config.setChromiumOpenGlRenderer('angle');
// Do NOT use useFrame(() => mesh.rotation.y += delta) or unseeded random.
