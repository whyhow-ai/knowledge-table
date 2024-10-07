FROM oven/bun
COPY . .
RUN bun install
EXPOSE 3000
CMD ["bun", "start", "--host", "0.0.0.0", "--port", "3000"]