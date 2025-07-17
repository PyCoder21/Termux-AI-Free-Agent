"""
tools.py
This is the file with the tools of the AI Agent.
"""
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from io import BytesIO
import urllib.request
import math
import os
import subprocess
from typing import Optional, List, Any, Tuple
import pexpect

import numexpr
import pollinations
import requests
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.utilities import (
    WikipediaAPIWrapper,
    StackExchangeAPIWrapper,
)
from langchain_community.utilities.wikidata import WikidataAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools.wikidata.tool import WikidataQueryRun

# Инициализация оберток API
_wikidata_wrapper = WikidataAPIWrapper(top_k_results=10, max_response_length=4000)
_wikipedia_wrapper = WikipediaAPIWrapper()
_stackexchange_wrapper = StackExchangeAPIWrapper(query_type='all', max_results=10)
_search_tool = DuckDuckGoSearchResults()
_wikidata_tool = WikidataQueryRun(api_wrapper=_wikidata_wrapper)

def read_file(filepath: str) -> str:
    """Читает и возвращает содержимое указанного файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Ошибка: Файл не найден по пути {filepath}"
    except Exception as e:
        return f"Ошибка чтения файла '{filepath}': {e}"

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

def edit_file(filepath: str, old_snippet: str, new_snippet: str) -> str:
    """Заменяет фрагмент кода на другой в файле"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if old_snippet not in content:
            return f"Ошибка: Исходный фрагмент не найден в файле '{filepath}'"

        new_content = content.replace(old_snippet, new_snippet, 1)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"Файл '{filepath}' успешно отредактирован"
    except Exception as e:
        return f"Ошибка редактирования: {str(e)}"

def wikipedia(query: str) -> str:
    """Ищет информацию в Википедии по заданному запросу."""
    try:
        return _wikipedia_wrapper.run(query)
    except Exception as e:
        return f"Ошибка при поиске в Wikipedia: {e}"

def create_image(prompt: str, filename: str) -> str:
    """Создает изображение по текстовому описанию и сохраняет его в файл."""
    try:
        model = pollinations.Image()
        image_data = model(prompt)
        image_data.save(filename)
        return f"Изображение сохранено в {filename}"
    except Exception as e:
        return f"Ошибка создания изображения: {e}"

def duckduckgo(query: str) -> str:
    """Выполняет поиск в DuckDuckGo для получения актуальной информации."""
    try:
        return _search_tool.invoke(query)
    except Exception as e:
        return f"Ошибка поиска в DuckDuckGo: {e}"

