# Slay the Spire 2 数据查询插件 for AstrBot

一个用于在 AstrBot 中查询杀戮尖塔2 Codex 数据库的插件。

## 功能特性

- 查询杀戮尖塔2游戏数据，包括卡牌、遗物、怪物、药水等
- 支持 Spire Codex API 的 19 个不同端点
- 支持详细的信息展示，包含图片（适用于特定端点）
- 中文语言支持（默认：zhs）
- 智能查询解析，支持单复数别名

## 安装方法

1. 确保已安装并运行 [AstrBot](https://github.com/AstrBotDevs/AstrBot)
2. 将 `astrbot_plugin_sts2_data` 文件夹复制到 AstrBot 的 `data/plugins/` 目录
3. 重启 AstrBot 或重新加载插件

## 使用方法

### 命令列表

- `/sts2_help` - 显示帮助信息和可用端点
- `/sts2 <端点> <关键词>` - 从指定端点查询数据

### 使用示例

```
/sts2 cards strike          # 搜索包含 "strike" 的卡牌
/sts2 relics snecko         # 搜索包含 "snecko" 的遗物
/sts2 monsters slime        # 搜索包含 "slime" 的怪物
/sts2 potions strength      # 搜索包含 "strength" 的药水
```

### 可用端点

插件支持以下端点：

| 端点 | 描述 | 详细视图 |
|------|------|----------|
| `cards` | 游戏卡牌 | ✅ 是（包含图片） |
| `relics` | 遗物 | ✅ 是（包含图片） |
| `monsters` | 怪物 | ✅ 是（包含图片） |
| `potions` | 药水 | ✅ 是（包含图片） |
| `enchantments` | 卡牌附魔 | ✅ 是（包含图片） |
| `events` | 游戏事件 | ✅ 是 |
| `powers` | 能力 | ✅ 是（包含图片） |
| `characters` | 角色 | ❌ 仅列表 |
| `encounters` | 遭遇 | ❌ 仅列表 |
| `epochs` | 时代 | ❌ 仅列表 |
| `keywords` | 关键词 | ❌ 仅列表 |
| `orbs` | 法球 | ❌ 仅列表 |
| `afflictions` | 异常状态 | ❌ 仅列表 |
| `modifiers` | 修饰符 | ❌ 仅列表 |
| `achievements` | 成就 | ❌ 仅列表 |
| `acts` | 章节 | ❌ 仅列表 |
| `ascensions` | 进阶 | ❌ 仅列表 |
| `stories` | 故事 | ❌ 仅列表 |
| `intents` | 意图 | ❌ 仅列表 |

**注意**：标记为"详细视图"的端点在查询时会显示详细信息（包括图片）。其他端点仅显示匹配项列表。

### 单复数支持

插件自动处理单复数形式：

- `card` → `cards`
- `relic` → `relics`
- `monster` → `monsters`
- 等等

## API 详情

插件使用 [Spire Codex API](https://spire-codex.com) 获取游戏数据。

### 默认语言

所有查询都使用 `lang=zhs` 参数，支持简体中文。

### 超时设置

API 请求有 10 秒超时限制。

## 开发说明

### 项目结构

```
astrbot_plugin_sts2_data/
├── __init__.py          # 模块导出
├── main.py              # 主插件类
├── constants.py         # 常量和配置
├── models.py           # 数据模型（TypedDict）
├── api_client.py       # HTTP 请求的 API 客户端
├── formatters.py       # 响应格式化器
├── metadata.yaml       # 插件元数据
└── README.md           # 本文件
```

## 致谢

- [AstrBot](https://github.com/AstrBotDevs/AstrBot) - 聊天机器人框架
- [Spire Codex](https://spire-codex.com) - Slay the Spire 2 数据库 API
- Slay the Spire 2 by Mega Crit Games
