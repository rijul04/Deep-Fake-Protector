"use client";

import Image from "next/image";
import styles from "./page.module.css";
import { useState } from "react";
import { useForm, SubmitHandler, Controller } from "react-hook-form"
import { BodyCreateUploadFileUploadfilePost, useCreateUploadFileUploadfilePost } from "../../gen";
import { Shield } from "lucide-react";
import {
  FormErrorMessage,
  FormLabel,
  FormControl,
  Input,
  Button
} from "@chakra-ui/react";
import { FilePond, registerPlugin } from "react-filepond";
// FilePond css below loading here as this only page so not important
import "filepond/dist/filepond.min.css";
import "filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css";

import FilePondPluginImagePreview from "filepond-plugin-image-preview";
import FilePondPluginFileValidateType from "filepond-plugin-file-validate-type";

registerPlugin(FilePondPluginImagePreview, FilePondPluginFileValidateType);

export default function Home() {
  const uploadMutation = useCreateUploadFileUploadfilePost();
  const [pondFiles, setPondFiles] = useState<any[]>([]);
  // Form Setup Below with React Hook Form + Using ChakraUi to design the stuff
  const {
    control,
    handleSubmit,
    register,
    formState: { errors, isSubmitting }
  } = useForm<{file: File | null}>();

  const onSubmit: SubmitHandler<{ file: File | null }> = (data) => {
    const file = data.file;
    if (!file) return;

    const body: BodyCreateUploadFileUploadfilePost = { file };

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
          <FormLabel htmlFor="file">File Upload</FormLabel>
          <Controller
            name="file"
            control={control}
            rules={{
              required: "Please upload an image",
              // validate: (f) =>
              //   !f || f[0].type.startsWith("image/") || "Only images are allowed",
            }}
            render={({ field }) => (
              <>
                <FilePond
                  files={pondFiles}
                  onupdatefiles={(items) => {
                    setPondFiles(items);
                    const f = items?.[0]?.file as File | undefined;
                    field.onChange(f ?? null);
                  }}
                  acceptedFileTypes={["image/jpeg", "image/png", "image/webp"]}
                  labelIdle='Upload Your Image<br/><span style="opacity:.75">Drag & drop or click to select</span>'
                />
                {errors.file && (
                  <div style={{ color: "#E53E3E", marginTop: 8 }}>
                    {errors.file.message}
                  </div>
                )}
              </>
            )}
          />
          <FormErrorMessage>
            {errors.file && errors.file.message}
          </FormErrorMessage>
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