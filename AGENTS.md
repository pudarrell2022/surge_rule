# AGENTS 指南

## 项目定位
本仓库用于维护 Surge 可复用规则集，核心产物是 `ruleset/*.list` 文本文件，供 Surge 配置中的 `RULE-SET` 远程引用。输入是待收敛的域名清单，输出是符合 Surge 语法的域名后缀规则（如 `DOMAIN-SUFFIX,example.com`）。当前仓库以轻量维护为主，不包含应用程序代码或构建流程。

## 目录与职责
- `ruleset/homebrew.list`：Homebrew 相关域名规则。
- `ruleset/bybit.list`：Bybit 相关域名规则。
- `README.md`：项目简介、使用示例与维护说明。
- `AGENTS.md`：协作与贡献约定（本文件）。

## 开发与编辑约定
- 规则文件一行一条，统一使用 `DOMAIN-SUFFIX,<domain>`。
- 新增域名前先去重，避免重复条目和明显无效域名。
- 优先保持 ASCII 文本；文件编码使用 UTF-8。
- 命名建议：按服务或场景命名，如 `service_name.list`。
- 变更应最小化：仅提交与本次规则维护直接相关的修改。

## 常用操作
- 查看仓库文件：`rg --files`
- 检查某规则文件：`sed -n '1,200p' ruleset/<name>.list`
- 在 Surge 中引用：`RULE-SET,https://raw.githubusercontent.com/<user>/surge_rule/main/ruleset/<name>.list,PROXY`

## 测试与验证
当前仓库未发现自动化测试框架。提交前至少做以下人工验证：
- 语法检查：每行是否满足 `DOMAIN-SUFFIX,<domain>`。
- 内容检查：无重复、无空白噪声、无明显拼写错误。
- 使用验证：将规则接入本地 Surge 配置后确认可正常加载。

## 提交与发布
- 分支策略：当前主分支为 `main`。
- 提交信息建议：`ruleset: add/update <target> domains`。
- 推送前确认远端引用路径稳定（`main/ruleset/*.list`）。

## 安全与边界
- 不在仓库存放密钥、账户信息或私有配置。
- 规则仅描述域名匹配，不应承载一次性调试数据。
- 如需新增自动化脚本，请在 `README.md` 与本文件同步维护说明。
