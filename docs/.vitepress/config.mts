import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Documentation",
  base: '/ifex/',
  description:
    "IFEX is a general interface description and transformation technology to integrate/unify/translate different IDLs, and provide tools and methods to facilitate system integration using popular IPC/RPC protocols, and a variety of deployment technologies.",
  srcExclude: ["README.md"],
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    logo: "/ifex-logo.svg",
    search: {
      provider: "local",
    },
    nav: [
      { text: "Specification", link: "/specification" },
      { text: "Developers manual", link: "/developers-manual" },
      { text: "FAQ", link: "/faq/" },
    ],
    sidebar: {
      "/faq/": {
        base: "/faq/",
        items: [
          {
            text: "FAQ",
            link: "index.md",
          },
          {
            text: "History and renaming",
            link: "/static-history-and-rename.md",
          },
          {
            text: "VSS integration proposal",
            link: "/static-vss_integration_proposal.md",
          },
        ],
      },
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
