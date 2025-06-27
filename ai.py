import urllib.request
import json
import math
import os
import subprocess
from typing import Optional, List, Dict, Any

import numexpr
import pollinations
import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools import (
    ShellTool,
    WikipediaQueryRun,
    DuckDuckGoSearchResults,
)
from langchain_community.tools.wikidata.tool import WikidataQueryRun
from langchain_community.utilities import (
    WikipediaAPIWrapper,
    StackExchangeAPIWrapper,
)
from langchain_community.utilities.wikidata import WikidataAPIWrapper
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.shell import BashLexer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markup import escape

from sympy import symbols, Eq, solve, sympify, S
from sympy.parsing.sympy_parser import parse_expr

# ==============================================================================
# 1. Глобальные настройки и инициализация
# ==============================================================================

console = Console()

def load_config() -> Dict[str, Any]:
    """Загружает конфигурацию из файла config.json."""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        console.print(f"[bold red]Ошибка загрузки config.json:[/]{e}")
        console.print("[yellow]Создайте config.json с необходимыми ключами (api_key, model, base_url).[/]")
        exit(1)

CONFIG = load_config()

# ==============================================================================
# 2. Инициализация API и оберток
# ==============================================================================

try:
    # Обертки для API
    WIKIDATA_API_WRAPPER = WikidataAPIWrapper(top_k_results=10, max_response_length=4000)
    WIKIPEDIA_API_WRAPPER = WikipediaAPIWrapper()
    STACKEXCHANGE_API_WRAPPER = StackExchangeAPIWrapper(query_type='all', max_results=10)

    # Инструменты LangChain
    SHELL_TOOL = ShellTool(handle_tool_error=True)
    SEARCH_TOOL = DuckDuckGoSearchResults()
    WIKIDATA_TOOL = WikidataQueryRun(api_wrapper=WIKIDATA_API_WRAPPER)

except Exception as e:
    console.print(f"[bold red]Ошибка инициализации API-оберток:[/]{e}")
    exit(1)


# ==============================================================================
# 3. Определение инструментов (Tools)
# ==============================================================================

@tool
def run_command(cmd: str) -> str:
    """
    Выполняет одну shell-команду в Termux и возвращает ее вывод.
    Используйте эту функцию для выполнения системных команд.
    Например: "ls -l"
    """
    try:
        return SHELL_TOOL.run(cmd)
    except Exception as e:
        return f"Ошибка выполнения команды '{cmd}': {e}"

@tool
def read_file(filepath: str) -> str:
    """Читает и возвращает содержимое указанного файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Ошибка: Файл не найден по пути {filepath}"
    except Exception as e:
        return f"Ошибка чтения файла '{filepath}': {e}"

@tool
def write_file(filepath: str, content: str, append: bool = False) -> str:
    """Записывает или дописывает строку в файл."""
    mode = 'a' if append else 'w'
    try:
        with open(filepath, mode, encoding='utf-8') as f:
            f.write(content)
        action = 'дополнен' if append else 'записан'
        return f"Файл '{filepath}' успешно {action}."
    except Exception as e:
        return f"Ошибка записи в файл '{filepath}': {e}"

@tool
def edit_file(filepath: str, old_code: str, new_code: str) -> str:
    """
    Заменяет один фрагмент кода (old_code) на другой (new_code) в файле.
    Эта функция требует точного совпадения `old_code`.
    """
    try:
        content = read_file(filepath)
        if "Ошибка:" in content:
            return content # Возвращаем ошибку от read_file

        if old_code not in content:
            return f"Ошибка: Исходный фрагмент кода не найден в файле '{filepath}'."

        new_content = content.replace(old_code, new_code, 1)
        write_result = write_file(filepath, new_content)

        if "Ошибка:" in write_result:
            return write_result

        return f"Файл '{filepath}' успешно отредактирован."
    except Exception as e:
        return f"Непредвиденная ошибка при редактировании файла: {e}"

@tool
def wikipedia(query: str) -> str:
    """Ищет информацию в Википедии по заданному запросу."""
    try:
        return WIKIPEDIA_API_WRAPPER.run(query)
    except Exception as e:
        return f"Ошибка при поиске в Wikipedia: {e}"

@tool
def create_image(prompt: str, filename: str) -> str:
    """
    Создает изображение по текстовому описанию (prompt) и сохраняет его в файл.
    """
    try:
        console.print(f"[yellow]Создание изображения по запросу: '{prompt}'...[/]")
        model = pollinations.Image()
        image_data = model(prompt)
        image_data.save(filename)
        console.print(f"[green]Изображение сохранено в {filename}[/]")
        
        if os.path.exists(filename):
            console.print("[bold cyan]Предпросмотр в терминале:[/]")
            os.system(f"chafa {filename}")
        
        return f"Изображение было успешно создано и сохранено как '{filename}'."
    except Exception as e:
        return f"Ошибка создания изображения: {e}"

@tool
def duckduckgo(query: str) -> str:
    """Выполняет поиск в DuckDuckGo для получения актуальной информации. Возвращает результаты с ссылками"""
    try:
        return SEARCH_TOOL.invoke(query)
    except Exception as e:
        return f"Ошибка поиска в DuckDuckGo: {e}"

@tool
def get_weather_data(latitude: float, longitude: float) -> str:
    """Получает данные о погоде для указанных координат."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
        "&daily=temperature_2m_max,temperature_2m_min&hourly=temperature_2m,relative_humidity_2m,"
        "apparent_temperature,rain,showers,snowfall,snow_depth,surface_pressure,cloud_cover,visibility"
        "&current=is_day,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Ошибка получения данных о погоде: {e}"

