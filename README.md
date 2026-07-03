# Awesome ActionQuick Plugins

ActionQuick 社区插件索引仓库。

## 索引文件

- `index.json` — 插件列表，主程序通过此文件发现和更新插件

## 索引格式

```json
{
  "id": "json-formatter",
  "name": "JSON 格式化",
  "version": "1.0.0",
  "author": "ActionQuick",
  "description": "格式化、压缩、校验 JSON",
  "repo": "https://github.com/action-quick/aq-json-formatter",
  "path": "releases/download/v1.0.0/json-formatter.zip",
  "tags": ["开发", "JSON"]
}
```

| 字段 | 说明 |
|---|---|
| `id` | 插件唯一标识（小写字母+数字+连字符） |
| `name` | 显示名称 |
| `version` | 当前版本号（与 path 中的版本保持一致） |
| `author` | 作者 |
| `description` | 简短描述 |
| `repo` | 插件源码仓库 |
| `path` | 相对于 repo 的下载路径，拼接为 `{repo}/{path}` |
| `tags` | 标签分类 |

## 自动更新

`version` 和 `path` 字段由 GitHub Actions 定时从各插件的最新 release 同步更新。

## 提交新插件

1. Fork 本仓库
2. 在 `index.json` 中添加你的插件信息
3. 提交 Pull Request