def get_weather_data(latitude: float, longitude: float) -> str:
    """Получает данные о погоде для указанных координат."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
        "&daily=temperature_2m_max,temperature_2m_min&hourly=temperature_2m,relative_humidity_2m,"
        "apparent_temperature,rain,showers,snowfall,snow_depth,surface_pressure,cloud_cover,visibility"
        "&current=is_day,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
    )
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Ошибка получения данных о погоде: {e}"

def stackoverflow(query: str) -> str:
    """Ищет ответы на вопросы по программированию на StackOverflow."""
    try:
        return _stackexchange_wrapper.run(query)
    except Exception as e:
        return f"Ошибка поиска на StackOverflow: {e}"

def calculator(expression: str) -> str:
    """Вычисляет математическое выражение. Примеры: '37593 * 67', 'pi * e'"""
    try:
        local_dict = {"pi": math.pi, "e": math.e}
        result = numexpr.evaluate(expression.strip(), global_dict={}, local_dict=local_dict)
        return str(result)
    except Exception as e:
        return f"Ошибка вычисления '{expression}': {e}"

def solve_equation(equation_str: str, variable: str = 'x') -> str:
    """Решает алгебраическое уравнение относительно указанной переменной."""
    from sympy import symbols, Eq, solve
    from sympy.parsing.sympy_parser import parse_expr
    
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

def scrape_webpage(url: str) -> str:
    """Извлекает текстовое содержимое веб-страницы по URL."""
    try:
        loader = WebBaseLoader([url])
        docs = loader.load()
        return "".join(doc.page_content for doc in docs)
    except Exception as e:
        return f"Ошибка загрузки страницы '{url}': {e}"

def get_git_repo(url: str) -> str:
    """Клонирует Git-репозиторий и извлекает его содержимое."""
    repo_dir = "temp_git_repo"
    output_file = "repo_content.txt"
    try:
        subprocess.run(["git", "clone", url, repo_dir], check=True, capture_output=True, text=True)
        
        repo2txt_path = os.path.expanduser("~/Termux-AI-Free-Agent/repo2txt.py")
        if not os.path.exists(repo2txt_path):
            urllib.request.urlretrieve(
                "https://github.com/pde-rent/repo2txt/blob/main/main.py",
                repo2txt_path
            )
            
        subprocess.run(
            ["python", repo2txt_path, "-d", repo_dir, "-o", output_file],
            check=True, capture_output=True, text=True
        )
        
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        return content
    except subprocess.CalledProcessError as e:
        return f"Ошибка при работе с Git: {e.stderr}"
    except Exception as e:
        return f"Непредвиденная ошибка: {str(e)}"
    finally:
        if os.path.isdir(repo_dir):
            subprocess.run(["rm", "-rf", repo_dir])
        if os.path.exists(output_file):
            os.remove(output_file)

def query_wikidata(query: str) -> str:
    """Ищет данные в Wikidata по запросу."""
    try:
        return _wikidata_tool.run(query)
    except Exception as e:
        return f"Ошибка поиска в Wikidata: {e}"

def open_url(url: str) -> str:
    """Открывает URL на телефоне пользователя."""
    try:
        res = subprocess.run(["termux-open-url", url], capture_output=True, text=True, check=True)
        return f"{url} был успешно открыт" if res.returncode == 0 else f"Ошибка: {res.stderr}"
    except Exception as e:
        return f"Ошибка открытия URL: {str(e)}"

def run_cmd_pexpect(command: str, cwd: Optional[str] = None) -> Tuple[int, str]:
    """Выполняет команду в интерактивной оболочке с помощью pexpect."""
    output = BytesIO()

    def output_callback(b):
        output.write(b)
        return b

    try:
        shell = os.environ.get("SHELL", "/bin/sh")
        if os.path.exists(shell):
            child = pexpect.spawn(shell, args=["-i", "-c", command], encoding="utf-8", cwd=cwd)
        else:
            child = pexpect.spawn(command, encoding="utf-8", cwd=cwd)

        child.interact(output_filter=output_callback)
        child.close()
        return child.exitstatus, output.getvalue().decode("utf-8", errors="replace")
    except (pexpect.ExceptionPexpect, TypeError, ValueError) as e:
        return 1, f"Error running command {command}: {e}"

def ask(question: str) -> str:
    """Задает вопрос пользователю и возвращает ответ."""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.styles import Style
    
    style = Style.from_dict({
        'prompt': 'bold ansigreen',
        'input': 'bold'
    })
    
    session = PromptSession()
    return session.prompt(
        [('class:prompt', f'{question} => Ваш ответ : ')],
        style=style
    )

def ls(path = "."):
    """Выводит список всех файлов и папок в директории"""

    try:
        entries = os.listdir(path)
        entries_info = []
        for entry in sorted(entries):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                entry_type = "directory"
            elif os.path.isfile(full_path):
                entry_type = "file"
            else:
                entry_type = "other"
            entries_info.append({"name": entry, "type": entry_type})

        return {"path": path, "contents": entries_info}

    except Exception as e:
        return {"error": f"Could not list directory '{path}': {e}"}


def get_tools() -> List[Any]:
    """Возвращает список всех инструментов LangChain."""
    from langchain_core.tools import tool
    from inspect import getmembers, isfunction
    import sys
    
    current_module = sys.modules[__name__]
    functions = getmembers(current_module, isfunction)
    
    excluded = {
        'get_tools',
        'output_callback'  # Внутренняя функция run_cmd_pexpect
    }
    
    tools = []
    for name, func in functions:
        if name.startswith('_') or name in excluded:
            continue
        tools.append(tool(func))
    
    return tools
