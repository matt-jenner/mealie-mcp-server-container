# Changelog

## 0.2.0 - 2026-06-25

- Vendor the Mealie MCP implementation into this repository instead of downloading upstream source during the container build.
- Preserve upstream MIT license attribution in `UPSTREAM_LICENSE`.
- Build the container from local `src/` implementation code and local project dependencies.
- Fix recipe ingredient/instruction updates for recipes whose existing Mealie metadata contains string time fields or object-shaped categories/tags.
- Add configurable MCP Host/Origin allowlists for DNS-rebinding protection when deployed behind a reverse proxy.
- Add regression coverage for recipe update payload generation, recipe write tools, and Mealie HTTP client handling.
- Update documentation to describe this as an owned Dockerized Mealie MCP server rather than a thin upstream wrapper.
