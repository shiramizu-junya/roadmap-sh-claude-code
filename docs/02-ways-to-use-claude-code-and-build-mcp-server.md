# Claude Code の「使い方の種類」を理解して、自作 MCP サーバーで拡張する

> 対象読者: ソフトウェアエンジニア(初〜中級)/ Claude Code をいろんな環境で使い、さらに **自分で機能を拡張** したい人
> ゴール: 「Claude Code は同じエンジンを CLI / Desktop / IDE / メッセージング / 外部連携という **5つの入口** から使える」ことを理解し、その拡張の共通基盤である **MCP(Model Context Protocol)** を、**自分でサーバーを書いて** 体験する
> 進め方: このドキュメントを **上から順に読むだけ** で、概念 → 各入口 → 共通基盤(MCP)→ 自作サーバーの実装まで一気通貫で学べます。コードは **自分で写経** してください。

> 📌 この教材はシリーズ3冊目です。
> - `00-...`:Claude Code とは何か / エージェントの作り方
> - `01-...`:セットアップ・認証・API課金・自作バックエンド
> - `02-...`(本書):**Claude Code の使い方の種類** と **自作 MCP サーバー** による拡張

---

## 目次

1. [この教材で学ぶこと](#1-この教材で学ぶこと)
2. [全体像:同じエンジン、5つの入口](#2-全体像同じエンジン5つの入口)
3. [入口①:CLI(`claude` コマンド)](#3-入口clauclaude-コマンド)
4. [入口②:Desktop アプリ](#4-入口desktop-アプリ)
5. [入口③:IDE 拡張(VS Code / JetBrains)](#5-入口ide-拡張vs-code--jetbrains)
6. [入口④:Channels(メッセージングと繋ぐ)](#6-入口channelsメッセージングと繋ぐ)
7. [入口⑤:Community Tools(MCP とプラグインで外部連携)](#7-入口community-toolsmcp-とプラグインで外部連携)
8. [ここまでの共通項 = MCP を理解する](#8-ここまでの共通項--mcp-を理解する)
9. [ハンズオン準備:uv で MCP SDK を入れる](#9-ハンズオン準備uv-で-mcp-sdk-を入れる)
10. [ステップ1:最小の MCP サーバーを書く](#10-ステップ1最小の-mcp-サーバーを書く)
11. [ステップ2:Claude Code に接続する](#11-ステップ2claude-code-に接続する)
12. [ステップ3:実用ツールを足す(外部 API を叩く)](#12-ステップ3実用ツールを足す外部-api-を叩く)
13. [ステップ4:HTTP トランスポートで動かす](#13-ステップ4http-トランスポートで動かす)
14. [チェックリストと次のステップ](#14-チェックリストと次のステップ)
15. [付録A:完成版 MCP サーバー全文](#付録a完成版-mcp-サーバー全文)
16. [付録B:トラブルシューティング](#付録bトラブルシューティング)

---

## 1. この教材で学ぶこと

元記事は「**Ways to Use Claude Code(Claude Code の使い方の種類)**」として、6つのトピックを扱っています。

| トピック | ひとことまとめ |
|---|---|
| **Ways to Use Claude Code** | 同じ「エージェントエンジン」を、複数のインターフェースから使える |
| **Claude CLI** | ターミナルで `claude` を叩いて使う基本形 |
| **Claude Code Desktop** | GUI のデスクトップアプリで使う |
| **Code Editor** | VS Code / JetBrains の拡張として、サイドバー + インライン差分で使う |
| **Channels** | Telegram / Discord / iMessage などのメッセージから Claude Code に橋渡し |
| **Community Tools** | MCP やプラグインで GitHub / Slack / Jira / Linear などと連携 |

このうち **前半(CLI / Desktop / IDE)は「どこで使うか」**、**後半(Channels / Community Tools)は「何と繋ぐか」** の話です。そして後半2つの **技術的な共通基盤が MCP(Model Context Protocol)** です。

```
[ 同じエージェントエンジン(研究・コード生成・実行)]
        │
   ┌────┼────┬────────┬───────────┬─────────────┐
   ▼    ▼    ▼        ▼           ▼             
  CLI  Desktop IDE  Channels   Community Tools
                     └────┬────────┘
                          ▼
                   すべて MCP / プラグインで拡張
```

> 💡 **学ぶゴール**
> - 5つの入口それぞれの特徴と「いつ使うか」を説明できる
> - Channels と Community Tools が **なぜ MCP の上に成り立つか** を理解する
> - **テンプレートを使わず**、自分で MCP サーバー(= Claude が呼べる自作ツール群)を書いて Claude Code に接続できる

---

## 2. 全体像:同じエンジン、5つの入口

最初に一番大事な事実を押さえます。

> **どの入口を使っても、中で動いている "エージェントエンジン"(コードを読む・書く・実行する頭脳)は同じ。** 違うのは「人間がどこから話しかけるか(UI)」だけ。

| 入口 | UI | 主な強み | 向いている場面 |
|---|---|---|---|
| **CLI** | ターミナル | 自動化・スクリプト化に最適、軽量 | CI、サーバー上、玄人向け |
| **Desktop** | 独立 GUI アプリ | 複数プロジェクトの管理、ターミナル不要 | 込み入ったプロジェクトの常用 |
| **IDE 拡張** | エディタのサイドバー | インライン差分、ワークスペース自動認識 | コードを書きながら使う |
| **Channels** | スマホのチャットアプリ | 外出先から、URLを公開せず操作 | 移動中・通知駆動の作業 |
| **Community Tools** | (各入口に追加) | GitHub/Slack/Jira 等と連携 | チーム運用・既存ツール統合 |

ポイントは「**入口は気分・場面で選べばよく、覚えることの本体は1つ**」ということ。以下、順に見ていきます。

---

## 3. 入口①:CLI(`claude` コマンド)

最も基本的で、**自動化・スクリプト化に強い** 形です。

### 3.1 特徴

- ターミナルで動くので **言語・OS 非依存**、SSH 先のサーバーでも動く
- シェルスクリプトや CI に組み込みやすい
- 玄人ほど結局これに戻ってくる「素」の形

### 3.2 使い方(おさらい)

```bash
cd ~/your-project   # プロジェクトに入る
claude              # 起動 → 初回はブラウザでログイン
```

> 詳しいインストールと認証は `01-...` を参照。CLI は **Claude サブスク** でも **API キー** でもログインできます。

### 3.3 エンジニア向けの一歩進んだ使い方

CLI ならではの「自動化」を少し体験しましょう。`claude` は対話だけでなく **ワンショット実行** もできます(バージョンにより `-p`/`--print` などのフラグ)。

```bash
# 例:プロンプトを1回だけ渡して結果を受け取る(対話に入らない)
claude -p "このリポジトリのテストコマンドを README から探して教えて"
```

こうした非対話実行は、シェルスクリプトやコミットフック、CI に組み込むときの基本になります。

> 📝 利用可能なフラグは時期で変わるので、`claude --help` で確認する癖をつけましょう。

---

## 4. 入口②:Desktop アプリ

**ターミナルを開かずに GUI で使える** スタンドアロンアプリです。

### 4.1 特徴

- 独立したアプリとして起動(ターミナル不要)
- 複数のプロジェクト/セッションを **GUI で管理** しやすい
- 中身は CLI と同じエージェント(ファイル読み書き・コマンド実行ができる)

### 4.2 いつ使う?

- ターミナルに不慣れ/常用したくない人
- 複数の作業を並行して回し、視覚的に管理したいとき
- 「腰を据えた大きめのプロジェクト」を継続的に進めるとき

> 💡 CLI と Desktop は **排他ではありません**。「サクッと自動化は CLI、じっくり開発は Desktop」のように **使い分け** ればOKです。

---

## 5. 入口③:IDE 拡張(VS Code / JetBrains)

普段のエディタの中で Claude Code を使う形。**今いちばん"開発体験"が良い** ことが多い入口です。

### 5.1 対応エディタ

- **VS Code**
- **JetBrains 系**(IntelliJ IDEA / PyCharm / WebStorm など)

### 5.2 何が嬉しいのか(IDE 統合の本質)

| 機能 | 何が起きるか |
|---|---|
| **グラフィカルなサイドバー** | チャットがエディタ内に常駐 |
| **インライン差分ビューア** | 提案された変更を **既存コードと並べて** レビューできる |
| **ワークスペース自動認識** | 開いているフォルダ・**選択中のファイル**を Claude が自動で把握 |
| **ターミナルエラーの取り込み** | エラーメッセージを **コピペせずに** 文脈として渡せる |

> 🎯 **ここが核心**:IDE 拡張の価値は「**コンテキストの手渡しが要らなくなる**」こと。CLI では「このファイルのここ」と説明する必要がありますが、IDE では Claude が **今あなたが見ている場所** を自動で知っています。

### 5.3 セットアップの考え方

VS Code なら拡張機能をインストール、JetBrains ならプラグインを入れる、というだけ。多くの場合、IDE 内のターミナルで `claude` を起動すると拡張が自動連携します(詳細は公式の VS Code / JetBrains ガイド参照)。

---

## 6. 入口④:Channels(メッセージングと繋ぐ)

ここから「**何と繋ぐか**」の話。Channels は **スマホのチャットアプリから Claude Code を操作** する仕組みです。

### 6.1 どういう仕組みか(超重要)

記事の説明を分解すると、こうなります。

```
[スマホの Telegram/Discord/iMessage]
        │ メッセージ送信
        ▼
[プラットフォームの API]
        ▲ 「新着ある?」と定期的に問い合わせ(ポーリング)
        │
[あなたの PC で動く "チャンネルプラグイン"]   ← ここが橋渡し役
        │ 受け取ったメッセージを転送
        ▼
[ローカルで動いている Claude Code セッション]
        │ 読んで応答
        ▼
[応答がプラグイン経由でスマホへ返る]
```

ポイントを噛み砕くと:

- **プラグインはあなたの PC でローカルに動く**。メッセージ基盤の API を **ポーリング** して新着を拾う
- 拾ったメッセージを **稼働中の Claude Code セッションに「押し込む(push)」**
- だから **インターネットに URL を公開する必要がない**(Webhook 用のサーバーを外部に晒さない)= セキュリティ上の利点
- 設定は **MCP の設定ファイル** に書く。Claude Code がプラグインを **自動で起動** する

> 🔑 **注目**:Channels の設定が「**MCP config に書く**」という点。つまり Channels は **MCP の仕組みの上に乗っている** のです。次の Community Tools も同じ。だから本書の後半で **MCP 自体** を自作して理解します。

### 6.2 いつ使う?

- 外出中にスマホから「あのバグ直しといて」と投げたい
- 長時間回る処理の **完了通知** をチャットで受けたい(イベントを push する用途)

---

## 7. 入口⑤:Community Tools(MCP とプラグインで外部連携)

Claude Code を **GitHub / Slack / Jira / Linear** などの外部サービスと繋ぐ拡張群です。

### 7.1 2つの拡張手段

| 手段 | 何か |
|---|---|
| **MCP(Model Context Protocol)** | Claude に「外部の道具(ツール)やデータ」を標準化された方法で繋ぐプロトコル |
| **プラグイン** | MCP サーバーや設定をパッケージ化して、`/plugin` コマンドで簡単に追加できる仕組み |

### 7.2 具体的にできること(例)

- **GitHub**:Pull Request の管理、Issue 操作
- **Slack**:プロジェクトの進捗を投稿
- **Jira / Linear**:課題(チケット)の作成・追跡

### 7.3 プラグインの追加

Claude Code 内で次のコマンドを使います。

```
/plugin
```

コミュニティ製の拡張も、このコマンド経由で手軽に追加できます。

> 💡 公式・コミュニティ問わず、これらの多くは **MCP サーバー** として実装されています。`Conductor` のような並列実行ツールも、この「外部連携」の文脈に位置づけられます。

---

## 8. ここまでの共通項 = MCP を理解する

> Channels も Community Tools も、根っこは **MCP** です。ここを自分で作れると、Claude Code の拡張の「仕組みそのもの」が手に入ります。

### 8.1 MCP とは何か(一言で)

> **MCP(Model Context Protocol)= 「AI に "道具(ツール)" や "データ(リソース)" を渡すための共通規格」。**

USB に例えるとわかりやすいです。

```
   昔: ツールごとに独自の繋ぎ方(バラバラ)
   今: MCP という共通端子に挿せば、どの AI クライアントからも使える
```

- **MCP サーバー**:道具を提供する側(あなたが書く側)。「天気を取る」「DBを引く」などの **ツール** を公開する
- **MCP クライアント**:道具を使う側。**Claude Code や Claude Desktop がこれ**

### 8.2 MCP サーバーが公開できる3種類

| 種類 | 役割 | 例 |
|---|---|---|
| **Tool(ツール)** | AI が **実行** できる関数(副作用OK) | 「PRを作る」「APIを叩く」 |
| **Resource(リソース)** | AI が **読める** データ | ファイル、設定、DBの内容 |
| **Prompt(プロンプト)** | 再利用できる定型プロンプト | 「コードレビュー用テンプレ」 |

本書では一番重要な **Tool** を中心に作ります。

### 8.3 通信方式(トランスポート)

MCP サーバーと Claude の繋ぎ方は主に2つ。

| トランスポート | 仕組み | いつ使う |
|---|---|---|
| **stdio** | サーバーを **子プロセスとして起動** し、標準入出力でやりとり | ローカルで動かす定番。まずこれ |
| **HTTP (streamable-http)** | HTTP で通信 | リモート/共有、複数クライアントから使うとき |

> 🎯 ここまで来れば「Channels のプラグインがローカルで動いて、URLを公開しない」理由もわかります。**stdio トランスポートで Claude Code が子プロセスとして起動するから** です。

---

## 9. ハンズオン準備:uv で MCP SDK を入れる

ここから手を動かします。**自分で MCP サーバーを書いて、Claude Code に繋ぎます。**

> 🎯 **作るもの**:Claude が呼べる自作ツール群(MCP サーバー)。最初は計算ツール → 次に外部 API を叩く実用ツール、と段階的に育てます。

### 9.1 環境構築(uv)

```bash
# 作業ディレクトリ
mkdir my-mcp-server && cd my-mcp-server

# プロジェクト初期化
uv init

# MCP SDK を追加(CLI 補助コマンド付きの extras を入れる)
uv add "mcp[cli]"

# (ステップ3で外部APIを叩くのに使う HTTP クライアント)
uv add httpx
```

| パッケージ | 役割 |
|---|---|
| `mcp[cli]` | MCP の公式 Python SDK + `mcp` 補助CLI(`mcp install` 等) |
| `httpx` | 外部 API を叩くための HTTP クライアント(ステップ3で使用) |

> 📌 **「テンプレートを使わない」とは**:`create-mcp-server` のようなスキャフォルドや既製テンプレートは使いません。**空の `server.py` にツールを1個ずつ自分で書く** ことで、「MCP サーバー = AI が呼べる自作 API」だと体で理解します。`@mcp.tool()` を付けた関数1つが、API でいう **1エンドポイント** に相当します。

---

## 10. ステップ1:最小の MCP サーバーを書く

まずは外部依存ゼロの **計算ツール** だけのサーバーを作ります。`server.py` を **空から** 作成:

```python
# server.py
# 目的: 最小の MCP サーバー。Claude が呼べるツールを1つ公開する。

from mcp.server.fastmcp import FastMCP

# サーバー本体を作る。引数の文字列が「サーバー名」
mcp = FastMCP("my-first-mcp")


# @mcp.tool() を付けた関数が、Claude から呼べる「ツール」になる。
# - 関数名 → ツール名
# - docstring → ツールの説明(Claude はこれを読んで使い方を判断する)
# - 型ヒント → 入力スキーマ(Claude が正しい引数を組み立てるのに使う)
@mcp.tool()
def add(a: int, b: int) -> int:
    """2つの整数を足し算して返す。"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """2つの整数を掛け算して返す。"""
    return a * b


if __name__ == "__main__":
    # 引数なしの run() は stdio トランスポートで起動する(ローカル定番)
    mcp.run()
```

> 🔍 **ここが MCP の肝**:`@mcp.tool()` を付けるだけで、関数の **名前・docstring・型ヒント** から Claude に渡す「ツールの説明書」が自動生成されます。`01-...` で手書きした `input_schema`(JSON Schema)を、SDK が型ヒントから作ってくれている、という関係です。

### 10.1 単体で起動確認

```bash
uv run server.py
```

stdio サーバーは標準入出力で待ち受けるため、**ターミナルには何も表示されず止まったように見えれば正常** です(Claude などのクライアントが繋ぐのを待っている状態)。`Ctrl-C` で止めてOK。

> 💡 GUI で動作確認したい場合は MCP Inspector が便利です:
> ```bash
> uv run mcp dev server.py
> ```
> ブラウザでツール一覧を見て、手で叩いて試せます。

---

## 11. ステップ2:Claude Code に接続する

書いた MCP サーバーを Claude Code から使えるようにします。方法は2つ。

### 11.1 方法A:`claude mcp add` コマンド(手軽)

プロジェクトのディレクトリで:

```bash
claude mcp add my-first-mcp -- uv run server.py
```

- `my-first-mcp` … Claude 側で表示されるサーバー名(任意)
- `--` の後ろ … **サーバーを起動するコマンド**。ここでは `uv run server.py`

### 11.2 方法B:`.mcp.json` を手で書く(中身を理解する)

プロジェクト直下に `.mcp.json` を作成します。**これが Channels や Community Tools と同じ「MCP config」** です。

```json
{
  "mcpServers": {
    "my-first-mcp": {
      "command": "uv",
      "args": ["run", "server.py"]
    }
  }
}
```

| キー | 意味 |
|---|---|
| `mcpServers` | 登録する MCP サーバーの一覧 |
| `command` | サーバーを起動する実行ファイル(ここでは `uv`) |
| `args` | その引数(`uv run server.py` に分解) |

> 🔑 Claude Code はこの設定を読み、**サーバーを子プロセスとして自動起動**(spawn)します。セクション6で見た Channels プラグインの挙動と同じ仕組みです。

### 11.3 接続を確認する

Claude Code を起動して、スラッシュコマンドで確認:

```
/mcp
```

`my-first-mcp` が **connected** と表示され、`add` / `multiply` ツールが見えれば成功です。実際に試してみましょう:

```
123 と 456 を足して。さっき作った add ツールを使って。
```

Claude が `add` ツールを呼び、`579` を返してくれれば、**あなたの自作ツールが Claude に組み込まれた** ことになります。

---

## 12. ステップ3:実用ツールを足す(外部 API を叩く)

計算だけでは面白くないので、**外部 API を叩く実用ツール** を追加します。「MCP サーバー = 自作 API のゲートウェイ」という感覚を掴むパートです。

ここでは認証不要の公開 API(GitHub の公開ユーザー情報)を例にします。`server.py` に追記:

```python
# server.py に追記

import httpx


@mcp.tool()
def get_github_user(username: str) -> dict:
    """GitHub の公開ユーザー情報(名前・公開リポジトリ数・フォロワー数など)を返す。

    Args:
        username: 調べたい GitHub のユーザー名(例: "torvalds")
    """
    url = f"https://api.github.com/users/{username}"
    try:
        resp = httpx.get(url, timeout=10.0)
    except httpx.RequestError as e:
        return {"error": f"リクエスト失敗: {e}"}

    if resp.status_code == 404:
        return {"error": f"ユーザーが見つかりません: {username}"}
    if resp.status_code != 200:
        return {"error": f"予期しないステータス: {resp.status_code}"}

    data = resp.json()
    # Claude に渡す情報を必要な分だけに絞る(トークン節約 & ノイズ削減)
    return {
        "login": data.get("login"),
        "name": data.get("name"),
        "bio": data.get("bio"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "html_url": data.get("html_url"),
    }
```

> 🎯 **ここで効いている設計の勘所**(`00-...` のツール設計の話と地続き)
> - **戻り値を絞る**:API の生レスポンスを丸ごと返さず、必要なフィールドだけにする。余計なデータは Claude のコンテキスト(=トークン=コスト)を食う
> - **エラーを Claude にわかる言葉で返す**:例外を投げっぱなしにせず、`{"error": "..."}` で「何が起きたか」を文章で返す。Claude はこれを読んで次の手を判断できる
> - **timeout を必ず付ける**:外部 API がハングしてもサーバーが固まらないように

### 12.1 再接続して試す

ツールを足したらサーバーを再起動(Claude Code 側で `/mcp` から reconnect、または Claude Code を再起動)。そして:

```
torvalds の GitHub プロフィールを調べて、公開リポジトリ数とフォロワー数を教えて
```

Claude が `get_github_user("torvalds")` を呼び、整形して答えてくれれば成功です。

> 💡 この `get_github_user` を「社内 API を叩くツール」「DB を引くツール」に置き換えれば、**自社サービスを Claude から操作できる** ようになります。これが Community Tools(GitHub/Slack/Jira 連携)の実体です。

### 12.2 副作用のあるツールは慎重に(発展)

ここまでは「読むだけ」のツールでした。「書く・送る」ツール(PR作成、Slack投稿、ファイル削除など)を作るときは、`00-...` で学んだ通り **確認フラグ** や **スコープ制限** を入れます。

```python
@mcp.tool()
def post_to_log(message: str, confirm: bool = False) -> str:
    """ローカルのログファイルに1行追記する。confirm=True のときだけ実行する。"""
    if not confirm:
        return "確認が必要です。confirm=True で再実行してください。"
    with open("agent.log", "a", encoding="utf-8") as f:
        f.write(message + "\n")
    return "OK: 追記しました"
```

> ⚠️ MCP ツールは Claude に「あなたの環境で何かを実行する力」を与えます。**破壊的な操作には必ずブレーキ** を設計してください。

---

## 13. ステップ4:HTTP トランスポートで動かす

ここまでは stdio(子プロセス起動)でした。**リモートで動かしたい / 複数のクライアントから使いたい** 場合は HTTP トランスポートにします。

`server.py` の起動部分を変えるだけです。

```python
if __name__ == "__main__":
    # streamable-http で起動(HTTP サーバーとして待ち受ける)
    mcp.run(transport="streamable-http")
```

起動:

```bash
uv run server.py
```

これで HTTP エンドポイントとして待ち受けます(デフォルトのポート/パスは SDK の表示に従う)。Claude Code 側は `.mcp.json` を HTTP 接続用に書き換えます。

```json
{
  "mcpServers": {
    "my-remote-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

| トランスポート | 設定の書き方 | 主な用途 |
|---|---|---|
| stdio | `command` + `args` | ローカルで子プロセス起動 |
| HTTP | `type: "http"` + `url` | リモート/共有サーバー |

> 🎯 **使い分けの結論**:まずは **stdio** で開発(楽・速い)。チームで共有したり別マシンに置きたくなったら **HTTP** に切り替える、という順番が自然です。

> 📝 `01-...` で作った FastAPI バックエンドが「**人間/フロントエンド向けの API**」だったのに対し、MCP サーバーは「**AI(Claude)向けの API**」です。どちらも "自分で書いたツールを外から呼ばせる" 点は同じで、相手が人か AI かが違うだけ、と捉えると腑に落ちます。

---

## 14. チェックリストと次のステップ

### 14.1 理解度チェック

- [ ] CLI / Desktop / IDE 拡張、それぞれの強みと「いつ使うか」を言えるか?
- [ ] IDE 拡張の「コンテキスト自動認識」は何が嬉しいのか?
- [ ] Channels が「URL を公開せずに」動けるのはなぜか?
- [ ] MCP の Tool / Resource / Prompt の違いは?
- [ ] stdio と HTTP トランスポートの使い分けは?
- [ ] `@mcp.tool()` の docstring と型ヒントは、Claude にとって何の役割を果たすか?

### 14.2 写経したコードを拡張する課題

`server.py` をベースに挑戦してください。

1. **検索ツール**:`search_files(pattern: str)` を作り、`glob` でローカルファイルを検索して返す
2. **天気ツール**:公開の天気 API を `httpx` で叩く `get_weather(city)` を作る(戻り値は必要な項目だけに絞る)
3. **Resource を公開**:`@mcp.resource("config://app")` でアプリ設定を読めるようにする
4. **`01-...` の自作バックエンドと連携**:MCP ツールから `01-...` の `POST /chat` を叩く `ask_backend(message)` を作り、「自作 API を呼ぶ MCP ツール」を体験する
5. **プラグイン化に挑戦**:作った MCP サーバーを配布可能な形にまとめ、`/plugin` で入れられる構成を調べてみる

### 14.3 参照リソース

- 公式: [Claude Code を"あらゆる場所"で使う(overview)](https://code.claude.com/docs/en/overview#use-claude-code-everywhere)
- 公式: [VS Code で使う](https://code.claude.com/docs/en/vs-code) / [JetBrains で使う](https://code.claude.com/docs/en/jetbrains)
- 公式: [Desktop](https://code.claude.com/docs/en/desktop)
- 公式: [Channels](https://code.claude.com/docs/en/channels) / [Channels reference](https://code.claude.com/docs/en/channels-reference)
- 公式: MCP Python SDK(`modelcontextprotocol/python-sdk`)
- 関連: 本リポジトリ `docs/00-...`(エージェント設計)/ `docs/01-...`(認証・課金・自作バックエンド)

### 14.4 最後に

この教材で押さえたのは、**「Claude Code の "入口" は5つあるが、エンジンは1つ」**「**Channels も Community Tools も MCP という共通基盤の上に乗っている**」という構造的な見方でした。

そして MCP サーバーを自分で書いてみたことで、**「Claude に自作の道具を持たせる」** という拡張の本質を手に入れました。`00-...` の「ツール設計」、`01-...` の「自作バックエンド」、本書の「MCP サーバー」は、すべて **"AI が呼べるツールをどう設計し、どう繋ぐか"** という同じテーマの別の側面です。

Happy extending! 🚀

---

## 付録A:完成版 MCP サーバー全文

ステップ1〜3をまとめた写経用の完成版です(stdio 起動)。

```python
# server.py — 自作 MCP サーバー(完成版)
# 依存: uv add "mcp[cli]" httpx
# 起動(単体): uv run server.py
# Claude Code 接続: claude mcp add my-mcp -- uv run server.py
#                 または .mcp.json に登録

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-mcp")


# ---------- 計算ツール ----------
@mcp.tool()
def add(a: int, b: int) -> int:
    """2つの整数を足し算して返す。"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """2つの整数を掛け算して返す。"""
    return a * b


# ---------- 外部 API を叩くツール ----------
@mcp.tool()
def get_github_user(username: str) -> dict:
    """GitHub の公開ユーザー情報を返す。

    Args:
        username: 調べたい GitHub のユーザー名(例: "torvalds")
    """
    url = f"https://api.github.com/users/{username}"
    try:
        resp = httpx.get(url, timeout=10.0)
    except httpx.RequestError as e:
        return {"error": f"リクエスト失敗: {e}"}

    if resp.status_code == 404:
        return {"error": f"ユーザーが見つかりません: {username}"}
    if resp.status_code != 200:
        return {"error": f"予期しないステータス: {resp.status_code}"}

    data = resp.json()
    return {
        "login": data.get("login"),
        "name": data.get("name"),
        "bio": data.get("bio"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "html_url": data.get("html_url"),
    }


# ---------- 副作用ありツール(確認フラグ付き) ----------
@mcp.tool()
def post_to_log(message: str, confirm: bool = False) -> str:
    """ローカルのログファイルに1行追記する。confirm=True のときだけ実行する。"""
    if not confirm:
        return "確認が必要です。confirm=True で再実行してください。"
    with open("agent.log", "a", encoding="utf-8") as f:
        f.write(message + "\n")
    return "OK: 追記しました"


if __name__ == "__main__":
    # ローカルは stdio。リモート共有したいときは下行に差し替え:
    # mcp.run(transport="streamable-http")
    mcp.run()
```

対応する `.mcp.json`(stdio 版):

```json
{
  "mcpServers": {
    "my-mcp": {
      "command": "uv",
      "args": ["run", "server.py"]
    }
  }
}
```

---

## 付録B:トラブルシューティング

| 症状 | 原因 / 対処 |
|---|---|
| `/mcp` でサーバーが出てこない | `.mcp.json` の場所(プロジェクト直下)と JSON の文法を確認。Claude Code を再起動 |
| `failed to connect` | `command`/`args` でサーバーが起動できるか、まず手で `uv run server.py` を試す |
| `uv run server.py` が即終了する | `if __name__ == "__main__": mcp.run()` を書き忘れていないか確認 |
| ツールが呼ばれない | docstring が空/曖昧だと Claude が使い方を判断できない。説明と引数を具体的に書く |
| `ModuleNotFoundError: mcp` | `uv add "mcp[cli]"` を実行したか、`uv run` 経由で起動しているか確認 |
| 外部APIツールがタイムアウト | `httpx.get(..., timeout=...)` を設定。ネットワーク/プロキシも確認 |
| HTTP 接続できない | `mcp.run(transport="streamable-http")` で起動し、`.mcp.json` を `type:"http"` + 正しい `url` に |
| 戻り値が大きすぎて遅い/高い | API レスポンスを丸ごと返さず、必要なフィールドだけに絞る |

---

以上で **「Claude Code の使い方の種類を理解して、自作 MCP サーバーで拡張する」** は完了です。
00→01→02 と進めたことで、Claude を **「使う」「組み込む」「拡張する」** の3層すべてに触れました。次は、自分の実務で使っているサービスを MCP ツール化して、Claude Code をあなた専用の相棒に育ててみてください。
