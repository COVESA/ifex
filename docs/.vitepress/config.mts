import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Documentation",
  description:
    "IFEX is a general interface description and transformation technology to integrate/unify/translate different IDLs, and provide tools and methods to facilitate system integration using popular IPC/RPC protocols, and a variety of deployment technologies.",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    logo: "./ifex-logo.svg",
    nav: [
      { text: "Home", link: "/" },
      { text: "Specification", link: "/specification" },
      { text: "Developers manual", link: "/developers-manual/index.md" },
      { text: "FAQ", link: "/faq" },
    ],
    search: {
      provider: "local",
    },
    sidebar: {
      "/developers-manual/": {
        base: "/developers-manual/",
        items: [
          {
            text: "Introduction",
            link: "index.md",
          },
          {
            text: "Mapping documents",
            link: "mapping-documents/index.md",
            items: [
              { text: "D-Bus", link: "mapping-documents/d-bus" },
              {
                text: "Protobuf/gRPC",
                link: "mapping-documents/static-mapping-protobuf.md",
              },
            ],
          },
          {
            text: "Datatype mapping",
            link: "static-ifex-type-mapping-howto.md",
          },
          {
            text: "Layer types and schemas",
            link: "static-layer-types.md",
          },
          {
            text: "Generators",
            link: "static-developer-generators.md",
          },
        ],
      },
    },

    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/COVESA/ifex?tab=readme-ov-file",
      },
    ],
  },
});
