"use client";

import { useState } from 'react';
import { Input } from '@chakra-ui/react'
import {
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Box
} from '@chakra-ui/react'

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
      <div className="w-full max-w-screen-sm p-2" >
        <Accordion allowToggle className="my-3">
          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box textAlign='left'>
                  Tip #1 : Type in the description of the scene for best results
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
              tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
              veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
              commodo consequat.
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box textAlign='left'>
                  Tip #2 : You can search by director name
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
              tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
              veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
              commodo consequat.
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box textAlign='left'>
                  Tip #3 : You can search by movie name
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
              tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
              veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
              commodo consequat.
            </AccordionPanel>
          </AccordionItem>
        </Accordion>
      </div>
    </div>
  );
}