@tool
def stackoverflow(query: str) -> str:
    """Ищет ответы на вопросы по программированию на StackOverflow."""
    try:
        return STACKEXCHANGE_API_WRAPPER.run(query)
    except Exception as e:
        return f"Ошибка поиска на StackOverflow: {e}"

@tool
def calculator(expression: str) -> str:
    """
    Вычисляет математическое выражение.
    Примеры: '37593 * 67', '37593**(1/5)', 'pi * e'
    """
    try:
        local_dict = {"pi": math.pi, "e": math.e}
        result = numexpr.evaluate(expression.strip(), global_dict={}, local_dict=local_dict)
        return str(result)
    except Exception as e:
        return f"Ошибка вычисления '{expression}': {e}"

@tool
def solve_equation(equation_str: str, variable: str = 'x') -> str:
    """
    Решает алгебраическое уравнение относительно указанной переменной.
    Пример: 'x**2 - 4 = 0'
    """
    try:
        x = symbols(variable)
        if '=' in equation_str:
            lhs_str, rhs_str = equation_str.split('=', 1)
            lhs = parse_expr(lhs_str.strip())
            rhs = parse_expr(rhs_str.strip())
        else:
            lhs = parse_expr(equation_str.strip())
            rhs = 0
        
        equation = Eq(lhs, rhs)
        solutions = solve(equation, x)
        
        if not solutions:
            return "Решений не найдено."
        if solutions == [True]:
             return "Бесконечное множество решений."

        return "; ".join(map(str, solutions))
    except Exception as e:
        return f"Ошибка решения уравнения: {e}"

@tool
def scrape_webpage(url: str) -> str:
    """Извлекает текстовое содержимое веб-страницы по URL."""
    try:
        loader = WebBaseLoader([url])
        docs = loader.load()
        return "".join(doc.page_content for doc in docs)
    except Exception as e:
        return f"Ошибка загрузки страницы '{url}': {e}"

