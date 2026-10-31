# AGENTS 指南

## 项目定位
本仓库维护 Surge 远程规则集 `ruleset/*.list`，供 Surge 配置用 `RULE-SET` 引用。每个文件对应 Surge 里的一个策略组，让配置中的规则区保持简短。

## 目录与职责
- `ruleset/ai.list`：AI 服务（Anthropic、Claude、OpenAI、OpenRouter），对应 `AI` 组。
- `ruleset/hk.list`：大文件下载、没有地区限制的服务（Homebrew、GitHub、Python、npm、Docker、Dropbox、T3 Code），对应 `hk` 组。
- `ruleset/us.list`：需要美国出口的服务（Google、YouTube、Gemini、Spotify），对应 `US Apps` 组。
- `ruleset/bybit.list`：Bybit 相关域名，对应 `Bybit` 组，手写维护。
- `scripts/build_rulesets.py`：从开源列表和手写条目合并生成 `ai.list`、`hk.list`、`us.list`，来源和手写条目都在脚本的 `RULESETS` 里。
- `.github/workflows/build-rulesets.yml`：每天北京时间 04:17 运行合并脚本，上游有变化才提交；也可以在 Actions 页面或用 `gh workflow run build-rulesets.yml` 手动触发。
- `AGENTS.md`：协作约定（本文件）。

`ai.list`、`hk.list`、`us.list` 由脚本生成，不要手改；要增删来源或条目，改脚本后本地运行 `python3 scripts/build_rulesets.py` 检查结果再提交，或提交脚本后手动触发工作流。`bybit.list` 直接编辑。任一上游下载失败、为空，或某个列表条目比现有文件少一半以上时，脚本报错且不写入，工作流显示失败，需要查看上游。

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
- 修改生成方式时同步更新本文件。
