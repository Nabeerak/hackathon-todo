// Animated Rays Background Component
// Blood Red & Yellow rays emanating from center

"use client";

import { useEffect, useState } from "react";

export default function AnimatedRays() {
  const [dimensions, setDimensions] = useState({
    isMobile: false,
    rayLength: 2000,
    isClient: false,
  });

  useEffect(() => {
    const updateDimensions = () => {
      setDimensions({
        isMobile: window.innerWidth < 768,
        rayLength: Math.sqrt(window.innerWidth ** 2 + window.innerHeight ** 2),
        isClient: true,
      });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);

    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Number of rays: 16 on desktop, 10 on mobile
  const rayCount = dimensions.isMobile ? 10 : 16;
  const rayLength = dimensions.rayLength;

  const rays = Array.from({ length: rayCount }, (_, i) => {
    const angle = (360 / rayCount) * i;
    const isRed = i % 2 === 0;

    return {
      id: i,
      angle,
      color: isRed ? '#8B0000' : '#FFD700',
      opacity: isRed ? 0.35 : 0.25,
    };
  });

  return (
    <div
      className="absolute inset-0 overflow-hidden"
      style={{
        zIndex: 0,
        pointerEvents: 'none',
      }}
    >
      <div
        className="absolute"
        style={{
          top: '50%',
          left: '50%',
          width: `${rayLength * 2}px`,
          height: `${rayLength * 2}px`,
          transform: 'translate(-50%, -50%)',
          animation: 'rotateRays 50s linear infinite',
        }}
      >
        <svg
          width="100%"
          height="100%"
          viewBox={`0 0 ${rayLength * 2} ${rayLength * 2}`}
          style={{
            filter: 'blur(1.5px)',
          }}
        >
          <defs>
            {rays.map((ray) => (
              <linearGradient
                key={`gradient-${ray.id}`}
                id={`ray-gradient-${ray.id}`}
                x1="50%"
                y1="50%"
                x2="100%"
                y2="50%"
              >
                <stop offset="0%" stopColor={ray.color} stopOpacity="0" />
                <stop offset="5%" stopColor={ray.color} stopOpacity={ray.opacity} />
                <stop offset="50%" stopColor={ray.color} stopOpacity={ray.opacity * 0.6} />
                <stop offset="100%" stopColor={ray.color} stopOpacity="0" />
              </linearGradient>
            ))}
          </defs>

          {rays.map((ray) => {
            const centerX = rayLength;
            const centerY = rayLength;
            const startWidth = 3;
            const endWidth = dimensions.isMobile ? 60 : 100;

            // Calculate ray path points
            const angleRad = (ray.angle * Math.PI) / 180;
            const x1 = centerX + Math.cos(angleRad) * 50;
            const y1 = centerY + Math.sin(angleRad) * 50;
            const x2 = centerX + Math.cos(angleRad) * rayLength;
            const y2 = centerY + Math.sin(angleRad) * rayLength;

            // Create trapezoid shape for ray
            const perpAngle = angleRad + Math.PI / 2;
            const path = `
              M ${x1 + Math.cos(perpAngle) * startWidth} ${y1 + Math.sin(perpAngle) * startWidth}
              L ${x2 + Math.cos(perpAngle) * endWidth} ${y2 + Math.sin(perpAngle) * endWidth}
              L ${x2 - Math.cos(perpAngle) * endWidth} ${y2 - Math.sin(perpAngle) * endWidth}
              L ${x1 - Math.cos(perpAngle) * startWidth} ${y1 - Math.sin(perpAngle) * startWidth}
              Z
            `;

            return (
              <path
                key={ray.id}
                d={path}
                fill={`url(#ray-gradient-${ray.id})`}
                opacity={ray.opacity * 1.3}
              />
            );
          })}
        </svg>
      </div>
    </div>
  );
}
