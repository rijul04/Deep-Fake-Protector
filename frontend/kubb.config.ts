import { defineConfig } from '@kubb/core'
import { pluginOas } from '@kubb/plugin-oas'
import { pluginTs } from '@kubb/plugin-ts'
import { pluginReactQuery } from '@kubb/plugin-react-query'
import { pluginSwr } from '@kubb/plugin-swr'
import { pluginZod } from '@kubb/plugin-zod'
import { pluginMsw } from '@kubb/plugin-msw'
import { pluginClient } from "@kubb/plugin-client";

export default defineConfig({
  root: '.',
  input: {
    path: '../OpenApi.yaml',
  },
  output: {
    path: 'gen/',
    clean: true,
  },
  plugins: [
    pluginOas(),
    pluginTs({
      output: {
        path: 'models',
      },
    }),
    pluginClient({
      client: "axios",
      baseURL: "http://localhost:8000",
    }),
    pluginReactQuery({
      output: {
        path: 'hooks',
      },
    }),
    pluginSwr({
      output: {
        path: 'hooks',
      },
    }),
    pluginZod({
      output: {
        path: 'zod',
      },
    }),
    pluginMsw({
      output: {
        path: 'msw',
      },
    }),
  ],
})
