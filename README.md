# AI Terminal Chat 🚀

这是一个基于 Python 的轻量级终端 AI 聊天工具。它利用 SiliconFlow API（支持 DeepSeek, Qwen 等模型），实现了**流式输出**、**Markdown 渲染**和**代码高亮**，并且针对终端环境进行了防闪烁优化。

## ✨ 特性

- **流式响应**：打字机效果，零延迟。
- **智能渲染**：支持 Markdown 格式，代码高亮（上下文无关）。
- **极速稳定**：采用逐行渲染策略，无闪烁，低 CPU 占用。
- **轻量级**：仅依赖 `rich` 和 `requests`。

## 🛠️ 安装

1. 克隆仓库：
```bash
git clone [https://github.com/你的用户名/ai-terminal-chat.git](https://github.com/你的用户名/ai-terminal-chat.git)
cd ai-terminal-chat
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```



## ⚙️ 配置

你需要一个 [SiliconFlow](https://www.google.com/search?q=https://cloud.siliconflow.cn) 的 API Key。

**Mac/Linux (Fish Shell):**

```fish
set -Ux SF_API_KEY "sk-你的密钥"

```

**Mac/Linux (Bash/Zsh):**

```bash
export SF_API_KEY="sk-你的密钥"

```

## 🚀 使用方法

直接运行脚本即可：

```bash
python3 main.py "写一个 Python 的贪吃蛇游戏"

```

### 推荐：设置别名 (Fish Shell)

在 `~/.config/fish/functions/ag.fish` 中添加：

```fish
function ag
    python3 ~/project/ai-terminal-chat/main.py $argv
end

```

这样就可以直接使用 `ag "你好"` 提问了。

## 📝 许可证

MIT License