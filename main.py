import os
import sys
import requests
import json
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.syntax import Syntax  # <--- 关键引入：用于代码高亮

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

# 确保 URL 是纯字符串
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
code_language = "text" # 默认为纯文本

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
                                # === A. 行结束时刻：高亮渲染 ===
                                
                                # 1. 擦除当前行 (清除刚才的打字机 Raw 文本)
                                sys.stdout.write("\r\033[K")
                                
                                # 2. 检测代码块标记 ```
                                if "```" in current_line_buffer:
                                    # 切换状态
                                    in_code_block = not in_code_block
                                    
                                    # 如果是进入代码块，提取语言 (如 ```python -> python)
                                    if in_code_block:
                                        lang_candidate = current_line_buffer.replace("```", "").strip()
                                        code_language = lang_candidate if lang_candidate else "text"
                                    else:
                                        code_language = "text" # 退出代码块
                                    
                                    # 打印分隔线（用一种醒目的颜色）
                                    console.print(Text(current_line_buffer, style="bold magenta"))

                                elif in_code_block:
                                    # === 核心修改：使用 Syntax 进行单行高亮 ===
                                    # 即使只有一行，Pygment 也能识别关键字、字符串和数字
                                    syntax = Syntax(
                                        current_line_buffer, 
                                        code_language, 
                                        theme="monokai", # 推荐 monokai 或 ansi_dark
                                        line_numbers=False,
                                        word_wrap=False,
                                        padding=0,
                                        background_color="default" # 防止背景色太突兀
                                    )
                                    console.print(syntax)
                                
                                else:
                                    # 普通文本：使用 Markdown 渲染
                                    # 注意：为了防止 Markdown 解析器吃掉某些单行格式，有时直接 print Text 也可以
                                    console.print(Markdown(current_line_buffer))

                                # 3. 清空缓冲区
                                current_line_buffer = ""
                            
                            else:
                                # === B. 输入时刻：打字机效果 ===
                                current_line_buffer += char
                                sys.stdout.write(char)
                                sys.stdout.flush()
                                
                except Exception as e:
                    continue
    
    # 处理最后一行
    if current_line_buffer:
        sys.stdout.write("\r\033[K")
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
