"""把开源规则列表和手写条目按策略合并成自有规则集，输出到仓库的 ruleset/。

每个自有列表对应 Surge 里的一个策略组。GitHub Actions 每天运行本脚本，上游有变化时自动提交，
所以不要手改生成结果：增删来源或手写条目时改这里的 RULESETS。bybit.list 手写维护，不由本脚本生成。

保护：任一上游下载失败或为空，或某个列表的条目比现有文件少一半以上，脚本报错退出、不写文件。
"""

from __future__ import annotations

import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "ruleset"
MIN_KEEP_RATIO = 0.5
ZYDOU = "https://raw.githubusercontent.com/zydou/domain-list-community-converter/surge-domain-set"
BM7_CLASH = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash"
BM7_SURGE = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge"
ACL4SSR = "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash"


@dataclass(frozen=True)
class Source:
    """一个来源：上游 URL（kind 为 domain-set 或 rule-set），或手写的规则行。"""

    title: str
    url: str = ""
    kind: str = "rule-set"
    lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class Ruleset:
    filename: str
    description: str
    sources: tuple[Source, ...] = field(default_factory=tuple)


RULESETS = (
    Ruleset(
        "ai.list",
        "AI 服务，Surge 中走 AI 组。Claude 的进程规则只在 macOS 有效，留在配置模板里。",
        (
            Source("Anthropic", f"{ZYDOU}/anthropic.txt", "domain-set"),
            Source("Claude", f"{BM7_CLASH}/Claude/Claude.list"),
            Source("OpenAI", f"{BM7_CLASH}/OpenAI/OpenAI.list"),
            Source("OpenRouter（无公开列表）", lines=("DOMAIN-SUFFIX,openrouter.ai",)),
            Source(
                "Claude / Anthropic 补充",
                lines=(
                    "DOMAIN-KEYWORD,claude",
                    "DOMAIN-KEYWORD,anthropic",
                    "DOMAIN-SUFFIX,datadoghq.com",
                    "IP-ASN,399358,no-resolve",
                    "IP-CIDR,160.79.104.0/23,no-resolve",
                ),
            ),
        ),
    ),
    Ruleset(
        "hk.list",
        "大文件下载、没有地区限制的服务，Surge 中走 hk 组。须放在 Microsoft 规则之前，GitHub 属于微软。",
        (
            Source(
                "Homebrew（原 homebrew.list）",
                lines=(
                    "DOMAIN-SUFFIX,brew.sh",
                    "DOMAIN-SUFFIX,homebrew.org",
                    "DOMAIN-SUFFIX,rubygems.org",
                ),
            ),
            Source("GitHub（含 ghcr.io、githubusercontent.com、npm）", f"{ZYDOU}/github.txt", "domain-set"),
            Source("Python / PyPI", f"{ZYDOU}/python.txt", "domain-set"),
            Source("npm", f"{ZYDOU}/npmjs.txt", "domain-set"),
            Source("Docker", f"{ZYDOU}/docker.txt", "domain-set"),
            Source("Docker 补充", f"{BM7_SURGE}/Docker/Docker.list"),
            Source("Dropbox", f"{ZYDOU}/dropbox.txt", "domain-set"),
            Source(
                "T3 Code（无公开列表）",
                lines=("DOMAIN-SUFFIX,t3.codes", "DOMAIN-SUFFIX,t3coderelay.com"),
            ),
        ),
    ),
    Ruleset(
        "us.list",
        "需要美国出口的服务，Surge 中走 US Apps 组。须放在 BanAD 之后，让广告域名先被拦截。",
        (
            Source("Google", f"{BM7_CLASH}/Google/Google.list"),
            Source("YouTube", f"{ACL4SSR}/Ruleset/YouTube.list"),
            Source("Gemini", f"{BM7_CLASH}/Gemini/Gemini.list"),
            Source("Spotify", f"{BM7_SURGE}/Spotify/Spotify.list"),
        ),
    ),
)


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "surge-ruleset-builder"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def normalize(raw: str, kind: str) -> list[str]:
    """转成 Surge 规则集行。domain-set 中以点开头的是后缀匹配，否则是完整域名。"""
    rules = []
    for line in raw.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("//"):
            continue
        if kind == "domain-set":
            rules.append(f"DOMAIN-SUFFIX,{line[1:]}" if line.startswith(".") else f"DOMAIN,{line}")
        else:
            rules.append(",".join(part.strip() for part in line.split(",")))
    return rules


def covered(rule: str, suffixes: set[str]) -> bool:
    """DOMAIN 或 DOMAIN-SUFFIX 已被同一列表中更短的后缀覆盖时返回 True。"""
    kind, _, value = rule.partition(",")
    if kind not in ("DOMAIN", "DOMAIN-SUFFIX"):
        return False
    labels = value.lower().split(".")
    start = 1 if kind == "DOMAIN-SUFFIX" else 0
    return any(".".join(labels[index:]) in suffixes for index in range(start, len(labels)))


def build(ruleset: Ruleset) -> tuple[str, int]:
    sections: list[tuple[Source, list[str]]] = []
    for source in ruleset.sources:
        rules = normalize(fetch(source.url), source.kind) if source.url else list(source.lines)
        if source.url and not rules:
            raise RuntimeError(f"{ruleset.filename}：来源为空 {source.url}")
        sections.append((source, rules))

    suffixes = {
        rule.split(",", 1)[1].lower()
        for _, rules in sections
        for rule in rules
        if rule.startswith("DOMAIN-SUFFIX,")
    }
    seen: set[str] = set()
    output = [
        f"# {ruleset.filename}：{ruleset.description}",
        "# 由 scripts/build_rulesets.py 生成，GitHub Actions 每天自动更新，不要手改。",
    ]
    total = 0
    for source, rules in sections:
        kept = []
        for rule in rules:
            key = rule.lower()
            if key in seen or covered(rule, suffixes):
                continue
            seen.add(key)
            kept.append(rule)
        output += ["", f"# {source.title}" + (f"：{source.url}" if source.url else "")]
        output += kept or ["# （与前面重复，已全部去除）"]
        total += len(kept)
    return "\n".join(output) + "\n", total


def count_rules(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#"))


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    # 先全部生成并检查，全部通过后才写文件，避免只更新了一部分。
    for ruleset in RULESETS:
        text, total = build(ruleset)
        previous = count_rules(OUTPUT_DIR / ruleset.filename)
        if previous and total < previous * MIN_KEEP_RATIO:
            raise RuntimeError(f"{ruleset.filename}：条目从 {previous} 降到 {total}，疑似上游异常，停止更新")
        results.append((ruleset.filename, text, previous, total))
    for filename, text, previous, total in results:
        (OUTPUT_DIR / filename).write_text(text, encoding="utf-8")
        print(f"{filename}：{previous} → {total} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
