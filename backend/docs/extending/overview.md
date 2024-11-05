# Extending the Knowledge Table Backend

The Knowledge Table backend is designed for extensibility, allowing developers to add new capabilities and integrate services with ease.

---

## Getting Started

_For full instructions, please see the [Contributing Guide](../CONTRIBUTING.md)._

1. **Create a Branch**: Use Git to create a new branch for your extension.
2. **Develop Your Extension**: Follow guidelines, and add base classes where needed.
3. **Test Your Component**: Implement tests to verify functionality and integration.
4. **Update Configurations and Docs**: Add any new options to config files and provide detailed documentation. (`README.md`, `docs/`, `.env.sample`, etc.)
5. **Submit a Pull Request**: Submit your PR with tests, documentation, and configurations for review.

---

## Areas for Extension

Here are some key areas where we are looking to extend the Knowledge Table backend:

**Document Loaders**

- **New Formats**: Support additional file types (e.g., PDFs, DOCX, HTML).
- **Custom Parsing**: Use external libraries or custom logic for parsing.
- **Document Preprocessing**: Implement chunking, metadata extraction, or content filtering.

**LLM Services**

- **LLM Integrations**: Add support for different LLM providers (e.g., OpenAI, Anthropic).
- **Prompt Strategies**: Modify prompts for specific tasks and use cases.
- **Efficiency**: Optimize usage for cost-effectiveness and performance.

**Vector Databases**

- **Database Options**: Support for additional vector databases (e.g., Pinecone, Weaviate).
- **Indexing and Search**: Implement custom indexing and search strategies.
- **Performance Tuning**: Optimize for handling large datasets.

---

## Principles

1. **Modularity**: Design new components as self-contained units that integrate smoothly without impacting other areas.
2. **Consistency**: Follow established design patterns and conventions to maintain cohesion with existing architecture.
3. **Configuration**: Use environment variables or configuration files for settings, avoiding hardcoding.
4. **Error Handling**: Provide meaningful error messages and logging.
5. **Testing**: Write unit and integration tests covering edge cases and common inputs.
6. **Documentation**: Include usage instructions, configuration steps, and any dependencies.
7. **Performance**: Design for scalability, especially for data-intensive processes.

---

## Contributions and Support

We welcome community contributions! Check the [Contributing Guide](../CONTRIBUTING.md) for more on how to contribute. For help, join our [Discord community](https://discord.gg/PAgGMxfhKd) or contact us at team@whyhow.ai.
