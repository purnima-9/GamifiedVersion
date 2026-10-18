import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sparkles, Text, ContactShadows } from '@react-three/drei';
import { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';

const getLanePositions = (count) => {
  if (count <= 1) return [0];
  const first = -4.5;
  const last = 4.5;
  const spacing = (last - first) / (count - 1);
  return Array.from({ length: count }, (_, index) => first + spacing * index);
};
const PALETTE = ['#ffbd54', '#66dce5', '#d39bff', '#c9e77c'];

function Ground({ isPaused }) {
  const stripes = useRef();
  useFrame((_, dt) => {
    if (!isPaused && stripes.current) {
      stripes.current.position.z = (stripes.current.position.z + dt * 9) % 5;
    }
  });
  return <group>
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.12, -8]} receiveShadow><planeGeometry args={[18, 70]} /><meshStandardMaterial color="#9b8b7e" roughness={0.92} /></mesh>
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.08, -8]}><planeGeometry args={[13, 70]} /><meshStandardMaterial color="#b5a495" roughness={0.94} /></mesh>
    <group ref={stripes}>{Array.from({ length: 15 }, (_, i) => <group key={i} position={[0, -0.04, -i * 5]}>{[-2.15, 2.15].map((x) => <mesh key={x} position={[x, 0, 0]}><boxGeometry args={[0.12, 0.03, 2.8]} /><meshStandardMaterial color="#fff0c2" emissive="#c9a866" emissiveIntensity={0.12} /></mesh>)}</group>)}</group>
    {[-1, 1].map((side) => <mesh key={side} position={[side * 6.35, -0.015, -8]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[0.18, 70]} /><meshStandardMaterial color="#d79d51" emissive="#ad7137" emissiveIntensity={0.18} /></mesh>)}
    {[-1, 1].map(side => <group key={side} position={[side * 8.3, 0, -8]}>{Array.from({ length: 10 }, (_, i) => <group key={i} position={[side * (i % 2) * .5, 0, -i * 6]}><mesh position={[0, 1.1, 0]} castShadow><cylinderGeometry args={[0.08, 0.15, 2.2, 7]} /><meshStandardMaterial color="#6b5344" /></mesh><mesh position={[0, 2.3, 0]} castShadow><coneGeometry args={[0.85 + (i % 3) * .15, 2.4, 7]} /><meshStandardMaterial color={i % 2 ? '#8b6f47' : '#a08165'} roughness={0.9} /></mesh><mesh position={[0, 3.1, 0]}><sphereGeometry args={[.28, 8, 8]} /><meshStandardMaterial color="#f5ede0" emissive="#e6d4c4" emissiveIntensity={.3} /></mesh></group>)}</group>)}
    <fog attach="fog" args={['#e3d5cc', 18, 48]} />
  </group>;
}

