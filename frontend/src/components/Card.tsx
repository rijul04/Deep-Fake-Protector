import { Box } from '@chakra-ui/react';
import React, { ReactNode } from 'react';


interface CardProps {
  children: ReactNode;
}



export default function Card({children}: CardProps){
    return (
        <>
            <Box
                border="2px"
                borderColor="purple.300"
                borderRadius="2xl"
                p="10"
                bg="rgba(0,0,0,0.25)"
                _hover={{ borderColor: "purple.200" }}
                // onClick={() => inputRef.current?.click()}
                cursor="pointer"
              >
                {children}
              </Box>
        </>
    )
}