"use client";

import { useState } from 'react';
import { Button, Code, Input, useToast } from '@chakra-ui/react'
import {
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Box
} from '@chakra-ui/react'
import { ingest, search } from './api/search';
import Image from 'next/image'; // Import if you want to use Next.js' Image component

export default function Home() {
  const [isLoading, setLoading] = useState(false);
  const toast = useToast();

  const handleIngest = async () => {
    setLoading(true);
    try {
      console.log("Making ingestion request")
      const result = await ingest();
      console.log(result)
      toast({
        title: result.message, 
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Ingestion failed',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
    setLoading(false);
  };

  return (
    <div className='flex flex-col items-center pt-10'>
      <div className='flex flex-col items-center'>
        <div className="flex items-center mb-3"> 
          <Image 
            src="/clip.svg" 
            alt="Clip"
            height={50} 
            width={30} 
          />
          <h1 className="text-4xl ml-2">moviesearch</h1> {/* ml-2 for margin-left, adjust as needed */}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-[auto,1fr] gap-4 m-4 w-full max-w-screen-sm">
          <p className="md:col-span-1"> You must ingest before you search to ensure that all the images in your custom directory are present in the vector store</p>
          <Button
            className={`md:col-span-1 justify-self-end ${isLoading ? 'bg-gray-400' : 'bg-blue-500'}`} // Replace with your actual class names
            onClick={handleIngest}
            disabled={isLoading}
          >
          {isLoading ? 'Ingesting...' : 'Ingest'}
        </Button>
        </div>
        <Input className="w-full max-w-screen-sm p-2 border rounded" placeholder="Search for images" /> 
      </div> 
      <div className="w-full max-w-screen-sm" >
        <Accordion allowToggle className="my-3">
          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box textAlign='left'>
                  Tip #1 : Type in the description of the scene
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
                The best results come when you describe the scene you want to see. 
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box textAlign='left'>
                  Tip #2 : Use d="director name" to filter on director name
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
                  Tip #3 : Use a="actor name" to filter on actor name 
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              You can filter on movies that have a specific actor by appending <Code>a=</Code> at the end of your query. It would look something like this
              <Code display="block" whiteSpace="pre" className="my-3">spaceship a="Mark Hamill"</Code>
            </AccordionPanel>
          </AccordionItem>
          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box textAlign='left'>
                  Tip #4 : Use g="genre" to search on genres 
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              You can filter on movies of a specific genre by appending <Code>g=</Code> at the end of your query. It would look something like this
              <Code display="block" whiteSpace="pre" className="my-3">high school g="Comedy"</Code>
            </AccordionPanel>
          </AccordionItem>
          <AccordionItem>
            <h2>
              <AccordionButton>
                <Box textAlign='left'>
                  Tip #5 : Use y="year" to filter on year 
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
              You can filter on movies in a specific year by appending <Code>y=</Code> at the end of your query. It would look something like this
              <Code display="block" whiteSpace="pre" className="my-3">pink y=2023</Code>
            </AccordionPanel>
          </AccordionItem>
        </Accordion>
      </div>
    </div>
  );
}