function Gate({ option, index, positionX, active, onChoose, gateWidth }) {
  const hingeL = useRef(); const hingeR = useRef();
  const x = positionX; const color = PALETTE[index % PALETTE.length];
  const halfWidth = gateWidth / 2;
  const doorWidth = gateWidth * 0.39;
  useFrame((_, dt) => {
    const target = active ? -1.24 : 0;
    if (hingeL.current) hingeL.current.rotation.y = THREE.MathUtils.damp(hingeL.current.rotation.y, target, 5, dt);
    if (hingeR.current) hingeR.current.rotation.y = THREE.MathUtils.damp(hingeR.current.rotation.y, active ? 1.24 : 0, 5, dt);
  });
  return <group position={[x, 0, 0]} onClick={(e) => { e.stopPropagation(); onChoose(option, index); }}>
    <mesh position={[0, 2.1, 0]} castShadow><boxGeometry args={[gateWidth, .18, .35]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={.65} /></mesh>
    {[-1, 1].map(s => <mesh key={s} position={[s * (halfWidth - 0.09), 1.08, 0]} castShadow><boxGeometry args={[.18, 2.16, .32]} /><meshStandardMaterial color={color} metalness={.3} roughness={.25} emissive={color} emissiveIntensity={.35} /></mesh>)}
    <group ref={hingeL} position={[-doorWidth, .06, .04]}><mesh position={[doorWidth / 2, 1, 0]} castShadow><boxGeometry args={[doorWidth, 1.9, .12]} /><meshStandardMaterial color="#8b5a3c" roughness={.5} /></mesh><mesh position={[doorWidth / 2, 1, .071]}><boxGeometry args={[doorWidth * .76, 1.6, .025]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={.35} /></mesh><mesh position={[doorWidth * .8, 1, .1]}><sphereGeometry args={[.07, 12, 12]} /><meshStandardMaterial color="#fff5cc" metalness={.8} emissive={color} emissiveIntensity={.2} /></mesh></group>
    <group ref={hingeR} position={[doorWidth, .06, .04]}><mesh position={[-doorWidth / 2, 1, 0]} castShadow><boxGeometry args={[doorWidth, 1.9, .12]} /><meshStandardMaterial color="#8b5a3c" roughness={.5} /></mesh><mesh position={[-doorWidth / 2, 1, .071]}><boxGeometry args={[doorWidth * .76, 1.6, .025]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={.35} /></mesh><mesh position={[-doorWidth * .8, 1, .1]}><sphereGeometry args={[.07, 12, 12]} /><meshStandardMaterial color="#fff5cc" metalness={.8} emissive={color} emissiveIntensity={.2} /></mesh></group>
    <mesh position={[0, 2.72, .13]}><boxGeometry args={[gateWidth + .12, 1.28, .2]} /><meshStandardMaterial color="#3d2940" emissive={color} emissiveIntensity={.18} /></mesh>
    <mesh position={[0, 2.72, .235]}><boxGeometry args={[gateWidth - .06, 1.12, .04]} /><meshStandardMaterial color="#4a3650" /></mesh>
    <mesh position={[0, 1.08, 0]} castShadow><sphereGeometry args={[.55, 16, 16]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={.6} transparent opacity={.85} roughness={.3} /></mesh>
    <Text position={[0, 2.77, .29]} fontSize={Math.min(.84, 4.9 / Math.max(option.label.length, 7))} maxWidth={2.35} textAlign="center" color="#fff6e6" anchorX="center" anchorY="middle" outlineWidth={.012} outlineColor="#160e21">{option.label}</Text>
    <Text position={[0, 3.48, .22]} fontSize={.22} color={color} anchorX="center" outlineWidth={.015} outlineColor="#25162b">{`OPTION ${index + 1}`}</Text>
    <pointLight position={[0, 2.3, 1.2]} color={color} intensity={active ? 4.5 : 2.2} distance={6.5} decay={1.5} />
    <pointLight position={[0, 1.08, 0]} color={color} intensity={active ? 2.5 : 1.3} distance={3.5} />
  </group>;
}

function Player({ lane, lanePositions, running, isPaused, characterId }) {
  const root = useRef(); const leftLeg = useRef(); const rightLeg = useRef(); const leftArm = useRef(); const rightArm = useRef();
  useFrame((state, dt) => {
    if (isPaused || !root.current) return;
    root.current.position.x = THREE.MathUtils.damp(root.current.position.x, lanePositions[lane] || 0, 5, dt);
    root.current.position.z = THREE.MathUtils.damp(root.current.position.z, running ? -0.5 : -7.5, running ? 2.4 : 7, dt);
    root.current.position.y = running ? .08 + Math.abs(Math.sin(state.clock.elapsedTime * 13)) * .18 : 0;
    const swing = running ? Math.sin(state.clock.elapsedTime * 13) * 1.2 : 0;
    if (leftLeg.current) leftLeg.current.rotation.x = swing;
    if (rightLeg.current) rightLeg.current.rotation.x = -swing;
    if (leftArm.current) leftArm.current.rotation.x = -swing * 1.1;
    if (rightArm.current) rightArm.current.rotation.x = swing * 1.1;
  });
  const bodyColor = characterId === 'girl' ? '#FF6B9D' : '#6366F1';
  const pantsColor = '#1F2937';
  const skinColor = '#FDBCB4';
  return <group ref={root} position={[0, 0, 0]}>
    <mesh position={[0, 0.65, 0]} castShadow><capsuleGeometry args={[.22, .42, 4, 8]} /><meshStandardMaterial color={bodyColor} roughness={.6} /></mesh>
    <mesh position={[0, 1.15, 0]} castShadow><sphereGeometry args={[.2, 16, 12]} /><meshStandardMaterial color={skinColor} roughness={.75} /></mesh>
    <mesh position={[0, 1.27, -.01]} castShadow><sphereGeometry args={[.22, 14, 8, 0, Math.PI * 2, 0, Math.PI * .5]} /><meshStandardMaterial color="#2C2C2C" roughness={.85} /></mesh>
    {characterId === 'girl' && <group><mesh position={[0, 1.16, -.13]} castShadow><sphereGeometry args={[.15, 12, 10]} /><meshStandardMaterial color="#8B6B7F" /></mesh><mesh position={[-.18, 0.92, 0]} castShadow><capsuleGeometry args={[.07, .3, 3, 6]} /><meshStandardMaterial color="#8B6B7F" /></mesh><mesh position={[.18, 0.92, 0]} castShadow><capsuleGeometry args={[.07, .3, 3, 6]} /><meshStandardMaterial color="#8B6B7F" /></mesh></group>}
    <mesh position={[0, 0.32, .03]}><boxGeometry args={[.34, .1, .23]} /><meshStandardMaterial color={pantsColor} /></mesh>
    <mesh position={[0, 1.05, -0.24]} castShadow><boxGeometry args={[.5, .45, .3]} /><meshStandardMaterial color={pantsColor} roughness={.65} /></mesh>
    <mesh position={[0, 0.95, -0.27]}><boxGeometry args={[.44, .35, .26]} /><meshStandardMaterial color="#374151" roughness={.45} /></mesh>
    <group ref={leftLeg} position={[-.11, .35, 0]}><mesh position={[0, -.16, 0]} castShadow><capsuleGeometry args={[.075, .3, 3, 6]} /><meshStandardMaterial color={pantsColor} roughness={.7} /></mesh><mesh position={[0, -.33, .065]}><boxGeometry args={[.15, .08, .24]} /><meshStandardMaterial color="#4B5563" roughness={.8} /></mesh></group>
    <group ref={rightLeg} position={[.11, .35, 0]}><mesh position={[0, -.16, 0]} castShadow><capsuleGeometry args={[.075, .3, 3, 6]} /><meshStandardMaterial color={pantsColor} roughness={.7} /></mesh><mesh position={[0, -.33, .065]}><boxGeometry args={[.15, .08, .24]} /><meshStandardMaterial color="#4B5563" roughness={.8} /></mesh></group>
    <group ref={leftArm} position={[-.25, .88, 0]}><mesh position={[-.02, -.16, 0]} rotation={[0, 0, -.15]}><capsuleGeometry args={[.06, .3, 3, 6]} /><meshStandardMaterial color={skinColor} roughness={.75} /></mesh></group>
    <group ref={rightArm} position={[.25, .88, 0]}><mesh position={[.02, -.16, 0]} rotation={[0, 0, .15]}><capsuleGeometry args={[.06, .3, 3, 6]} /><meshStandardMaterial color={skinColor} roughness={.75} /></mesh></group>
    <mesh position={[0, .03, -.05]} rotation={[-Math.PI / 2, 0, 0]}><circleGeometry args={[.36, 24]} /><meshBasicMaterial color="#171022" transparent opacity={.32} /></mesh>
  </group>;
}

function RunnerScene({ options, selected, multiSelect, isPaused, onChoose, sceneKey, characterId }) {
  const passedRef = useRef(false); const [lane, setLane] = useState(1);
  const gateZ = useRef(-25); const gateGroup = useRef(); const cameraTarget = useRef(new THREE.Vector3(0, 1.5, -8));
  const readyToChoose = useRef(false); const characterZ = useRef(0);
  const lanePositions = useMemo(() => getLanePositions(options.length), [options.length]);
  const gateWidth = options.length > 4 ? 1.78 : 2.6;
  const selectedOptions = Array.isArray(selected) ? selected : selected ? [selected] : [];
  useEffect(() => {
    passedRef.current = false;
    readyToChoose.current = false;
    // Keep the explorer in their current lane so the journey feels continuous.
    // Respawn only the next gate set far ahead on the same path.
    gateZ.current = -25;
    characterZ.current = 0;
    if (gateGroup.current) gateGroup.current.position.z = -25;
  }, [sceneKey]);
  useEffect(() => {
    if (selected && !multiSelect) {
      const selectedIndex = options.findIndex((option) => option.id === selected.id);
      if (selectedIndex >= 0) setLane(selectedIndex);
    }
  }, [multiSelect, options, selected]);
  useFrame((state, dt) => {
    if (isPaused) return;
    characterZ.current += dt * 3.5;
    if (selected && !multiSelect) {
      // Keep the selected gate moving through and beyond the camera while the next question loads.
      gateZ.current += dt * 9.5;
      if (gateZ.current > 1) passedRef.current = true;
    } else if (!passedRef.current) {
      gateZ.current = Math.min(-6.5, gateZ.current + dt * 2.2);
      readyToChoose.current = gateZ.current >= -6.5;
    }
    if (gateGroup.current) gateGroup.current.position.z = gateZ.current;
    const selectedIndex = selected && !multiSelect ? options.findIndex(o => o.id === selected.id) : -1;
    state.camera.position.x = THREE.MathUtils.damp(state.camera.position.x, selectedIndex >= 0 ? lanePositions[selectedIndex] * .55 : 0, 2.8, dt);
    state.camera.position.y = THREE.MathUtils.damp(state.camera.position.y, 4.3, 2, dt);
    state.camera.position.z = 7.5;
    state.camera.lookAt(cameraTarget.current.set(state.camera.position.x * .35, 1.3, -8.8));
  });
  return <>
    <color attach="background" args={['#e8d5c4']} />
    <hemisphereLight intensity={1.6} color="#fff8f0" groundColor="#9b8866" />
    <directionalLight position={[-5, 11, 5]} intensity={2.5} castShadow shadow-mapSize-width={1024} shadow-mapSize-height={1024} color="#ffeacc" />
    <directionalLight position={[6, 6, -14]} intensity={1.4} color="#f5d5b8" />
    <pointLight position={[0, 3, -8]} color="#ffd9a8" intensity={1.2} distance={20} />
    <Ground isPaused={isPaused} />
    {[-8, 8].map(side => <group key={side}>{Array.from({ length: 5 }, (_, i) => <group key={i} position={[side * 7, 0.5, -i * 8]}><mesh position={[0, 1.2, 0]} castShadow><cylinderGeometry args={[0.12, 0.2, 2, 6]} /><meshStandardMaterial color="#7a5c44" roughness={.7} /></mesh><mesh position={[0, 2.6, 0]} castShadow><sphereGeometry args={[0.8, 12, 12]} /><meshStandardMaterial color="#a8925f" roughness={.8} emissive="#a8925f" emissiveIntensity={.15} /></mesh></group>)}</group>)}
    <group ref={gateGroup} position={[0, 0, -25]}>{options.map((option, i) => <Gate key={`${sceneKey}-${option.id}`} option={option} index={i} positionX={lanePositions[i]} active={selectedOptions.some((item) => item.id === option.id)} gateWidth={gateWidth} onChoose={(opt, idx) => { if (isPaused) return; if (multiSelect) { onChoose(opt); } else if (!selected) { setLane(idx); onChoose(opt); } }} />)}</group>
    <Player lane={lane} lanePositions={lanePositions} running={true} isPaused={isPaused} characterId={characterId} />
    <Sparkles count={120} scale={[15, 8, 40]} size={2.8} speed={.25} opacity={.6} color="#f5ede0" position={[0, 3, -11]} />
    <ContactShadows position={[0, -.11, 0]} opacity={.35} scale={9} blur={3} far={5} />
    <Float speed={1.2} rotationIntensity={.1} floatIntensity={.15}><mesh position={[-7, 4.5, -18]}><sphereGeometry args={[.85, 20, 20]} /><meshStandardMaterial color="#fff5e0" emissive="#f5e6d3" emissiveIntensity={.5} /></mesh></Float>
    <Float speed={0.9} rotationIntensity={.08} floatIntensity={.12}><mesh position={[7, 3.8, -20]}><sphereGeometry args={[.6, 16, 16]} /><meshStandardMaterial color="#ffeacc" emissive="#f5d5b8" emissiveIntensity={.4} /></mesh></Float>
  </>;
}

export default function RunnerWorld({ options, selected, multiSelect = false, isPaused = false, onChoose, sceneKey, characterId }) {
  return <div className="runner-world"><Canvas shadows dpr={[1, 1.5]} camera={{ position: [0, 4.3, 7.5], fov: 52 }} gl={{ antialias: true, powerPreference: 'high-performance' }}>
    <Suspense fallback={null}><RunnerScene options={options} selected={selected} multiSelect={multiSelect} isPaused={isPaused} onChoose={onChoose} sceneKey={sceneKey} characterId={characterId} /></Suspense>
  </Canvas></div>;
}
