"use client";

import { useState } from 'react';
import { Button, Code, Input, useToast } from '@chakra-ui/react'
import { WarningIcon } from "@chakra-ui/icons"
import {
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Alert,
  AlertIcon,
  Box
} from '@chakra-ui/react'
import { ingest, search_text, SearchResult, baseurl } from './api/search';
import Image from 'next/image'; // Import if you want to use Next.js' Image component
import FileUpload from '@/components/fileupload';

export default function Home() {
  const [isLoading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const toast = useToast();

  // Define the type for the accordion data
  type AccordionTuple = [string, string, JSX.Element];

  // Create the list of accordion data
  const accordionData: AccordionTuple[] = [
    ["Tip #2 : Use d=\"director name\" to filter on director name", "You can filter on movies by a specific director by appending d= at the end of your query. It would look something like this:", <Code key={1} display="block" whiteSpace="pre" className="my-3">spaceship a=&quot;George Lucas&quot;</Code>],
    ["Tip #3 : Use a=\"actor name\" to filter on actor name", "You can filter on movies that have a specific actor by appending a at the end of your query. It would look something like this:", <Code key={2} display="block" whiteSpace="pre" className="my-3">spaceship a=&quot;Mark Hamill&quot;</Code>],
    ["Tip #4 : Use g=\"genre\" to search on genres", "You can filter on movies of a specific genre by appending g at the end of your query. It would look something like this:", <Code key={3} display="block" whiteSpace="pre" className="my-3">high school g=&quot;Comedy&quot;</Code>],
    ["Tip #5 : Use y=\"year\" to filter on year", "You can filter on movies in a specific year by appending y at the end of your query. It would look something like this:", <Code key={4} display="block" whiteSpace="pre" className="my-3">pink y=&quot;2023&quot;</Code>],
    ["Tip #6 : Use m=\"title\" to filter on movie title", "You can filter on movies by title by appending m at the end of your query. It would look something like this:", <Code key={5} display="block" whiteSpace="pre" className="my-3">a movie scene showing a factory m=&quot;Charlie and the Chocolate Factory&quot;</Code>],
  ]; 
  
  // Define this function to set a loading state for ingest.
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
  // Callback function to update search results
  const updateSearchResults = (newResults: SearchResult[]) => {
    setSearchResults(newResults);
    toast({
      title: 'Results updated',
      status: 'success',
      duration: 5000,
      isClosable: true,
    });
  };

  // 
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const handleSearchSubmit = async () => {
    setLoading(true);
    try {
      console.log("Sending query ", searchQuery)
      const results = await search_text(searchQuery);
      updateSearchResults(results); 
    } catch (error: any) {
      toast({
        title: 'Search failed',
        description: error.toString(),
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
        <Alert status='warning'>
        <AlertIcon/>
        <div className="grid grid-cols-1 md:grid-cols-[auto,1fr] gap-4 w-full max-w-screen-sm">
          <p className="md:col-span-1"> You must ingest before you search to ensure that all the images in your custom directory are present in the vector store</p>
          <Button
            className={`md:col-span-1 justify-self-end ${isLoading ? 'bg-gray-400' : 'bg-blue-500'}`} // Replace with your actual class names
            onClick={handleIngest}
            disabled={isLoading}
          >
          {isLoading ? 'Ingesting...' : 'Ingest'}
        </Button>
        </div>
        </Alert>

        {/* Dividing line */}
        <hr className="border-t border-gray-300 w-full max-w-screen-sm my-4" />

        {/* Search bar */}
        <div className="flex w-full max-w-screen-sm">
          <Input
            className="p-4 border rounded-tl rounded-bl flex-grow"
            placeholder="Search for images"
            value={searchQuery}
            onChange={handleSearchChange}
            onKeyDown={event => event.key === 'Enter' && handleSearchSubmit()}
          />
          <Button
            className={`justify-self-end ${isLoading ? 'bg-gray-400' : 'bg-blue-500'} rounded-tr rounded-br`}
            onClick={handleSearchSubmit}
            disabled={isLoading}
          > Search
          </Button>
        </div>
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
                The best results come when you describe the scene you want to see after the text `a movie scene showing ...` 
            </AccordionPanel>
          </AccordionItem>

          {/* Mapping the filter query tips */}
          {accordionData.map(([title, description, codeElement], index) => (
            <AccordionItem key={index}>
              <h2>
                <AccordionButton>
                  <Box textAlign='left'>{title}</Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                {description}
                {codeElement}
              </AccordionPanel>
            </AccordionItem>
          ))}
        </Accordion>
      </div>

      {/* Upload section with 'Upload Image' button aligned to the right */}
      <Box className="flex justify-between items-center max-w-screen-sm my-5">
        <p className="text-left w-max">You can even search by images:</p>
        <FileUpload accept="image/*" onResultsUpdate={updateSearchResults}>
          <Button>
            Upload Image
          </Button>
        </FileUpload>
      </Box>

     
      {/* Conditionally render the no-results icon or the search results */}
      {searchResults.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {searchResults.map(result => (
            <div key={result.pic_id} className="mb-3">
              <Image
                src={result.url_path}
                alt={`Image for ${result.movie_name}`}
                width={300}
                height={300}
              />
              <p>{result.movie_name} - {result.pic_id}</p>
            </div>
          ))}
        </div>
      ) : (
        <Box textAlign="center" my={10}>
          <WarningIcon w={20}></WarningIcon>
          <p>No results found</p>
        </Box>
      )}
      </div>
  );
}
