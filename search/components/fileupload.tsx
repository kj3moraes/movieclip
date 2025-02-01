import React, { useRef } from 'react';
import { InputGroup } from '@chakra-ui/react';
import { search_image } from '@/app/api/search';

interface FileUploadProps {
  accept: string;
  multiple?: boolean;
  children: React.ReactNode;
  onResultsUpdate: (response: any) => void; // Adjust the type of response based on your API's response structure
}

const FileUpload = ({ accept, multiple, children, onResultsUpdate }: FileUploadProps) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log("Called the handleChange function")
    const files = event.target.files;
    if (files && files.length > 0) {
      // Assuming `search_image` function can handle `FileList` directly or adjust accordingly
      const response = await search_image(files); // Modify according to how your API expects the file
      onResultsUpdate(response);
      console.log(response)
    }
  };

  return (
    <InputGroup onClick={() => inputRef.current?.click()}>
      <input
        type="file"
        multiple={multiple}
        hidden
        accept={accept}
        onChange={handleChange}
        ref={inputRef}
      />
      {children}
    </InputGroup>
  );
};

export default FileUpload;
