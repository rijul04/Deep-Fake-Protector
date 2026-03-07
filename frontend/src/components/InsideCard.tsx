import { Box } from "@chakra-ui/react";
import { ReactNode } from "react";


interface InsideCardProps {
  children: ReactNode;
}


export default function InsideCard({children}: InsideCardProps){
    return (
        <>
            <Box
                // border="2px"
                // borderColor="purple.300"
                borderRadius="2xl"
                p="10"
                bg="rgba(0,0,0,0.25)"
                // _hover={{ borderColor: "purple.200" }}
                // onClick={() => inputRef.current?.click()}
                // cursor="pointer"
                >
                {children}
            </Box>
        </>
    )
}