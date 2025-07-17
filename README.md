# 🚀 Termux-AI-Free-Agent: Your Autonomous AI Assistant for Termux 📱 + 🐳 + 🦜 = 🔥

## Asciinema Demo:

[![Asciinema Demo](https://asciinema.org/a/ghlVT2vpxVOULmGrajcDTUqo6.svg)](https://asciinema.org/a/ghlVT2vpxVOULmGrajcDTUqo6)

## Unleash the Power of AI, Totally free and Recursively! ✨

Termux-AI-Free-Agent is a cutting-edge LangChain 🦜 AI assistant designed to operate seamlessly within your Termux environment. This intelligent agent is built to tackle a wide array of tasks by **recursively answering and executing function calls until your objective is fully achieved!** Say goodbye to manual intervention and let Termux-AI-Free-Agent drive your productivity.

### 🖥️ NEW!!!:

- **Now you can use the qwen version without api keys!!!**
- **Run interactive commands:** Termux-AI-Free-Agent now can run fully interactive commands using pexpect!!!
- **Context compression:** If your context is full, you can use the `/compress` command to replace the dialog history with a detailed summary.
- **Context fullness indicator:** At the end of each response, there is an indicator showing the percentage of context fullness.

### 🌟 Key Features:                                                                                      
-   **Autonomous Execution:** The agent intelligently breaks down complex tasks and executes a series of tool calls, iterating until the goal is met.
-   **Recursive Problem Solving:** It's designed to think, act, and refine its approach through multiple iterations of tool usage and response generation.
-   **Zero cost!** 🎉 Unlike many AI solutions, Termux-AI-Free-Agent is designed to be incredibly accessible. It leverages powerful, **zero-cost** tools like various LangChain Community tools, meaning you can get started without the need for cumbersome API registrations or hidden costs.
-   **Rich Toolset:** Equipped with a diverse set of tools, Termux-AI-Free-Agent can interact with your system, fetch information from the web, perform calculations, and much more.
-   **Termux Optimized:** Tailored for the Termux environment, ensuring smooth operation and compatibility with your mobile Linux setup.

### 🛠️ Tools at Your Command:                                                                              
Termux-AI-Free-Agent can work with files, execute interactive commands, search in DuckDuckgo, Wikipedia, WikiData, and StackOverflow, get the values of expressions, solve equations, get the weather, get the content of web pages, get the weather, open an URL on your phone, ask additional questions, and even generate images.

Here is the complete tool list:

1.  **`run_cmd_pexpect(command, verbose=False, cwd=None)`**
    *   Runs a command interactively.

2.  **`read_file(filepath: str)`**
    *   Reads and returns the content of a specified file.

3.  **`write_file(filepath: str, content: str, append: bool = False)`**
    *   Writes or appends content to a file.

4.  **`edit_file(filepath: str, old_code: str, new_code: str)`**
    *   Replaces a specific code fragment (`old_code`) with new code (`new_code`) within a file. Requires exact matching of `old_code`.

5.  **`wikipedia(query: str)`**
    *   Searches for information on Wikipedia based on your query.

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

15. **`open_url(url: str)`**
    *   Opens an URL on your phone.

16. **`ask(question: str)`**
    *   Ask an additional question.

### 🚀 Get Started:                                                                                       
To begin your journey with Termux-AI-Free-Agent, simply run the install.sh, then run the `ai.py` script in your Termux environment.

**Install :**
```bash
bash install.sh
```

**Run :**
```bash
python ai.py
```

Termux-AI-Free-Agent also has a non-interactive mode :

```bash
python ai.py "What is the weather in Paris today?"
```

**Or you can use the qwen no-auth version :**

```bash
python ai.py --qwen
```

It also has a non-interactive mode.

**Or the GPT-4.5 version: no-auth version :**
```bash
python ai.py --gpt
```

It also has a non-interactive mode.

Start interacting with your new autonomous AI assistant today!
