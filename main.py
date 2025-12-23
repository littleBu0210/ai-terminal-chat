import os
import sys
import requests
import json
import shutil
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.syntax import Syntax

# 1. 基础配置
api_key = os.getenv("SF_API_KEY")
if not api_key:
    print("❌ 错误: 环境变量 SF_API_KEY 未设置")
    sys.exit(1)

if len(sys.argv) < 2:
    print("请提供问题")
    sys.exit(1)

question = sys.argv[1]
MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"

url = "https://api.siliconflow.cn/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": MODEL_NAME,
    "messages": [{"role": "user", "content": question}],
    "stream": True,
    "max_tokens": 4096,
    "temperature": 0.7
}

console = Console()
console.print(f"[bold blue]🚀 [{MODEL_NAME}] 正在思考...[/bold blue]\n")

current_line_buffer = ""
in_code_block = False
code_language = "text"

# === 新增功能：计算文本在终端的显示宽度 ===
# 中文占2格，英文占1格
def get_display_width(text):
    width = 0
    for char in text:
        if ord(char) > 127: # 简单判断：非ASCII字符算2格
            width += 2
        else:
            width += 1
    return width

# === 新增功能：智能多行清除 ===
def clear_lines(text_buffer):
    # 1. 获取当前终端宽度
    terminal_width = shutil.get_terminal_size().columns
    
    # 2. 计算文本 buffer 实际占用了几行
    display_width = get_display_width(text_buffer)
    num_lines = display_width // terminal_width
    
    # 3. 核心魔法：先回到行首
    sys.stdout.write("\r")
    
    # 4. 如果占了多行，就向上移动光标
    if num_lines > 0:
        # \033[nA 表示光标上移 n 行
        sys.stdout.write(f"\033[{num_lines}A")
    
    # 5. \033[J 表示清除从光标到屏幕底部的所有内容
    sys.stdout.write("\033[J")
    sys.stdout.flush()

try:
    response = requests.post(url, json=payload, headers=headers, stream=True)
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith("data: "):
                json_str = line[6:]
                if json_str == "[DONE]":
                    break
                try:
                    data = json.loads(json_str)
                    content = data['choices'][0]['delta'].get('content', '')
                    
                    if content:
                        for char in content:
                            if char == '\n':
                                # === A. 行结束时刻 ===
                                
                                # 1. 调用新的清除函数，彻底擦除（包括自动折行的部分）
                                clear_lines(current_line_buffer)
                                
                                # 2. 渲染 Markdown / 代码高亮
                                if "```" in current_line_buffer:
                                    in_code_block = not in_code_block
                                    if in_code_block:
                                        lang_candidate = current_line_buffer.replace("```", "").strip()
                                        code_language = lang_candidate if lang_candidate else "text"
                                    else:
                                        code_language = "text"
                                    console.print(Text(current_line_buffer, style="bold magenta"))

                                elif in_code_block:
                                    syntax = Syntax(
                                        current_line_buffer, 
                                        code_language, 
                                        theme="monokai", 
                                        word_wrap=True, # 允许代码块换行
                                        background_color="default"
                                    )
                                    console.print(syntax)
                                
                                else:
                                    console.print(Markdown(current_line_buffer))

                                current_line_buffer = ""
                            
                            else:
                                # === B. 输入时刻 ===
                                current_line_buffer += char
                                sys.stdout.write(char)
                                sys.stdout.flush()
                                
                except Exception as e:
                    continue
    
    # 处理最后一行
    if current_line_buffer:
        clear_lines(current_line_buffer)
        if in_code_block:
             syntax = Syntax(current_line_buffer, code_language, theme="monokai", background_color="default")
             console.print(syntax)
        else:
             console.print(Markdown(current_line_buffer))
        
    print("\n")

except KeyboardInterrupt:
    console.print("\n[yellow]用户中断...[/yellow]")
except Exception as e:
    console.print(f"\n[red]发生错误: {e}[/red]")