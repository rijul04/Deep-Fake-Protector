"use client";

import Image from "next/image";
import styles from "./page.module.css";
import { useForm, SubmitHandler } from "react-hook-form"
import { BodyCreateUploadFileUploadfilePost, useCreateUploadFileUploadfilePost } from "../../gen";

type Inputs = {
  example: string
  exampleRequired: string
}

export default function Home() {
  const uploadMutation = useCreateUploadFileUploadfilePost();
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<{file: FileList}>()

  const onSubmit: SubmitHandler<{ file: FileList }> = (data) => {
    const file = data.file?.[0];
    if (!file) return;

    const body: BodyCreateUploadFileUploadfilePost = { file };

    uploadMutation.mutate({ data: body }); 
  };

  console.log(watch("file")) // watch input value by passing the name of it


  return (
     /* "handleSubmit" will validate your inputs before invoking "onSubmit" */
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* register your input into the hook by invoking the "register" function */}
      <input type="file" {...register("file")} />

      {/* errors will return when field validation fails  */}
      {errors.file && <span>{errors.file.message}</span>}

      <input type="submit" />
    </form>
  );
}
