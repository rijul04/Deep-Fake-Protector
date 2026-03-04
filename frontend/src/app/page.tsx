"use client";

import Image from "next/image";
import styles from "./page.module.css";
import { useRef, useState } from "react";
import { useForm, SubmitHandler, Controller } from "react-hook-form"
import { BodyCreateUploadFileUploadfilePost, useCreateUploadFileUploadfilePost } from "../../gen";
import { Shield } from "lucide-react";
import {
  FormErrorMessage,
  FormLabel,
  FormControl,
  Input,
  Box,
  HStack,
  Text,
  VStack,
  Button
} from "@chakra-ui/react";

import { Upload, X } from "lucide-react";


export default function Home() {
  const uploadMutation = useCreateUploadFileUploadfilePost();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [name, setName] = useState("");
  // Form Setup Below with React Hook Form + Using ChakraUi to design the stuff
  const {
    control,
    setValue,
    handleSubmit,
    register,
    formState: { errors, isSubmitting }
  } = useForm<{ file: FileList }>();


  const { ref, onChange, ...rest } = register("file", {
    required: "Please select an image",
    // validate: (files) => files?.[0]?.type?.startsWith("image/") || "Only images allowed",
  });

  const clear = () => {
    setName("");
    setValue("file", null as any);
    if (inputRef.current) inputRef.current.value = "";
  };

  // const onSubmit: SubmitHandler<{ file: File | null }> = (data) => {
  //   const file = data.file;
  //   if (!file) return;

  //   const body: BodyCreateUploadFileUploadfilePost = { file };

  //   uploadMutation.mutate({ data: body });
  // };

  const onSubmit: SubmitHandler<{ file: FileList }> = (data) => {
    const file = data.file?.[0];
    if (!file) return;

    const body = { file };
    uploadMutation.mutate({ data: body });
  };


  return (
    <div className={styles.main}>
      <div className={styles.horizontalFlexBox}>
        <Shield className={styles.mIcon} />
        <h1 className={styles.title}>DeepFake Protector</h1>
      </div>
      <p className={styles.subtitle}>Protect your images from AI manipulation with advanced digital fingerprinting and blur protection</p>
      <div className={styles.gap}/>

      

      {/* Form Stuff below again */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <FormControl isInvalid={errors.file ? true : false}>
          {/* <FormLabel htmlFor="file">File Upload</FormLabel> */}
          {/* following for file input */}

          <div className={styles.horizontalFlexBox}>
            <div>
              <input
                  type="file"
                  accept="image/*"
                  hidden
                  {...rest}
                  ref={(el) => { ref(el); inputRef.current = el; }}
                  onChange={(e) => {
                    onChange(e);
                    setName(e.target.files?.[0]?.name ?? "");
                  }}
              />

              <Box
                border="2px dashed"
                borderColor="purple.300"
                borderRadius="2xl"
                p="10"
                bg="rgba(0,0,0,0.25)"
                _hover={{ borderColor: "purple.200" }}
                onClick={() => inputRef.current?.click()}
                cursor="pointer"
              >
                <VStack spacing="3" textAlign="center">
                  <Upload size={44} color="rgb(171, 71, 188)" />
                  <Text fontSize="2xl" fontWeight="800" color="white">
                    Upload Your Image
                  </Text>
                  <Text color="whiteAlpha.700">Click to select</Text>
                  <Text color="whiteAlpha.500" fontSize="sm">Supports: JPG, PNG, WebP</Text>

                  {name ? (
                    <HStack pt="2" spacing="2">
                      <Text color="whiteAlpha.800" fontSize="sm" noOfLines={1} maxW="420px">
                        Selected: {name}
                      </Text>
                      <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); clear(); }} type="button">
                        <X size={18} />
                      </Button>
                    </HStack>
                  ) : null}
                </VStack>
              </Box>
            </div>
            </div>
          {/* above for file input */}
          {/* <FormErrorMessage>
            {errors.file && errors.file.message}
          </FormErrorMessage> */}
        </FormControl>
        <Button mt={4} colorScheme="teal" isLoading={isSubmitting} type="submit">
          Submit
        </Button>
      </form>
    </div>
  )
}


// const uploadMutation = useCreateUploadFileUploadfilePost();
//   const {
//     register,
//     handleSubmit,
//     watch,
//     formState: { errors },
//   } = useForm<{file: FileList}>()

//   const onSubmit: SubmitHandler<{ file: FileList }> = (data) => {
//     const file = data.file?.[0];
//     if (!file) return;

//     const body: BodyCreateUploadFileUploadfilePost = { file };

//     uploadMutation.mutate({ data: body }); 
//   };

//   console.log(watch("file")) // watch input value by passing the name of it


//   return (
//      /* "handleSubmit" will validate your inputs before invoking "onSubmit" */
//     <form onSubmit={handleSubmit(onSubmit)}>
//       {/* register your input into the hook by invoking the "register" function */}
//       <input type="file" {...register("file")} />

//       {/* errors will return when field validation fails  */}
//       {errors.file && <span>{errors.file.message}</span>}

//       <input type="submit" />
//     </form>
//   );