# Claude Code と AI コーディングエージェント 入門ハンドブック

> 対象読者: ソフトウェアエンジニア(初〜中級)/ AI コーディングツールをこれから本格的に使う人
> ゴール: 「Claude Code」「Vibe Coding」「Coding Agent」「Agentic Loop」という4つのキーワードを、**手を動かして** 理解する
> 進め方: このドキュメントを **上から順に読むだけ** で、概念 → 仕組み → 実装まで一通り体験できます。コードはコピペではなく **自分で写経** することを推奨します。

---

## 目次

1. [この教材で学ぶこと](#1-この教材で学ぶこと)
2. [Claude Code とは何か](#2-claude-code-とは何か)
3. [Claude Code をインストールして触ってみる](#3-claude-code-をインストールして触ってみる)
4. [Vibe Coding という新しい開発スタイル](#4-vibe-coding-という新しい開発スタイル)
5. [Coding Agent(コーディングエージェント)の正体](#5-coding-agentコーディングエージェントの正体)
6. [Agentic Loop:エージェントの心臓部](#6-agentic-loopエージェントの心臓部)
7. [自分で最小の Coding Agent を作る(Python ハンズオン)](#7-自分で最小の-coding-agent-を作るpython-ハンズオン)
8. [Claude Code を「使う」から「設計する」へ](#8-claude-code-を使うから設計するへ)
9. [チェックリストと次のステップ](#9-チェックリストと次のステップ)

---

## 1. この教材で学ぶこと

最近、開発の現場で次のような言葉をよく聞くようになりました。

- **Claude Code**:Anthropic が出しているターミナル上で動く AI 開発ツール
- **Vibe Coding**:自然言語の「雰囲気(vibe)」で指示してアプリを作るスタイル
- **Coding Agent**:自律的にコードを書き、テストし、修正する AI
- **Agentic Loop**:エージェントが「観察 → 計画 → 行動 → 観察…」と繰り返す仕組み

これらは別々の言葉に見えますが、実は **同じ大きな流れの中の異なるレイヤー** です。

```
[ Agentic Loop (理論・パターン) ]
        ↓ 具体化
[ Coding Agent (このパターンに従う AI) ]
        ↓ 製品化
[ Claude Code (Anthropic が作った Coding Agent) ]
        ↓ 使い方
[ Vibe Coding (Claude Code を使う開発スタイル) ]
```

この教材では、**下のレイヤーから上のレイヤーへ** 順に理解していき、最後に「自分で小さなエージェントを書く」ところまで進みます。

> 💡 **学ぶゴール**
> - Claude Code を自分の PC で動かして基本コマンドを使えるようになる
> - なぜ AI が「自律的に」コードを書けるのかを、自分の言葉で説明できる
> - Anthropic SDK を使って **20 行程度の最小エージェント** を自作できる

---

## 2. Claude Code とは何か

### 2.1 一言でいうと

**Claude Code は「ターミナルの中で動く、コードベース全体を理解する AI コーディングツール」** です。

Anthropic(Claude を作っている会社)が公式に提供しています。VS Code の Copilot のような「次の数文字を予測する補完ツール」ではなく、もっと一段抽象度が高い存在です。

### 2.2 従来の AI コーディング支援との違い

|  | 従来の補完ツール(例: 古典的な IntelliSense) | Copilot 系の予測補完 | **Claude Code** |
|---|---|---|---|
| 入力 | カーソル位置の文脈 | 数十〜数百行のコード | プロジェクト全体 + 自然言語 |
| 出力 | 次のトークン | 数行のコード | **複数ファイルへの変更・テスト・コミット** |
| 自律性 | なし | なし | **タスクを分解して順に実行** |
| インターフェース | エディタ内 | エディタ内 | **ターミナル(CLI)** |

ポイントは「**コードベース全体を読んでから動く**」「**複数ステップのタスクをこなす**」「**ターミナル上で動く**」の3つです。

### 2.3 なぜ「ターミナル」なのか

Claude Code がエディタ拡張ではなく CLI を主戦場にしているのには理由があります。

- ターミナルは **言語・フレームワーク・OS に依存しない** 共通インターフェース
- `git`、`npm`、`pytest`、`docker` など、**開発で使うあらゆるコマンドを呼べる**
- AI が「ファイルを読む」「テストを走らせる」「コミットする」を **同じ世界の中で完結** できる

つまり、Claude Code にとってターミナルは「世界全体」なのです。後で出てくる **Agentic Loop** の「行動(action)」をここで実行します。

### 2.4 公式リソース(まず眺めるべきもの)

- 公式: [Claude Code overview](https://www.anthropic.com/claude-code)
- 公式: How Claude Code works(動作原理)
- コース: Claude Code in Action
- 動画: Claude Code Tutorial for Beginners

> 📝 **メモ**:URL は変わる可能性があるので、必ず公式サイトから辿ってください。

---

## 3. Claude Code をインストールして触ってみる

ここからは **手を動かすパート** です。概念だけ読んでも身につかないので、必ず実機でやりましょう。

### 3.1 必要なもの

- macOS / Linux / WSL いずれか
- Node.js(LTS 推奨)
- Anthropic のアカウントと API キー、または Claude Pro/Max 契約

### 3.2 インストール

ターミナルで次を実行します(npm 経由が公式の標準手順)。

```bash
npm install -g @anthropic-ai/claude-code
```

インストール後、適当な空ディレクトリに移動して起動してみます。

```bash
mkdir hello-claude && cd hello-claude
claude
```

初回はログインを求められるので、画面の指示に従って認証してください。

### 3.3 まず投げてみるプロンプト

ログイン後、対話プロンプトが出たら、次のように **自然言語で** 指示します。

```
Python で FizzBuzz を書いて、ファイル fizzbuzz.py に保存してください。
そのあと、3, 5, 15 のときに正しく動くかを確認するテストも追加して。
```

これだけで Claude Code は:

1. `fizzbuzz.py` を作って書く
2. テストファイルを作る
3. 必要なら `python -m pytest` を走らせる
4. 失敗したら修正して再実行する

ということを **連続して** やってくれます。これがまさに「Coding Agent」としての挙動です。

### 3.4 よく使うコマンド/操作

| 操作 | 説明 |
|---|---|
| `/help` | ヘルプ一覧 |
| `/init` | プロジェクトに `CLAUDE.md`(AI 用の説明書)を生成 |
| `/clear` | 会話履歴をリセット |
| `! <cmd>` | ターミナルコマンドをその場で実行 |
| `Esc` | 生成途中の応答を中断 |

最初の一手としておすすめなのが **`/init`** です。これを叩くと、リポジトリのコードを読み込んで `CLAUDE.md`(プロジェクト固有のルールを書いた説明書)を自動生成してくれます。以後、Claude Code はこのファイルを毎回参照するので、**プロジェクト独自の規約を AI に教える** のに便利です。

### 3.5 「触ってみる」課題

次の3つを実際に Claude Code にやらせてみましょう。

1. **新規作成**:「Express の小さな HTTP サーバを作って、`/health` で `{"ok":true}` を返して」
2. **既存改修**:そのサーバに `/echo?msg=hello` を追加して、`msg` をそのまま返すように
3. **テスト**:supertest でこの2つのエンドポイントのテストを書いて、`npm test` で通るところまで

ここで観察してほしいのは「**Claude Code が何をしているか**」です。

- ファイルを **読む** → **書く** → **コマンドを走らせる** → **結果を見て修正する**
- これらを **自分で順番に決めて** 実行している

この「自分で次の手を決めて、実行して、結果を観察して、また次の手を決める」という挙動こそが、後に出てくる **Agentic Loop** です。一旦この感覚を覚えておいてください。

---

## 4. Vibe Coding という新しい開発スタイル

### 4.1 言葉の出所

「Vibe Coding(バイブコーディング)」という言葉は、AI 研究者 **Andrej Karpathy**(OpenAI 共同創業者の一人、元 Tesla AI 部門長)が命名したと言われています。

定義はおおまかにこう:

> コードを一行ずつ書くのではなく、**作りたいものの「雰囲気(vibe)」を自然言語で AI に伝え**、AI が生成したコードに対して受け入れ・修正を繰り返して、アプリを完成させていく開発スタイル。

### 4.2 何が新しいのか

従来の開発:

```
[要件] → [設計] → [人がコードを書く] → [テスト] → [リリース]
```

Vibe Coding:

```
[要件をふんわり伝える]
    ↓
[AI が動くものを生成]
    ↓
[人は "動き" を見て感想/追加要望を返す]
    ↓
[AI が修正]
    ↓ ループ
[だいたい良くなったらリリース]
```

ポイントは「**人が手で書く量が極小** で、**フィードバックループが超高速**」になることです。

### 4.3 メリットと注意点

**メリット**

- プロトタイピングが圧倒的に速い
- プログラミング初学者でもアプリが作れる
- アイディア検証(PoC)に向く

**注意点(エンジニアが特に意識すべき)**

- **コードを読まないと、後で保守できない**
- セキュリティ・パフォーマンス・エッジケースは AI が見落とす
- 仕様が「動いている挙動」に閉じてしまい、ドキュメント化されにくい

> ⚠️ **エンジニアへのアドバイス**
> 業務コードを Vibe Coding で量産するのは危険です。
> **「使い捨てのプロトタイプ」「個人ツール」「学習目的」** までに留め、本番投入する場合は **必ず人間がレビューする** ことを習慣にしてください。

### 4.4 Vibe Coding を実際にやってみる

Claude Code を起動して、次のような **「雰囲気」だけ** のプロンプトを投げてみてください。

```
ローカルで動く簡単なメモアプリを作って。
- 1ファイルの HTML/JS で完結
- メモを追加・削除できる
- localStorage に保存
- 見た目はミニマルでダークモード
```

仕様の細かいところは指定していません。これが Vibe Coding です。

生成された後、次のようにフィードバックを返してみてください:

```
削除ボタンが押しにくいから、各メモにホバーしたときだけ右側に
ゴミ箱アイコンが出るようにして。
```

このやりとりを5〜6回繰り返せば、それなりのアプリが完成します。

---

## 5. Coding Agent(コーディングエージェント)の正体

### 5.1 定義

**Coding Agent** とは:

> 「コードを書く・テストする・デバッグする」を **自律的に** 行う AI ソフトウェア。
> LLM(大規模言語モデル)+ ツール実行能力 + ループ制御 の組み合わせで成り立つ。

Claude Code は **Coding Agent の一実装** です。他にも:

- GitHub Copilot Workspace
- Cursor の Agent モード
- Devin(Cognition AI)
- Aider
- OpenAI Codex CLI

など、多数の実装があります。

### 5.2 普通の LLM 呼び出しとの違い

**ただの LLM 呼び出し**:

```
入力 (プロンプト) → LLM → 出力 (テキスト)
```

これは **1往復で終わり**。コードを書くテキストは出せても、ファイルに保存したりテストを走らせたりはできません。

**Coding Agent**:

```
入力 → LLM → 「次にやる行動」を決める
               ↓
         ツールを実行 (ファイル読み書き / シェル実行 / Web 検索)
               ↓
         結果を LLM に戻す
               ↓
         十分か判断 → 続ける or 終わる
```

つまり Coding Agent = **LLM + ツール + ループ** です。

### 5.3 Coding Agent が持つ典型的な「ツール」

| ツール | 役割 |
|---|---|
| `read_file` | ファイルを読む |
| `write_file` / `edit_file` | ファイルを書く・編集する |
| `run_shell` | シェルコマンドを実行 |
| `search_code` | grep / 検索 |
| `web_search` | Web 検索 |
| `git` 操作 | コミット・diff・ブランチ |

LLM はこれらを「**今この瞬間に何を呼び出すか**」を **自分で決めて** 呼びます。これが「自律性」の正体です。

### 5.4 公式の参考リソース

- Anthropic 公式: [Claude Code Agentic Loop](https://docs.anthropic.com/claude-code/agentic-loop)
- 記事: What is an Agent Loop?
- 記事: Let's Build your Own Agentic Loop
- 動画: What is Agentic RAG?

---

## 6. Agentic Loop:エージェントの心臓部

### 6.1 4つのフェーズ

Agentic Loop は、ロボット工学や強化学習でいう **Sense → Plan → Act → Observe** のサイクルを LLM の世界に持ち込んだものです。

```
        ┌─────────────────┐
        │ 1. Perception   │  ← 環境を観察する(ファイルを読む等)
        │   (知覚)         │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ 2. Planning     │  ← 次の一手を決める(LLM が考える)
        │   (計画)         │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ 3. Action       │  ← 実行(コマンド・ファイル編集)
        │   (行動)         │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ 4. Observation  │  ← 結果を観察(コマンドの stdout 等)
        │   (観察)         │
        └────────┬────────┘
                 │
                 └──── ループ ──── 目的達成まで繰り返し
```

### 6.2 Claude Code 内部での例

たとえば「ユーザーが `bug を直して` と言った」場合、内部ではざっくり次のように回ります:

1. **Perception**: 関連ファイルを read_file で読む
2. **Planning**: LLM が「`utils.py` の関数 X が原因かも。書き換える」と判断
3. **Action**: edit_file で修正、`pytest` を実行
4. **Observation**: pytest の出力を読む。失敗なら戻る、成功なら次へ
5. → 必要な分だけ 1〜4 を繰り返し、最後にユーザーへ報告

このループは **「終了条件」** が必要です。Claude Code の場合は:

- LLM が「もう done」と判断したら止まる
- ユーザーが Esc で割り込んだら止まる
- ループ回数の上限(セーフティ)

### 6.3 なぜループが必要か

LLM は **一発で完璧なコードを書けるとは限らない** ためです。

- テストが落ちる → 修正
- ファイルが想定と違う → 読み直す
- 仕様が曖昧 → ユーザーに聞き返す

これらの「失敗から学んで次の手を変える」を **同じ仕組みで** こなすのが Agentic Loop の強みです。

---

## 7. 自分で最小の Coding Agent を作る(Python ハンズオン)

ここからが本番。**自分の手で Coding Agent を書きます。**

> 🎯 **このセクションのゴール**:
> Anthropic SDK と「Tool Use」機能を使い、**ファイルを読んで質問に答える** 最小エージェントを完成させる。
> コードは全部このドキュメントに書いてあるので、**写経しながら理解** してください。

### 7.1 準備

```bash
# 作業ディレクトリを作る
mkdir mini-agent && cd mini-agent

# Python の仮想環境(任意)
python3 -m venv .venv
source .venv/bin/activate

# Anthropic SDK を入れる
pip install anthropic
```

API キーを環境変数にセットします(`https://console.anthropic.com/` で取得)。

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 7.2 ステップ 1: 「ただの LLM 呼び出し」を書く

まず、ループもツールもない **最もシンプルな呼び出し** を理解しましょう。

ファイル `step1_basic.py` を作成:

```python
# step1_basic.py
# 目的: Anthropic SDK で 1 回だけ LLM を呼び出して結果を表示する

from anthropic import Anthropic

client = Anthropic()  # ANTHROPIC_API_KEY を環境変数から読む

message = client.messages.create(
    model="claude-sonnet-4-6",   # 学習用に十分なモデル
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "FizzBuzz を Python で書いて"}
    ],
)

# LLM の返答は content の中にブロック構造で入っている
for block in message.content:
    if block.type == "text":
        print(block.text)
```

実行:

```bash
python step1_basic.py
```

これは Coding Agent ではありません。**「LLM にテキストを聞いて、テキストを返してもらっただけ」** です。次のステップで「行動」を持たせます。

### 7.3 ステップ 2: ツールを定義する

「LLM が呼べるツール」を Python の関数として用意します。

ファイル `step2_tools.py` を作成:

```python
# step2_tools.py
# 目的: LLM が呼べるツール(関数)を定義し、Tool Use の宣言を作る

import os

# ===== ツールの実装(Python 関数) =====

def read_file(path: str) -> str:
    """指定パスのファイルを読んで中身を返す。"""
    if not os.path.exists(path):
        return f"ERROR: file not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_dir(path: str = ".") -> str:
    """指定パスのファイル一覧を返す。"""
    if not os.path.isdir(path):
        return f"ERROR: not a directory: {path}"
    return "\n".join(sorted(os.listdir(path)))


# ===== Claude に渡す「ツールの説明書」 =====
# LLM はこれを読んで「どのツールをどんな引数で呼ぶか」を決める
TOOLS = [
    {
        "name": "read_file",
        "description": "指定されたパスのテキストファイルを読み、その中身を返す。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "読み込むファイルの相対パスまたは絶対パス",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_dir",
        "description": "指定ディレクトリのファイル一覧を返す。省略時はカレント。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "ディレクトリの相対パス。省略時は '.'",
                }
            },
            "required": [],
        },
    },
]


# ツール名 → Python 関数のマッピング
TOOL_IMPL = {
    "read_file": read_file,
    "list_dir": list_dir,
}


if __name__ == "__main__":
    # 動作確認: ツール単体で呼んでみる
    print(list_dir("."))
```

実行して、ツールが単体で動くことを確認:

```bash
python step2_tools.py
```

ここまではただの Python 関数群。LLM はまだ絡んでいません。

### 7.4 ステップ 3: 1回だけ Tool Use を試す

LLM に「ツールを使うか?使うならどう呼ぶか?」を考えさせます。

ファイル `step3_tool_use_once.py` を作成:

```python
# step3_tool_use_once.py
# 目的: LLM に Tool Use を 1 回だけさせて、その結果を表示する
#       (まだループはしない)

from anthropic import Anthropic
from step2_tools import TOOLS, TOOL_IMPL

client = Anthropic()

# ユーザーからの最初の指示
messages = [
    {"role": "user", "content": "このディレクトリにあるファイル一覧を教えて"}
]

# LLM 呼び出し(ツール使用を許可)
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=TOOLS,        # ← ここがポイント
    messages=messages,
)

print("=== LLM の判断 ===")
print("stop_reason:", response.stop_reason)
for block in response.content:
    print("--- block type:", block.type)
    if block.type == "text":
        print(block.text)
    elif block.type == "tool_use":
        print("呼びたいツール:", block.name)
        print("引数:", block.input)
```

実行すると、`stop_reason` が `tool_use` になり、Claude が `list_dir` を呼びたがっていることが分かります。

これが Agentic Loop の **Planning フェーズ** の出力です。

### 7.5 ステップ 4: ループを回して「自律的に」動かす

いよいよ本物のエージェントを作ります。**ツール呼び出し → 実行 → 結果を LLM に返す → 次の手を決めさせる** のループを実装します。

ファイル `step4_agent.py` を作成:

```python
# step4_agent.py
# 目的: 最小の Coding Agent。
#       ユーザーの指示を達成するまで、ツール呼び出しをループする。

from anthropic import Anthropic
from step2_tools import TOOLS, TOOL_IMPL

client = Anthropic()

SYSTEM_PROMPT = """\
あなたはローカル PC で動くコーディング・アシスタントです。
ユーザーの質問に答えるために、必要であれば与えられたツール
(read_file / list_dir)を自由に呼び出してください。
答えが分かったら、最後に通常のテキストで結論を返してください。
"""


def run_agent(user_input: str, max_steps: int = 10) -> str:
    """ユーザー入力を受け取り、結論文字列を返す。"""

    # 会話履歴。LLM はこれを毎ターン丸ごと見る
    messages = [{"role": "user", "content": user_input}]

    for step in range(max_steps):
        print(f"\n----- Step {step + 1} -----")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # アシスタントの応答(text と tool_use の混在)を履歴に追加
        messages.append({"role": "assistant", "content": response.content})

        # 終了条件: ツールを使わずテキストだけ返してきた = "答えが出た"
        if response.stop_reason == "end_turn":
            final_text = "".join(
                b.text for b in response.content if b.type == "text"
            )
            print("=== 完了 ===")
            return final_text

        # tool_use があれば実行し、結果を user メッセージとして返す
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"🔧 ツール呼び出し: {block.name}({block.input})")
            impl = TOOL_IMPL.get(block.name)
            if impl is None:
                result = f"ERROR: unknown tool {block.name}"
            else:
                try:
                    result = impl(**block.input)
                except Exception as e:
                    result = f"ERROR: {e}"

            # 長すぎる結果は切り詰める(LLM のコンテキスト節約)
            if len(result) > 4000:
                result = result[:4000] + "\n... (truncated)"

            print(f"   ↳ 結果(先頭200字): {result[:200]!r}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        # ツール結果を user ロールで会話に追加 → 次の Step で LLM が読む
        messages.append({"role": "user", "content": tool_results})

    return "(max_steps に到達しました)"


if __name__ == "__main__":
    # 試してみる
    answer = run_agent(
        "このディレクトリのファイル一覧を見て、"
        "step1_basic.py の中身を読んで、何をするスクリプトか日本語で要約して"
    )
    print("\n=== 最終回答 ===")
    print(answer)
```

実行:

```bash
python step4_agent.py
```

出力を見てみてください。例えば次のような流れになるはずです:

1. Step 1: `list_dir(".")` を呼ぶ
2. Step 2: `read_file("step1_basic.py")` を呼ぶ
3. Step 3: テキストで「これは LLM を一回だけ呼ぶサンプルです…」と要約を返して終了

**これが最小の Coding Agent** であり、**これが Agentic Loop の最小実装** です。

### 7.6 ステップ 5: ツールを増やしてみる(自分で挑戦)

ここまでくれば、あとは応用です。次のツールを自分で追加してみましょう:

#### 課題 A: `write_file` を追加

`step2_tools.py` の `TOOLS` と `TOOL_IMPL` に、次の関数を追加してください。

```python
def write_file(path: str, content: str) -> str:
    """指定パスにファイルを書き込む。既存ファイルは上書き。"""
    # TODO: ファイルを書いて、"OK: wrote N bytes to <path>" を返す
    ...
```

ツール定義はこんな形になります(参考):

```python
{
    "name": "write_file",
    "description": "テキストファイルを指定パスに書き込む。",
    "input_schema": {
        "type": "object",
        "properties": {
            "path":    {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["path", "content"],
    },
},
```

その上で、こんな指示を投げてみてください:

```
Hello World を出力する Python スクリプトを hello.py という名前で書いて
```

#### 課題 B: `run_shell` を追加(危険なので注意)

`subprocess.run` でシェルコマンドを実行するツールを書きます。

> ⚠️ **セキュリティ警告**
> シェル実行ツールは LLM が任意のコマンドを撃てるようになります。
> **学習目的の使い捨てディレクトリ以外では使わないこと。**

```python
import subprocess

def run_shell(command: str) -> str:
    """シェルコマンドを実行し、stdout/stderr/returncode を文字列で返す。"""
    # TODO: subprocess.run を timeout 付きで呼ぶ
    # TODO: returncode と stdout/stderr を含む文字列を返す
    ...
```

実装できたら:

```
hello.py を実行してみて、出力を教えて
```

と投げてみてください。エージェントが:

1. `read_file("hello.py")`(必要なら)
2. `run_shell("python hello.py")`
3. 「Hello World と出力されました」と報告

の流れで動いたら成功です。**あなたは今、ミニ Claude Code を作りました。**

---

## 8. Claude Code を「使う」から「設計する」へ

ステップ 7 までで、Claude Code の内部構造が体感できたはずです。
ここからはエンジニアとして **「使う側」+「設計する側」** の視点で押さえておくべきポイントをまとめます。

### 8.1 良いツール設計のコツ

エージェントの性能は **ツールの設計が 7 割** と言って良いです。

- **粒度を揃える**:`read_file` と `read_line` を混ぜない。「1 ツール 1 責務」
- **エラーメッセージを LLM に分かる言葉で返す**:`ENOENT` よりも `file not found: foo.py`
- **副作用のあるツールには確認フラグ**:`force=True` がない限り上書きしない、など
- **出力サイズに上限**:長すぎる結果はトークンを食い潰す

### 8.2 セキュリティ上の注意

Claude Code を業務で使うときに最低限気をつけたいこと:

- **シークレットを読ませない**:`.env`、`credentials.json` は `.claudeignore` 等で除外
- **書き込み権限のスコープを絞る**:CI 環境では本番リポジトリへの直接 push を避ける
- **生成コードのレビュー**:特にネットワーク・認証・SQL・eval 周りは必ず人が見る

### 8.3 `CLAUDE.md` の活用

リポジトリ直下に `CLAUDE.md` を置くと、Claude Code は毎回これを読みます。書くと良いこと:

- プロジェクトのコーディング規約(命名・テスト・コミットメッセージ)
- 「やってはいけないこと」(例: 本番 DB に触らない、`force push` 禁止)
- よく使うコマンド一覧(`make test`、`npm run dev` など)

これは **AI へのオンボーディング資料** だと思って書いてください。

### 8.4 Vibe Coding を「業務に効かせる」コツ

- **PoC・社内ツール・スクリプト** → Vibe Coding でガンガン書く
- **本番プロダクト** → Vibe Coding は **最初のスケッチ** に留め、その後は普通の開発フローに戻す
- **テストファースト**:仕様を Vibe で曖昧にするほど、テストの存在価値が上がる

### 8.5 Agentic Loop を自分のシステムに組み込む

「Claude Code を使う」だけでなく、自社プロダクトにエージェントを組み込みたいときの設計指針:

| 項目 | 推奨 |
|---|---|
| ツール選定 | 5〜10 個までに絞る(増やすほど誤呼び出しが増える) |
| 終了条件 | 「max_steps」「ユーザー中断」「LLM の `end_turn`」の3点で必ず止まる設計 |
| ロギング | どのツールをどう呼んだかを **全部** 記録(後で再現できるように) |
| 観察可能性 | LLM の中間 thought はユーザーに見せる(透明性) |
| 安全装置 | 破壊的操作の前に確認、本番環境では人間承認を挟む |

---

## 9. チェックリストと次のステップ

### 9.1 理解度チェック

次の問いに自分の言葉で答えられたら OK です。

- [ ] Claude Code と GitHub Copilot は何が違うのか?
- [ ] Vibe Coding が向くシーンと向かないシーンは?
- [ ] Coding Agent と「ただの LLM 呼び出し」の決定的な差は?
- [ ] Agentic Loop の 4 つのフェーズを順番に言えるか?
- [ ] エージェントの「終了条件」をどう設計すべきか?

### 9.2 写経したコードを拡張する課題

ステップ 7 の `step4_agent.py` をベースに、次のいずれかに挑戦してみてください。

1. **REPL 化**:`while True:` で複数のターン会話できるようにする(会話履歴を保持)
2. **検索ツール追加**:`search_code(pattern: str)` で `grep -rn` 相当を実装
3. **コミットツール追加**:`git_commit(message)` を作り、エージェントに「変更したらコミットして」と頼む
4. **Web 検索追加**:何らかの Web 検索 API を叩く `web_search` を実装(料金注意)

### 9.3 もう一歩深く学ぶための参照

- 公式: Anthropic Tool Use ガイド
- 公式: Claude Code overview / How Claude Code works
- 公式: Claude Code Agentic Loop
- 記事: What is an Agent Loop?
- 記事: Let's Build your Own Agentic Loop
- ロードマップ: roadmap.sh の Vibe Coding / AI Agents Roadmap

### 9.4 最後に

ここまでお疲れさまでした。

この教材で押さえたのは、**「Claude Code がただの便利ツールではなく、Agentic Loop という設計パターンの上に乗ったソフトウェア」** という見方でした。

この視点を持つと、これから登場する数多くの「コーディング AI」を見るときに、

- どんなツールが組み込まれているか?
- ループの終了条件は?
- どこまで自律で、どこから人間が介入するのか?

という観点で **比較・評価** できるようになります。

そして、必要があれば **自分で作れる** ようにもなります。

Happy hacking with agents! 🚀

---

## 付録 A: 完成版 `step4_agent.py`(まとめ)

写経用にもう一度全文掲載しておきます。ファイル分割が面倒なら、`step2_tools.py` の内容も含めてこの 1 ファイルに統合してもかまいません。

```python
# mini_agent.py — 1ファイル完結版
# 実行: ANTHROPIC_API_KEY=... python mini_agent.py

import os
from anthropic import Anthropic

# ---------- ツール実装 ----------
def read_file(path: str) -> str:
    if not os.path.exists(path):
        return f"ERROR: file not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def list_dir(path: str = ".") -> str:
    if not os.path.isdir(path):
        return f"ERROR: not a directory: {path}"
    return "\n".join(sorted(os.listdir(path)))

TOOL_IMPL = {"read_file": read_file, "list_dir": list_dir}

TOOLS = [
    {
        "name": "read_file",
        "description": "指定されたパスのテキストファイルを読み、その中身を返す。",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "list_dir",
        "description": "指定ディレクトリのファイル一覧を返す。省略時はカレント。",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": [],
        },
    },
]

# ---------- エージェント本体 ----------
SYSTEM = """あなたはローカル PC のコーディング・アシスタントです。
必要なら read_file / list_dir を呼んで情報を集めた上で、
最終的な結論を日本語のテキストで返してください。"""

def run(user_input: str, max_steps: int = 10) -> str:
    client = Anthropic()
    messages = [{"role": "user", "content": user_input}]

    for step in range(max_steps):
        print(f"\n----- Step {step + 1} -----")
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "end_turn":
            return "".join(b.text for b in resp.content if b.type == "text")

        results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            print(f"🔧 {b.name}({b.input})")
            try:
                out = TOOL_IMPL[b.name](**b.input)
            except Exception as e:
                out = f"ERROR: {e}"
            if len(out) > 4000:
                out = out[:4000] + "\n... (truncated)"
            results.append({
                "type": "tool_result",
                "tool_use_id": b.id,
                "content": out,
            })
        messages.append({"role": "user", "content": results})

    return "(max_steps reached)"


if __name__ == "__main__":
    print(run(
        "このディレクトリのファイルを見て、"
        "Python ファイルが何個あるか教えて"
    ))
```

---

## 付録 B: トラブルシューティング

| 症状 | 原因 / 対処 |
|---|---|
| `anthropic.AuthenticationError` | `ANTHROPIC_API_KEY` が未設定。`export ANTHROPIC_API_KEY=...` を確認 |
| `tool_use` が永遠に止まらない | `max_steps` を入れる。ツールの結果が空 or 巨大すぎる可能性あり |
| 文字化け | ファイルを `utf-8` で開いているか確認 |
| 料金が心配 | 学習中は `max_tokens` を小さく、入力も短く。請求コンソールで上限設定 |
| モデル名エラー | 利用可能モデルは時期で変わる。コンソールで確認して差し替え |

---

以上で **「Claude Code と AI コーディングエージェント 入門ハンドブック」** は完了です。
このドキュメントを起点に、ぜひ自分のエージェントを育ててみてください。
