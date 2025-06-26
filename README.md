# 🚀 FreeSeekR1-Agent: Your Autonomous AI Assistant for Termux 🤖

## Unleash the Power of AI, Locally and Recursively! ✨

FreeSeekR1-Agent is a cutting-edge AI assistant designed to operate seamlessly within your Termux environment. This intelligent agent is built to tackle a wide array of tasks by **recursively answering and executing function calls until your objective is fully achieved!** Say goodbye to manual intervention and let FreeSeekR1-Agent drive your productivity.

### 🌟 Key Features:                                                                                      
-   **Autonomous Execution:** The agent intelligently breaks down complex tasks and executes a series of tool calls, iterating until the goal is met.
-   **Recursive Problem Solving:** It's designed to think, act, and refine its approach through multiple iterations of tool usage and response generation.
-   **Zero API Key Hassle!** 🎉 Unlike many AI solutions, FreeSeekR1-Agent is designed to be incredibly accessible. It leverages powerful, **API-key-free** tools like DeepSeek API (via `ChatOpenAI` with a compatible `base_url`) and various LangChain Community tools, meaning you can get started without the need for cumbersome API registrations or hidden costs.
-   **Rich Toolset:** Equipped with a diverse set of tools, FreeSeekR1-Agent can interact with your system, fetch information from the web, perform calculations, and much more.
-   **Termux Optimized:** Tailored for the Termux environment, ensuring smooth operation and compatibility with your mobile Linux setup.

### 🛠️ Tools at Your Command:                                                                              
FreeSeekR1-Agent comes packed with a versatile suite of tools to help you get things done:

1.  **`run_command(cmd: str)`**
    *   Executes a single shell command in Termux and returns its output. Perfect for system interactions.

2.  **`read_file(filepath: str)`**
    *   Reads and returns the content of a specified file.

3.  **`write_file(filepath: str, content: str, append: bool = False)`**
    *   Writes or appends content to a file.

4.  **`edit_file(filepath: str, old_code: str, new_code: str)`**
    *   Replaces a specific code fragment (`old_code`) with new code (`new_code`) within a file. Requires exact matching of `old_code`.

5.  **`wikipedia(query: str)`**                                                                               *   Searches for information on Wikipedia based on your query.
                                                                                                          6.  **`create_image(prompt: str, filename: str)`**
    *   Generates an image from a text description (prompt) and saves it to a file. Powered by Pollinations.

7.  **`duckduckgo(query: str)`**
    *   Performs a search on DuckDuckGo for up-to-date information.

8.  **`get_weather_data(latitude: float, longitude: float)`**
    *   Retrieves weather data for specified geographical coordinates.

9.  **`stackoverflow(query: str)`**
    *   Searches for programming-related answers on StackOverflow.

10. **`calculator(expression: str)`**
    *   Evaluates mathematical expressions (e.g., `37593 * 67`, `pi * e`).

11. **`solve_equation(equation_str: str, variable: str = 'x')`**
    *   Solves algebraic equations for a given variable (e.g., `x**2 - 4 = 0`).

12. **`scrape_webpage(url: str)`**
    *   Extracts the textual content of a webpage from a given URL.

13. **`get_git_repo(url: str)`**
    *   Clones a Git repository, extracts its content into a text format, and cleans up temporary files.

14. **`query_wikidata(query: str)`**
    *   Searches for data within Wikidata based on your query.

### 🚀 Get Started:                                                                                       
To begin your journey with FreeSeekR1-Agent, simply run the `ai.py` script in your Termux environment. Ensure you have `config.json` set up (even if empty for DeepSeek API, as it's configured to use a `base_url` that doesn't require a key).

```bash
python ai.py
```

Start interacting with your new autonomous AI assistant today!