@tool
def get_git_repo(url: str) -> str:
    """
    Клонирует Git-репозиторий, извлекает его содержимое в текстовом виде и удаляет временные файлы.
    """
    repo_dir = "temp_git_repo"
    output_file = "repo_content.txt"
    try:
        console.print(f"[yellow]Клонирование репозитория: {url}...[/]")
        subprocess.run(["git", "clone", url, repo_dir], check=True, capture_output=True, text=True)
        
        console.print("[yellow]Конвертация репозитория в текст...[/]")
        # Предполагается, что скрипт repo2txt.py находится в домашней директории
        repo2txt_path = os.path.expanduser("~/repo2txt.py")
        if not os.path.exists(repo2txt_path):
            print("Ошибка: Скрипт repo2txt.py не найден в ~, скачиваем...")
            url = "https://github.com/pde-rent/repo2txt/blob/main/main.py"
            urllib.request.urlretrieve(url, "~/repo2txt.py")
            
        subprocess.run(
            ["python", repo2txt_path, "-d", repo_dir, "-o", output_file],
            check=True, capture_output=True, text=True
        )
        
        console.print("[yellow]Чтение содержимого...[/]")
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        return content
    except subprocess.CalledProcessError as e:
        return f"Ошибка при работе с Git: {escape(e.stderr)}"
    except Exception as e:
        return f"Непредвиденная ошибка: {escape(str(e))}"
    finally:
        # Очистка
        console.print("[yellow]Очистка временных файлов...[/]")
        if os.path.isdir(repo_dir):
            subprocess.run(["rm", "-rf", repo_dir])
        if os.path.exists(output_file):
            os.remove(output_file)

@tool
def query_wikidata(query: str) -> str:
    """Ищет данные в Wikidata по запросу."""
    try:
        return WIKIDATA_TOOL.run(query)
    except Exception as e:
        return f"Ошибка поиска в Wikidata: {e}"

@tool
def open_url(url):
    """Открывает URL на телефоне пользователя"""
    res = subprocess.run(["termux-open-url", url], capture_output=True, text=True, check=True)
    if res.returncode == 0:
        return f"{url} был успешно открыт"
    else:
        return f"Ошибка: {res.stderr}"


# ==============================================================================
# 4. Обработка вывода и вызовов инструментов
# ==============================================================================

class StreamingOutputHandler(BaseCallbackHandler):
    """Обрабатывает потоковый вывод от LLM, форматируя его для консоли."""
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        console.print(token, end="", style="bold cyan")

def display_tool_call(tool_call: Dict[str, Any]):
    """Красиво отображает вызов инструмента."""
    tool_name = tool_call['name']
    tool_args = tool_call['args']
    panel_content = f"[bold]Инструмент:[/][cyan]{tool_name}[/][bold]Аргументы:[/]"
    
    # Используем Syntax для красивого отображения кода/аргументов
    args_str = json.dumps(tool_args, indent=2, ensure_ascii=False)
    panel_content += str(Syntax(args_str, "json", theme="monokai", line_numbers=True))
    
    console.print(Panel(panel_content, title="[yellow]Вызов инструмента", border_style="yellow"))

def process_tool_calls(tool_calls: List[Dict[str, Any]], tools: List) -> List[ToolMessage]:
    """Выполняет вызовы инструментов и возвращает результаты."""
    tool_messages = []
    tool_map = {t.name: t for t in tools}

    for tool_call in tool_calls:
        display_tool_call(tool_call)
        
        if func := tool_map.get(tool_call['name']):
            try:
                result = func.invoke(tool_call['args'])
                console.print(Panel(
                    f"[bold green]Результат '{tool_call['name']}':[/]{escape(str(result))}",
                    border_style="green",
                    title="[green]Результат"
                ))
                tool_messages.append(ToolMessage(
                    content=str(result),
                    name=tool_call['name'],
                    tool_call_id=tool_call['id']
                ))
            except Exception as e:
                error_message = f"Ошибка при вызове инструмента '{tool_call['name']}': {escape(str(e))}"
                console.print(Panel(error_message, title="[bold red]Ошибка", border_style="red"))
                tool_messages.append(ToolMessage(
                    content=error_message,
                    name=tool_call['name'],
                    tool_call_id=tool_call['id']
                ))
        else:
            error_message = f"Неизвестный инструмент: {tool_call['name']}"
            console.print(f"[bold red]{error_message}[/]")
            tool_messages.append(ToolMessage(
                content=error_message,
                name=tool_call['name'],
                tool_call_id=tool_call['id']
            ))
            
    return tool_messages


# ==============================================================================
# 5. Основной цикл приложения (CLI)
# ==============================================================================

