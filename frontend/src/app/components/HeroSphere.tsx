"use client";
import Image from "next/image";

export const HeroSphere = () => {
  return (
    <div className="flex justify-center mt-0 mb-1">
      <div className="relative w-[280px] h-[280px]">
        <Image
          src="/hero-sphere.png"
          alt="AI Core"
          fill
          className="object-contain"
          priority
        />
      </div>
    </div>
  );
};