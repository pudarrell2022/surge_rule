# AGENTS 指南

## 项目定位
本仓库维护 Surge 远程规则集 `ruleset/*.list`，供 Surge 配置用 `RULE-SET` 引用。每个文件对应 Surge 里的一个策略组，让配置中的规则区保持简短。

## 目录与职责
- `ruleset/ai.list`：AI 服务（Anthropic、Claude、OpenAI、OpenRouter），对应 `AI` 组。
- `ruleset/hk.list`：大文件下载、没有地区限制的服务（Homebrew、GitHub、Python、npm、Docker、Dropbox、T3 Code），对应 `hk` 组。
- `ruleset/us.list`：需要美国出口的服务（Google、YouTube、Gemini、Spotify），对应 `US Apps` 组。
- `ruleset/bybit.list`：Bybit 相关域名，对应 `Bybit` 组，手写维护。
- `AGENTS.md`：协作约定（本文件）。

`ai.list`、`hk.list`、`us.list` 由 Dropbox 中 software 项目的 `list/surge/build_rulesets.py` 从开源列表合并生成，不要在本仓库手改；要增删来源或条目，改脚本后重新生成，再用 `mconfig` 分发到本仓库。`bybit.list` 直接编辑。

## 开发与编辑约定
- 规则文件一行一条，允许空行与以 `#` 开头的说明和来源注释。手写条目中，服务专用域名用 `DOMAIN-SUFFIX,<domain>`，共享服务的具体主机用 `DOMAIN,<host>` 精确匹配。
- 生成的列表保留上游原有的规则类型，可能包含 `DOMAIN-KEYWORD`、`IP-CIDR`、`IP-ASN`、`PROCESS-NAME`、`USER-AGENT`，Surge 都支持；引用时加 `no-resolve`。
- 新增域名前先去重；文件编码使用 UTF-8。

## 常用操作
- 查看仓库文件：`rg --files`
- 检查某规则文件：`sed -n '1,200p' ruleset/<name>.list`
- 在 Surge 中引用：`RULE-SET,https://github.com/pudarrell2022/surge_rule/raw/refs/heads/main/ruleset/<name>.list,<策略组>,no-resolve`

## 测试与验证
提交前至少做以下验证：
- 语法检查：在 Surge 配置中引用后用 `surge-cli --check` 检查配置，再用 `surge-cli rule explain <域名>` 确认命中。
- 内容检查：无重复、无空白噪声、无明显拼写错误。
- 使用验证：将规则接入本地 Surge 配置后确认可正常加载。

## 提交与发布
- 分支策略：当前主分支为 `main`。
- 提交信息建议：`ruleset: add/update <target> domains`。
- 推送前确认远端引用路径稳定（`main/ruleset/*.list`）。

## 安全与边界
- 不在仓库存放密钥、账户信息或私有配置。
- 规则仅描述域名匹配，不应承载一次性调试数据。
- 生成脚本在 software 项目中，修改生成方式时同步更新本文件。
