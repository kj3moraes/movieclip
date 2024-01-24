"use client";

import { useState } from 'react';
import { Input } from '@chakra-ui/react'

import Image from 'next/image'; // Import if you want to use Next.js' Image component

export default function Home() {
  return (
    <div className='flex flex-col items-center pt-10'>
      <div className="flex items-center mb-3"> 
        <Image 
          src="/clip.svg" 
          alt="Clip"
          height={50} 
          width={30} 
        />
        <h1 className="text-4xl ml-2">moviesearch</h1> {/* ml-2 for margin-left, adjust as needed */}
      </div>

      <Input className="w-full max-w-screen-sm p-2 border rounded" placeholder="Search for images" /> 
    </div>
  );
}
