import Image from "next/image";

export function CornerAccents() {
  return (
    <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden">
      {/* Top Left */}
      <div className="absolute top-0 left-0 w-48 md:w-64 h-auto opacity-80">
        <img src="/creeper.png" alt="Corner creeper" className="w-full h-auto object-contain" />
      </div>
      
      {/* Top Right */}
      <div className="absolute top-0 right-0 w-48 md:w-64 h-auto opacity-80" style={{ transform: "scaleX(-1)" }}>
        <img src="/creeper.png" alt="Corner creeper" className="w-full h-auto object-contain" />
      </div>
      
      {/* Bottom Left */}
      <div className="absolute bottom-0 left-0 w-48 md:w-64 h-auto opacity-80" style={{ transform: "scaleY(-1)" }}>
        <img src="/creeper.png" alt="Corner creeper" className="w-full h-auto object-contain" />
      </div>
      
      {/* Bottom Right */}
      <div className="absolute bottom-0 right-0 w-48 md:w-64 h-auto opacity-80" style={{ transform: "scale(-1, -1)" }}>
        <img src="/creeper.png" alt="Corner creeper" className="w-full h-auto object-contain" />
      </div>
    </div>
  );
}
