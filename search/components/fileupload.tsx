import React, { useRef } from 'react';
import { Button, InputGroup } from '@chakra-ui/react';
// import { Icon } from '@chakra-ui/icons'
// import { FiFile } from 'react-icons/fi';

const convertToBase64 = (file: File) => new Promise<string | ArrayBuffer | null>((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
});

type FileUploadProps = {
  accept?: string;
  multiple?: boolean;
  children?: React.ReactNode;
};

const FileUpload: React.FC<FileUploadProps> = ({ accept, multiple, children }) => {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      for (const file of files) {
        const base64 = await convertToBase64(file);
        console.log(base64);
      }
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
