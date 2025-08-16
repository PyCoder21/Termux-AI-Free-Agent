"""
ai.py
This is the project's main file
"""

import sys
import argparse
import json
import os
from typing import List, Dict, Any
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
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
from rich.text import Text
from rich.console import Group
from tools import get_tools

# ==============================================================================
# 1. Глобальные настройки и инициализация
# ==============================================================================


console = Console(log_path=False)


def load_config() -> Dict[str, Any]:
    """Загружает конфигурацию из файла config.json."""
    try:
        with open("/data/data/com.termux/files/home/Termux-AI-Free-Agent/config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        console.print(f"[bold red]Ошибка загрузки config.json:[/]{e}")
        console.print("[yellow]Создайте config.json с необходимыми ключами (model, base_url).[/]")
        sys.exit(1)


CONFIG = load_config()

# Максимальный размер контекста модели в токенах.
# Желательно установить значение, соответствующее вашей модели (например, 128000 для gpt-4-turbo)
MAX_CONTEXT_TOKENS = 128000

# ==============================================================================
# 2. Инициализация API и оберток
# ==============================================================================


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
    
    # Создаем элементы для отображения
    header = Text.from_markup(f"[bold]Инструмент:[/] [cyan]{tool_name}[/]\n[bold]Аргументы:[/]\n")
    args_str = json.dumps(tool_args, indent=2, ensure_ascii=False)
    syntax = Syntax(args_str, "json", theme="monokai", line_numbers=True)

    # Создаем группу элементов для отображения
    content = Group(header, syntax)

    # Печатаем панель
    console.print(Panel(content, title="[yellow]Вызов инструмента", border_style="yellow"))

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
                    f"[bold green]'{tool_call['name']}' : [/]{escape(str(result))}",
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

def create_llm_chain(
    config: Dict[str, Any],
    tools: List,
    is_interactive_mode: bool,
    *,
    use_gpt: bool = False,
    use_qwen: bool = False,
    use_gemini: bool = False,
    use_deepseek: bool = False,
    use_kimi: bool = False
) -> Any:
    use_together = False

    global mo
    """Создает цепочку LLM с инструментами."""
    if use_qwen:
        mo = "Qwen/Qwen3-235B-A22B-fp8-tput"
    elif use_gpt:
        mo = "gpt-5"
    elif use_gemini:
        mo = "google/gemini-2.5-pro-preview-05-06"
    elif use_deepseek:
        mo = "deepseek-ai/DeepSeek-V3"
        use_together = True
    elif use_kimi:
        mo = "moonshotai/Kimi-K2-Instruct"
        use_together = True
    else:
        # Модель из конфига (по умолчанию)
        if config.get("default_model") == "qwen":
            mo = "Qwen/Qwen3-235B-A22B-fp8-tput"
        elif config.get("default_model") == "gpt":
            mo = "gpt-5"
        elif config.get("default_model") == "gemini-2.5-pro":
            mo = "google/gemini-2.5-pro-preview-05-06"
        elif config.get("default_model") == "deepseek-v3":
            mo = "deepseek-ai/DeepSeek-V3"
            use_together = True
        elif config.get("default_model") == "kimi-k2":
            mo = "moonshotai/Kimi-K2-Instruct"
            use_together = True
        else:
            print("set default model to qwen, gpt, gemini-2.5-pro, deepseek-v3 or kimi-k2.")
            sys.exit(1)
    if use_together:
        llm = ChatOpenAI(
            api_key="56c8eeff9971269d7a7e625ff88e8a83a34a556003a5c87c289ebe9a3d8a3d2c",
            model=mo,
            streaming=True,
            base_url="https://api.together.xyz/v1",
            temperature=0.1,
        )
    else:
        llm = ChatOpenAI(
            api_key = "sk-",
            model=mo,
            streaming=True,
            base_url="http://127.0.0.1:61252/v1",
            temperature=0.1,
        )
    # Системный промпт
    system_prompt = f"""
Ты — AI ассистент в среде Termux. Ты используешь ИИ модель {mo}. Твоя задача — помогать пользователю, выполняя задачи шаг за шагом.
- **Один инструмент за раз:** В каждом ответе вызывай не более ОДНОГО инструмента.
- **Последовательность:** Работай по циклу: "ответ -> вызов инструмента -> новый ответ -> вызов инструмента...", пока задача не будет полностью решена.
- **Точность:** Будь предельно точным при работе с файлами и командами.
- **Координаты:** Для погоды используй широту и долготу, округленные до двух знаков после точки (например, 55.75, 37.62 для Москвы).
- **Контекст Termux:** Помни, что ты работаешь в Termux. Адаптируй команды и пути к файлам под эту среду. При поиске ошибок в интернете, фокусируйся на общей части ошибки, а не на специфичных для Termux путях.
- **Не выдумывай:** Если не знаешь, как что-то сделать, используй поисковые инструменты.
- run_cmd_pexpect позволяет выполнять команды ПОЛНОСТЬЮ интерактивно, даже очень интерактивные, но не программы с curses, так как это ломает терминал.

Не используй MarkDown, вместо этого отвечай понятным текстом.
"""
    if not is_interactive_mode:
        system_prompt += """

ВНИМАНИЕ: Ты находишься в НЕИНТЕРАКТИВНОМ режиме. Ты ДОЛЖЕН выполнить задачу полностью, не ожидая уточнений от пользователя. Если ты не знаешь, как поступить, выбери наиболее подходящий вариант и продолжи выполнение. НЕ ЗАДАВАЙ ВОПРОСОВ.
"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages")
    ])
    llm_with_tools = llm.bind_tools(tools)
    return prompt | llm_with_tools

def compress_chat_history(chat_history: List, config: Dict[str, Any]) -> List:
    """Сжимает историю чата с помощью LLM и возвращает новую историю."""
    console.print("[bold yellow]Сжатие истории чата...[/]")

    # Создаем временную модель без потоковой передачи для сжатия
    compressor_llm = ChatOpenAI(
        api_key="sk-",
        model="gpt-5",
        streaming=True,
        base_url="http://127.0.0.1:61252/v1",
        temperature=0.1,
    )

    # Промпт для сжатия
    compression_prompt_text = 'Summarize our conversation up to this point. The summary should be a concise yet comprehensive overview of all key topics, questions, answers, and important details discussed. This summary will replace the current chat history to conserve tokens, so it must capture everything essential to understand the context and continue our conversation effectively as if no information was lost.'
    # Создаем новый шаблон промпта только для сжатия
    compression_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="messages"),
        ("user", compression_prompt_text)
    ])

    chain = compression_prompt | compressor_llm

    try:
        response = chain.invoke({"messages": chat_history})
        summary = response.content
        console.print(Panel(f"[bold green]История успешно сжата.[/]\n[dim]{summary}[/dim]", border_style="green"))
        # Возвращаем новую историю, состоящую из одного сообщения-саммари
        return [HumanMessage(content=f"This is a summary of the previous conversation:\n{summary}")]

    except Exception as e:
        console.print(f"[bold red]Ошибка при сжатии истории: {escape(str(e))}[/]")
        return chat_history # Возвращаем старую историю в случае ошибки



def main():
    """Главная функция, запускающая CLI."""
    # Парсинг аргументов
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='*', help='Запрос для неинтерактивного режима')
    parser.add_argument('--gpt', action='store_true', help='Использовать OpenAI GPT')
    parser.add_argument('--qwen', action='store_true', help='Использовать Qwen')
    parser.add_argument('--gemini', action='store_true', help='Использовать Gemini')
    parser.add_argument('--deepseek', action='store_true', help='Использовать DeepSeek-V3')
    parser.add_argument('--kimi', action='store_true', help='Использовать Kimi-K2 (1 триллион параметров!)')
    args = parser.parse_args()

    is_interactive_mode = not args.query
    initial_query = " ".join(args.query) if args.query else None
    console.print(Panel.fit(
        "[bold magenta]🤖 AI Ассистент для Termux[/]",
        subtitle="[cyan]📱 + 🐳 + 🦜 = 🔥[/]",
        border_style="blue"
    ))

    if is_interactive_mode:
        console.print("[dim]Введите 'exit' или нажмите Ctrl+D для выхода.[/]")
        session = PromptSession(
            history=FileHistory('.assistant_history'),
            auto_suggest=AutoSuggestFromHistory(),
            lexer=PygmentsLexer(BashLexer),
            style=Style.from_dict({'prompt': 'bold ansigreen', 'input': 'bold'})
        )
    else:
        console.print("[bold yellow]Запущен неинтерактивный режим.[/]")
        console.print("[dim]Задача будет выполнена без запросов к пользователю.[/]")
        session = None

    tools = get_tools()
    chain = create_llm_chain(
        CONFIG,
        tools,
        is_interactive_mode,
        use_gpt=args.gpt,
        use_qwen=args.qwen,
        use_gemini=args.gemini,
        use_deepseek=args.deepseek,
        use_kimi=args.kimi
    )
    chat_history = []
    last_prompt_tokens = 0
    console.log("Model:", mo)
    while True:
        try:
            if is_interactive_mode:
                # Показываем заполненность контекста перед вводом
                if last_prompt_tokens > 0:
                    context_percent = min(100.0, (last_prompt_tokens / MAX_CONTEXT_TOKENS) * 100)
                    bar_length = 20
                    filled = int(bar_length * context_percent / 100)
                    indicator = '█' * filled + '░' * (bar_length - filled)
                    console.print(f"[dim]Контекст: [{('green' if context_percent < 70 else 'yellow' if context_percent < 90 else 'red')}]{indicator}[/] [green]{context_percent:.1f}%[/] ({last_prompt_tokens}/{MAX_CONTEXT_TOKENS} токенов)[/]")

                user_input = session.prompt([('class:prompt', '[Ваш запрос] ➤ ')])
                if user_input.lower().strip() in ('exit', 'quit', 'q'):
                    break
                if user_input.lower().strip() == '/compress':
                    if len(chat_history) > 1:
                        chat_history = compress_chat_history(chat_history, CONFIG)
                        last_prompt_tokens = 0 # Сбрасываем токены, чтобы они пересчитались на след. шаге
                    else:
                        console.print("[yellow]История чата слишком коротка для сжатия.[/]")
                    continue

                if not user_input.strip():
                    continue
            else:
                user_input = initial_query
                if not user_input:
                    console.print("[bold red]Ошибка: В неинтерактивном режиме требуется запрос.[/]")
                    break
                console.print(f"[bold green]Запрос:[/][cyan] {user_input}[/]")
                initial_query = None 
            chat_history.append(HumanMessage(content=user_input))
            max_iterations = 50
            for i in range(max_iterations):
                try:
                    response = chain.invoke(
                        {"messages": chat_history},
                        config=RunnableConfig(callbacks=[StreamingOutputHandler()])
                    )
                except Exception as e:
                    console.print("[bold red]Ошибка при вызове модели:[/]")
                    console.print(escape(str(e)))
                    break
                
                console.print()

                # Показ информации о токенах
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    usage = response.usage_metadata
                    prompt = usage.get('prompt_tokens') or usage.get('input_tokens', 0)
                    completion = usage.get('completion_tokens') or usage.get('output_tokens', 0) or usage.get('generated_tokens', 0)
                    total = usage.get('total_tokens', 0)

                    # Если total все еще 0, но есть prompt и completion, посчитаем его
                    if total == 0 and (prompt > 0 or completion > 0):
                        total = prompt + completion
                    
                    last_prompt_tokens = prompt # Сохраняем для следующей итерации

                    console.print(f"[dim]Токены: [green]prompt={prompt} completion={completion} total={total}[/]")
                else:
                    last_prompt_tokens = 0 # Сбрасываем, если инфо нет
                    console.print("[yellow]Информация о токенах недоступна[/]")
                
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

            if not is_interactive_mode:
                break

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            console.print("[bold red]Произошла критическая ошибка:[/]")
            console.print(escape(str(e)))
            
    console.print("[bold green]Выход...[/]")

if __name__ == "__main__":
    main()
