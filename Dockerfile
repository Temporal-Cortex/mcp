FROM debian:trixie-slim AS build
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g @temporal-cortex/cortex-mcp@0.7.9

FROM debian:trixie-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /usr/local/lib/node_modules/@temporal-cortex/cortex-mcp/node_modules/@temporal-cortex/ /opt/cortex/
RUN find /opt/cortex -name cortex-mcp -type f -executable -exec cp {} /usr/local/bin/cortex-mcp \;
RUN useradd -r -u 1000 cortex
USER cortex
ENTRYPOINT ["cortex-mcp"]