def create_llm_chain(config: Dict[str, Any], tools: List) -> Any:
    """Создает и настраивает цепочку LLM с инструментами."""
    llm = ChatOpenAI(
        api_key=config.get("api_key"),
        model=config.get("model"),
        streaming=True,
        base_url=config.get("base_url"),
        temperature=0.1,
    )
    
    # Системный промпт
    system_prompt = """
Ты — AI ассистент в среде Termux. Твоя задача — помогать пользователю, выполняя задачи шаг за шагом.
- **Один инструмент за раз:** В каждом ответе вызывай не более ОДНОГО инструмента.
- **Последовательность:** Работай по циклу: "ответ -> вызов инструмента -> новый ответ -> вызов инструмента...", пока задача не будет полностью решена.
- **Точность:** Будь предельно точным при работе с файлами и командами.
- **Координаты:** Для погоды используй широту и долготу, округленные до двух знаков после точки (например, 55.75, 37.62 для Москвы).
- **Контекст Termux:** Помни, что ты работаешь в Termux. Адаптируй команды и пути к файлам под эту среду. При поиске ошибок в интернете, фокусируйся на общей части ошибки, а не на специфичных для Termux путях.
- **Думай, прежде чем действовать:** Прежде чем вызвать инструмент, кратко опиши свой план в теге <thinking>.
- **Не выдумывай:** Если не знаешь, как что-то сделать, используй поисковые инструменты.
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    llm_with_tools = llm.bind_tools(tools)
    return prompt | llm_with_tools

def main():
    """Главная функция, запускающая CLI."""
    console.print(Panel.fit(
        "[bold magenta]🤖 AI Ассистент для Termux[/]",
        subtitle="[cyan]📱 + 🐳 + 🦜 = 🔥[/]",
        border_style="blue"
    ))
    console.print("[dim]Введите 'exit' или нажмите Ctrl+D для выхода.[/]")

    session = PromptSession(
        history=FileHistory('.assistant_history'),
        auto_suggest=AutoSuggestFromHistory(),
        lexer=PygmentsLexer(BashLexer),
        style=Style.from_dict({'prompt': 'bold ansigreen', 'input': 'bold'})
    )

    tools = [
        run_command, read_file, write_file, edit_file, wikipedia, create_image,
        duckduckgo, get_weather_data, stackoverflow, calculator, solve_equation,
        scrape_webpage, get_git_repo, query_wikidata, open_url
    ]
    chain = create_llm_chain(CONFIG, tools)
    chat_history = []

    while True:
        try:
            user_input = session.prompt([('class:prompt', '[Ваш запрос] ➤ ')])
            if user_input.lower().strip() in ('exit', 'quit', 'q'):
                break
            if not user_input.strip():
                continue

            console.print("-" * 50)
            chat_history.append(HumanMessage(content=user_input))
            
            max_iterations = 50
            for i in range(max_iterations):
                console.print(f"[bold yellow]Итерация {i+1}/{max_iterations}...[/]")
                
                try:
                    response = chain.invoke(
                        {"messages": chat_history},
                        config=RunnableConfig(callbacks=[StreamingOutputHandler()])
                    )
                except Exception as e:
                    console.print(f"[bold red]Ошибка при вызове модели:[/]")
                    console.print(escape(str(e)))
                    break
                
                console.print() # Новая строка после ответа модели
                
                if response.tool_calls:
                    tool_messages = process_tool_calls(response.tool_calls, tools)
                    chat_history.append(response)
                    chat_history.extend(tool_messages)
                else:
                    chat_history.append(response)
                    console.print(Panel("[bold green]✓ Задача завершена[/]", border_style="green"))
                    break
            else:
                console.print(Panel("[bold yellow]⚠ Достигнут лимит итераций. Если задача не решена, попробуйте переформулировать запрос.[/]", border_style="yellow"))

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            console.print(f"[bold red]Произошла критическая ошибка:[/]")
            console.print(escape(str(e)))
            
    console.print("[bold green]Выход...[/]")

if __name__ == "__main__":
    main()
          
