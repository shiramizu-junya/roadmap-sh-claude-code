# Claude Code のセットアップ・認証方式・API課金 を理解して、自作バックエンドAPIに組み込む

> 対象読者: ソフトウェアエンジニア(初〜中級)/ これから Claude Code と Claude API を実務で使い始める人
> ゴール: 「Claude Code をどう入れて、どう認証するのか」「サブスクと API課金は何が違うのか」「お金はどうかかるのか」を**正しく理解した上で**、**自分でバックエンド API を書いて** Claude API を呼び出せるようになる
> 進め方: このドキュメントを **上から順に読むだけ** で、概念 → 料金の仕組み → 環境構築 → コードまで一通り体験できます。コードは **自分で写経** してください。コピペでも動きますが、写経した方が圧倒的に身につきます。

> 📌 この教材は `00-claude-code-and-agents-handbook.md`(Claude Code とは何か / エージェントの作り方)の **続編** です。00番が「Claude Code とエージェントの概念」だったのに対し、本書は「**インストール・認証・課金という"運用の入口"**」と「**Claude API を自作バックエンドに組み込む実装**」にフォーカスします。

---

## 目次

1. [この教材で学ぶこと](#1-この教材で学ぶこと)
2. [まず全体像:Claude / Claude Code / Claude API の関係](#2-まず全体像claude--claude-code--claude-api-の関係)
3. [Claude Code のセットアップ](#3-claude-code-のセットアップ)
4. [認証方式の選択:サブスク契約 vs API課金](#4-認証方式の選択サブスク契約-vs-api課金)
5. [API課金の仕組みを正しく理解する(トークンと料金)](#5-api課金の仕組みを正しく理解するトークンと料金)
6. [ハンズオン準備:uv で環境を作り、APIキーを設定する](#6-ハンズオン準備uv-で環境を作りapiキーを設定する)
7. [ステップ1:生の HTTP API を curl で叩く](#7-ステップ1生の-http-api-を-curl-で叩く)
8. [ステップ2:SDK で1回呼び出す](#8-ステップ2sdk-で1回呼び出す)
9. [ステップ3:自作バックエンド API を書く(テンプレートなし)](#9-ステップ3自作バックエンド-api-を書くテンプレートなし)
10. [ステップ4:ストリーミング対応にする](#10-ステップ4ストリーミング対応にする)
11. [ステップ5:コストを計測・制御する](#11-ステップ5コストを計測制御する)
12. [ステップ6:セキュリティの最低ライン](#12-ステップ6セキュリティの最低ライン)
13. [チェックリストと次のステップ](#13-チェックリストと次のステップ)
14. [付録A:完成版バックエンド全文](#付録a完成版バックエンド全文)
15. [付録B:トラブルシューティング](#付録bトラブルシューティング)

---

## 1. この教材で学ぶこと

元になった記事は、大きく3つのトピックを扱っています。

| トピック | 内容のひとことまとめ |
|---|---|
| **Setting up Claude Code** | CLI を1コマンドで入れて、`claude` で起動 → 初回ログインで認証 |
| **Subscription Options** | Pro / Max(個人)や Team / Enterprise(組織)の契約でログインして使う |
| **API Usage** | Console の API キーを使い、**従量課金(pay-as-you-go)** で直接 API に繋ぐ |

この3つは「**Claude Code をどう動かすか**」と「**Claude の頭脳(API)をどう呼ぶか**」という、運用の入口の話です。本書ではこれを次の順で理解します。

```
[ 全体像を掴む ] Claude / Claude Code / Claude API の違い
        ↓
[ Claude Code を入れる ] curl / irm で1コマンドインストール
        ↓
[ 認証を選ぶ ] サブスク契約 か API課金 か
        ↓
[ 課金を理解する ] トークンとは / 何にいくらかかるのか
        ↓
[ 手を動かす ] 自分でバックエンド API を書いて Claude API を呼ぶ
```

> 💡 **学ぶゴール**
> - Claude Code を自分の環境にインストールしてログインできる
> - 「サブスクで使う」と「API キーで使う」の違いを自分の言葉で説明できる
> - 従量課金の仕組み(入力/出力トークン)を理解し、コストを意識できる
> - **フレームワークのひな型に頼らず**、自分で書いたバックエンド API から Claude API を呼べる

---

## 2. まず全体像:Claude / Claude Code / Claude API の関係

ここを混同すると、料金や認証の話が一気にわからなくなります。最初に整理しておきましょう。

| 名前 | これは何か | 触り方 | お金 |
|---|---|---|---|
| **Claude(claude.ai)** | ブラウザで使うチャット AI | Web / アプリ | 無料枠 or Pro/Max サブスク |
| **Claude Code** | ターミナルで動く AI コーディングツール | CLI(`claude` コマンド) | サブスク契約 **または** API課金 |
| **Claude API** | Claude の頭脳を呼ぶための **API エンドポイント** | HTTP / SDK(コードから) | **従量課金(API課金)** |

関係を図にするとこうです。

```
                 ┌─────────────────────────────┐
                 │      Anthropic のモデル        │  ← 本体(Claude の"頭脳")
                 │  (Opus / Sonnet / Haiku)      │
                 └──────────────┬──────────────┘
                                │ すべてここを通る
                 ┌──────────────▼──────────────┐
                 │        Claude API            │  ← HTTP エンドポイント
                 │  api.anthropic.com/v1/...    │
                 └───┬───────────┬───────────┬──┘
                     │           │           │
        ┌────────────▼──┐ ┌──────▼──────┐ ┌──▼───────────────┐
        │ claude.ai      │ │ Claude Code │ │ あなたの自作アプリ  │
        │ (Webチャット)   │ │  (CLI)      │ │ (今回作るやつ)     │
        └────────────────┘ └─────────────┘ └──────────────────┘
```

ポイントは **「どのツールも、最終的には Claude API(=モデル)を呼んでいる」** ということ。違うのは **"誰がお金を払う仕組みになっているか(認証方式)"** だけです。

- claude.ai / Claude Code をサブスクで使う → **月額固定**(契約の使用量上限内)
- Claude Code を API キーで使う / 自作アプリから呼ぶ → **使った分だけ従量課金**

> 🔑 **覚えておくこと**
> 本書の後半で作る「自作バックエンド API」は、上図の右下「あなたの自作アプリ」です。これは **必ず API課金(従量課金)** になります。Claude Code のサブスクとは別物・別請求です。

---

## 3. Claude Code のセットアップ

> このセクションは記事の「Setting up Claude Code」に対応します。

### 3.1 インストール(OS別に1コマンド)

Claude Code は **OS に合わせた1コマンド** で入ります。

**macOS / Linux / WSL**(ターミナル):

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows**(PowerShell):

```powershell
irm https://claude.ai/install.ps1 | iex
```

> 📝 **コマンドの読み方(中身を理解しておこう)**
> - `curl -fsSL <URL>`:URL の中身(インストールスクリプト)を取得する。`-f`=失敗時にエラー、`-s`=進捗を出さない、`-S`=エラーは出す、`-L`=リダイレクト追従
> - `| bash`:取得したスクリプトを **そのまま bash で実行** する
> - `irm`=`Invoke-RestMethod`(PowerShell でURLを取得)、`| iex`=`Invoke-Expression`(取得した内容を実行)
>
> ⚠️ `... | bash` は「ネット越しのスクリプトを即実行する」という、本来は注意が必要な操作です。**公式ドメイン(`claude.ai`)であること** を確認してから実行してください。気になる場合は、一度ファイルに保存して中身を読んでから実行しても構いません。

> 💡 00番ハンドブックでは `npm install -g @anthropic-ai/claude-code` を紹介しました。どちらでも入ります。**Node.js を既に使っているなら npm 経由、そうでなければ上の install スクリプト** が手軽です。

### 3.2 起動と初回ログイン

インストールできたら、**任意のコードプロジェクトのディレクトリ** に移動して起動します。

```bash
cd ~/your-project   # 何かしらのプロジェクトに入る(空ディレクトリでも可)
claude              # 起動
```

初回だけ **一度きりのログイン** を求められます。次のどちらかで認証します。

1. **Claude アカウントでログイン**(Pro / Max サブスクを使う場合)
2. **Anthropic Console の API キー**(API課金を使う場合)

ログインが終われば、以降はすぐに使えます。どちらを選ぶべきかは次のセクションで判断します。

### 3.3 まず動作確認

ログイン後、対話プロンプトに自然言語で投げてみましょう。

```
このディレクトリにどんなファイルがあるか教えて
```

ファイル一覧が返ってくれば、セットアップは成功です。

---

## 4. 認証方式の選択:サブスク契約 vs API課金

> このセクションは記事の「Subscription Options」と「API Usage」に対応します。**ここが本書のいちばん大事な分かれ道** です。

Claude Code にログインする方法は、大きく2系統あります。

### 4.1 サブスク契約でログインする

**月額固定** で Claude を使う契約です。

| プラン | 主な対象 | 特徴 |
|---|---|---|
| **Pro** | 個人 | 手頃な月額。普段使いのコーディング補助に十分なことが多い |
| **Max** | 個人ヘビーユーザー | Pro より使用量上限が大きい。長時間・大量に回す人向け |
| **Team** | チーム | メンバー管理、より高い上限 |
| **Enterprise** | 組織 | SSO(シングルサインオン)、監査ログ、より深い統合・セキュリティ機能 |

**メリット**

- 料金が **予測しやすい**(月額固定)
- 「トークンを気にしながら使う」ストレスがない
- Claude.ai(Webチャット)も同じ契約で使える

**向いている人**:Claude Code を **対話的に・日常的に** 使う開発者。請求が読みにくくなるのを避けたい人。

### 4.2 API キー(Console)で使う = API課金

Anthropic の **Console で API キーを発行** し、それを使って **直接 API に接続** する方式です。これが記事でいう「API Usage(pay-as-you-go)」です。

**やること**

1. [Anthropic Console](https://platform.claude.com/) でアカウント作成
2. **API キー(シークレットキー)を発行**
3. アカウントに **クレジット(残高)をチャージ**(プリペイド)
4. そのキーで Claude Code にログイン、または自作アプリから API を呼ぶ

**メリット**

- **使った分だけ** の支払い(処理したトークン量に応じる)
- **モデルのバージョンを自分で選べる**(Opus / Sonnet / Haiku を用途で使い分け)
- 課金・使用量を **細かくコントロール** できる(上限設定など)
- **自作アプリに組み込める**(←本書の後半でやること)

**向いている人**:パワーユーザー、開発者、そして **API を自分のプロダクトに組み込みたい人**。

### 4.3 比較表:どっちを選ぶ?

| 観点 | サブスク(Pro/Max/Team/Ent) | API課金(Console キー) |
|---|---|---|
| 料金体系 | 月額固定 | 従量課金(トークン単位) |
| 請求の読みやすさ | ◎ 予測しやすい | △ 使い方次第で変動 |
| Claude Code で使える | ◎ | ◎ |
| 自作アプリに組み込める | ✗ | ◎ |
| モデルを細かく選ぶ | △ | ◎ |
| 使い始めの手間 | アカウントログインだけ | キー発行 + クレジット入金が必要 |

> 🎯 **結論(おすすめの考え方)**
> - **Claude Code を普段使いするだけ** なら → **Pro/Max サブスク** が楽でコスパが良い
> - **自分のアプリ・バックエンドに Claude を組み込みたい** なら → **API課金(Console キー)一択**
> - 両方やる人は **両方契約** することも普通にあります(用途が別物なので)

本書の後半(ステップ1以降)では **自作バックエンドを作る** ので、**API課金(Console キー)** を使います。

---

## 5. API課金の仕組みを正しく理解する(トークンと料金)

> 「API ってお金かかるの?」— はい、かかります。ここを曖昧にしたまま実装すると、意図せず課金が膨らみます。エンジニアとして必ず押さえましょう。

### 5.1 課金の単位は「トークン」

Claude API は **トークン(token)** という単位で課金されます。トークンはおおまかに「単語やその一部」のかたまりです。

- 英語ではだいたい **1トークン ≒ 4文字** 程度
- 日本語は1文字で複数トークンになることもあり、英語より割高になりがち
- 「こんにちは、元気ですか?」のような短文でも十数トークン使う

課金されるのは **2種類** です。

| 種類 | 何のトークンか | 特徴 |
|---|---|---|
| **入力トークン(input)** | あなたが送るプロンプト + 会話履歴 + システムプロンプト | 会話が長くなるほど増える |
| **出力トークン(output)** | モデルが生成した返答 | 一般に入力より **単価が高い** |

> ⚠️ **よくある落とし穴**:会話を続けると、過去のやりとり全部が毎回 **入力トークン** として再送されます。長い会話ほど1回あたりのコストが上がります(エージェントのループも同様)。

### 5.2 モデルによって単価が違う

ざっくりの序列はこうです(正確な金額は必ず公式の料金ページで確認):

```
   高性能・高価格 ←──────────────────────→ 軽量・低価格
        Opus            Sonnet            Haiku
   (難しい推論)      (バランス型)      (高速・安い)
```

- **Opus**:最も賢いが最も高い。難しい設計・推論向け
- **Sonnet**:性能と価格のバランス。多くの用途で標準
- **Haiku**:最も安く速い。**学習・お試し・大量処理** に最適

> 💰 **学習中の鉄則**:まずは **Haiku** を使い、`max_tokens` を小さくする。これだけで失敗してもダメージが小さくなります。

### 5.3 「いくらかかるか」のざっくり計算式

```
1リクエストのコスト ≒ (入力トークン × 入力単価) + (出力トークン × 出力単価)
```

たとえば短い質問1往復なら、Haiku では **1円未満〜数円** レベルで収まることがほとんどです。学習用途で破産することはまずありませんが、**無限ループで API を叩き続けるコード** だけは要注意です(これは桁が変わります)。

### 5.4 コストを抑える具体策(実装に効く)

| 対策 | 効果 |
|---|---|
| 安いモデル(Haiku)を使う | 単価が下がる |
| `max_tokens` を小さくする | 出力トークンの上限を絞る = 出力コストの天井を作る |
| 不要な会話履歴を送らない | 入力トークンを減らす |
| プロンプトを簡潔に | 入力トークンを減らす |
| ループに **必ず上限** を設ける | 暴走による課金事故を防ぐ |
| Console で **使用量上限/アラート** を設定 | 想定外の請求を物理的に止める |

> 🔒 **プリペイドという安全装置**:API課金は基本 **前払いのクレジット制** です。残高がなくなれば止まるので、「気づいたら何十万円」という事故は起きにくい設計になっています。とはいえ油断は禁物。

---

## 6. ハンズオン準備:uv で環境を作り、APIキーを設定する

ここから手を動かします。Python のパッケージ管理には **uv**(高速なモダンツール)を使います。

### 6.1 uv で作業環境を作る

```bash
# 作業ディレクトリを作る
mkdir claude-api-backend && cd claude-api-backend

# プロジェクトを初期化(pyproject.toml などを作成)
uv init

# 必要なパッケージを追加(.venv 作成 + インストールまで自動)
uv add anthropic fastapi "uvicorn[standard]"
```

それぞれの役割:

| パッケージ | 役割 |
|---|---|
| `anthropic` | Claude API を呼ぶ公式 SDK |
| `fastapi` | 自作 API を書くための Web フレームワーク |
| `uvicorn` | FastAPI を動かす ASGI サーバー |

> 💡 **uv の使い方メモ**
> - `uv add <pkg>` … 依存を追加(`pyproject.toml` に記録され、`.venv` に入る)
> - `uv run <file.py>` … 仮想環境を自動で使ってスクリプトを実行(`source .venv/bin/activate` 不要)
> - `uv run uvicorn ...` … サーバーも uv 経由で起動できる
>
> 従来の `python -m venv .venv && source .venv/bin/activate && pip install ...` と同じことを、より速く・自動でやってくれます。

> 📌 **「テンプレートを使わない」とは**:`fastapi` の雛形ジェネレータや `create-xxx-app` のようなスキャフォルドは使いません。**空のファイルにルートを1行ずつ自分で書く** ことで、API がどう組み立てられているかを理解します。

### 6.2 API キーを環境変数にセットする

[Anthropic Console](https://platform.claude.com/) でキーを発行し(セクション4.2参照)、環境変数に入れます。

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

> ⚠️ **絶対にやってはいけないこと**
> - API キーを **コードに直書きしてコミット** する(GitHub に上がると即悪用されます)
> - キーを Slack やチャットに貼る
>
> SDK は `ANTHROPIC_API_KEY` 環境変数を **自動で読む** ので、コードにキーを書く必要はありません。`.env` を使う場合も `.gitignore` に必ず入れてください。

`.gitignore` に最低限これを足しておきましょう:

```gitignore
.venv/
.env
__pycache__/
```

---

## 7. ステップ1:生の HTTP API を curl で叩く

SDK を使う前に、**「Claude API はただの HTTP エンドポイント」** だと体感しておきます。これを知っておくと、後でトラブったときに切り分けが早くなります。

ターミナルで次を実行(`ANTHROPIC_API_KEY` がセット済みである前提):

```bash
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-haiku-4-5",
    "max_tokens": 256,
    "messages": [
      {"role": "user", "content": "一文で自己紹介して"}
    ]
  }'
```

各ヘッダ/フィールドの意味:

| 項目 | 意味 |
|---|---|
| `x-api-key` | あなたの API キー(認証) |
| `anthropic-version` | API のバージョン(固定文字列) |
| `model` | 使うモデル。ここでは最安の Haiku |
| `max_tokens` | 出力トークンの上限(コストの天井) |
| `messages` | 会話の配列。`role` は `user` / `assistant` |

返ってくる JSON にはこんな構造が含まれます(抜粋):

```json
{
  "content": [{"type": "text", "text": "私はClaude、Anthropicが作ったAIです。"}],
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 12, "output_tokens": 20}
}
```

> 🔍 **注目ポイント**:`usage` に **input_tokens / output_tokens** が入っています。**これが課金の根拠** です。SDK でもこの値が取れるので、後でコスト計測に使います。

---

## 8. ステップ2:SDK で1回呼び出す

curl と同じことを Python SDK でやります。`step2_basic.py` を作成:

```python
# step2_basic.py
# 目的: Anthropic SDK で 1 回だけ Claude API を呼び、返答と使用トークンを表示する

from anthropic import Anthropic

client = Anthropic()  # ANTHROPIC_API_KEY を環境変数から自動で読む

resp = client.messages.create(
    model="claude-haiku-4-5",   # 学習用に最安のモデル
    max_tokens=256,             # 出力の上限 = コストの天井
    messages=[
        {"role": "user", "content": "一文で自己紹介して"}
    ],
)

# 返答テキストを取り出す(content はブロックの配列)
text = "".join(block.text for block in resp.content if block.type == "text")
print("返答:", text)

# 使用トークン = 課金の根拠。毎回見る習慣をつける
print("入力トークン:", resp.usage.input_tokens)
print("出力トークン:", resp.usage.output_tokens)
```

実行:

```bash
uv run step2_basic.py
```

> ✅ **curl と SDK は同じものを呼んでいる**:`messages.create` は内部で `POST /v1/messages` を叩いているだけです。SDK は「JSON の組み立て」「認証ヘッダ」「レスポンスのパース」を肩代わりしてくれている、という理解でOKです。

---

## 9. ステップ3:自作バックエンド API を書く(テンプレートなし)

ここが本書のメインです。**フレームワークの雛形を使わず、自分でルートを書いて** 「Claude を呼ぶ HTTP API」を作ります。

> 🎯 **作るもの**:`POST /chat` に `{"message": "..."}` を送ると、Claude の返答を JSON で返すバックエンド API。

### 9.1 最小の API を1ファイルで書く

`main.py` を **空から** 作成します(雛形なし、1行ずつ自分で)。

```python
# main.py
# 目的: 自作バックエンド API。POST /chat で Claude を呼んで返答を返す。

from anthropic import Anthropic
from fastapi import FastAPI
from pydantic import BaseModel

# --- アプリ本体を1つ作る ---
app = FastAPI(title="My Claude Backend")

# --- Claude クライアント(プロセスで使い回す) ---
client = Anthropic()  # ANTHROPIC_API_KEY を環境変数から読む


# --- リクエストの形を定義(バリデーションも兼ねる) ---
class ChatRequest(BaseModel):
    message: str


# --- レスポンスの形 ---
class ChatResponse(BaseModel):
    reply: str
    input_tokens: int
    output_tokens: int


# --- ヘルスチェック用の超シンプルなエンドポイント ---
@app.get("/health")
def health():
    return {"ok": True}


# --- メインのエンドポイント:Claude を呼ぶ ---
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[
            {"role": "user", "content": req.message}
        ],
    )

    reply = "".join(b.text for b in resp.content if b.type == "text")

    return ChatResponse(
        reply=reply,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
    )
```

各パーツの意味を理解しておきましょう。

| パーツ | 役割 |
|---|---|
| `app = FastAPI(...)` | API アプリ本体。これにルートを足していく |
| `class ChatRequest(BaseModel)` | リクエスト JSON の形。型が違えば FastAPI が自動で 422 エラーを返す |
| `@app.get("/health")` | GET エンドポイント。死活監視用 |
| `@app.post("/chat")` | POST エンドポイント。ここで Claude を呼ぶ |
| `response_model=...` | レスポンスの形を保証(ドキュメントも自動生成) |

### 9.2 サーバーを起動する

```bash
uv run uvicorn main:app --reload
```

- `main:app` … `main.py` の中の `app` を起動する、という意味
- `--reload` … コードを保存したら自動で再起動(開発中に便利)

起動すると `http://127.0.0.1:8000` で待ち受けます。

### 9.3 動作確認

**別のターミナル** から叩いてみます。

```bash
# ヘルスチェック
curl http://127.0.0.1:8000/health

# チャット
curl http://127.0.0.1:8000/chat \
  --header "content-type: application/json" \
  --data '{"message": "Pythonで素数判定する関数を書いて"}'
```

返ってくる JSON:

```json
{
  "reply": "def is_prime(n): ...",
  "input_tokens": 18,
  "output_tokens": 95
}
```

> 🎉 **これがあなたの自作バックエンド API です。** Claude の頭脳を、自分が書いた `/chat` エンドポイント越しに呼べました。フロントエンドや別サービスは、この `/chat` を叩くだけで Claude を使えます(=API キーをクライアントに晒さずに済む)。

### 9.4 自動ドキュメント(おまけだが超便利)

FastAPI はブラウザで `http://127.0.0.1:8000/docs` を開くと、**Swagger UI(API のお試し画面)** が自動生成されています。`/chat` をブラウザ上で叩いて試せます。これは雛形ではなく、あなたが書いた型定義から自動で作られたものです。

### 9.5 会話履歴に対応させる(任意・発展)

今のままだと毎回「一発勝負」です。会話を続けたいなら、クライアントから履歴ごと送ってもらう形にします。

```python
# main.py に追記する版(差分イメージ)

class Turn(BaseModel):
    role: str      # "user" または "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[Turn] = []   # これまでの会話(省略可)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 履歴 + 今回のメッセージ を組み立てる
    messages = [{"role": t.role, "content": t.content} for t in req.history]
    messages.append({"role": "user", "content": req.message})

    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=messages,
    )
    reply = "".join(b.text for b in resp.content if b.type == "text")
    return ChatResponse(
        reply=reply,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
    )
```

> ⚠️ **コスト注意**:履歴が長くなるほど **入力トークンが増えます**(セクション5.1)。本番では「直近N件だけ送る」「古い履歴は要約する」などの工夫が要ります。

---

## 10. ステップ4:ストリーミング対応にする

ChatGPT のように **文字が少しずつ流れてくる** 体験にするには、ストリーミングを使います。返答全体を待たずに、生成された端から返せます。

### 10.1 SDK のストリーミングを理解する

まず単体で確認(`step4_stream.py`):

```python
# step4_stream.py
# 目的: SDK のストリーミングで、生成テキストを少しずつ受け取る

from anthropic import Anthropic

client = Anthropic()

with client.messages.stream(
    model="claude-haiku-4-5",
    max_tokens=512,
    messages=[{"role": "user", "content": "短い詩を作って"}],
) as stream:
    for text in stream.text_stream:   # 生成されたテキスト片が順に届く
        print(text, end="", flush=True)
print()
```

`messages.stream(...)` を `with` で開き、`stream.text_stream` を回すと、テキストの断片が順次届きます。

### 10.2 バックエンドでストリーミングを返す

`main.py` にストリーミング版エンドポイントを足します。

```python
# main.py に追記

from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    def generate():
        with client.messages.stream(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": req.message}],
        ) as stream:
            for text in stream.text_stream:
                yield text   # 生成された端からクライアントへ送る

    # text/plain でチャンクを流す
    return StreamingResponse(generate(), media_type="text/plain")
```

確認(curl の `-N` でバッファリングを無効化):

```bash
curl -N http://127.0.0.1:8000/chat/stream \
  --header "content-type: application/json" \
  --data '{"message": "宇宙について短く語って"}'
```

文字が少しずつ流れてくれば成功です。

> 💡 実際の Web アプリでは、フロントエンドが **Server-Sent Events(SSE)** や `fetch` のストリーム読み取りでこれを受けて、画面に逐次表示します。バックエンドの役割は「届いた端から `yield` する」だけ。

---

## 11. ステップ5:コストを計測・制御する

API課金を扱う以上、**「今いくら使ったか」を自分で見える化** するのはエンジニアの責任です。

### 11.1 リクエストごとにトークンをログする

`main.py` の `/chat` を、毎回トークンを記録するように改良します。

```python
# main.py の chat を改良

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claude-backend")

# プロセスが生きている間の累計(簡易版)
TOTAL = {"input": 0, "output": 0, "requests": 0}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": req.message}],
    )

    # --- 使用量を記録 ---
    TOTAL["input"] += resp.usage.input_tokens
    TOTAL["output"] += resp.usage.output_tokens
    TOTAL["requests"] += 1
    logger.info(
        "tokens in=%d out=%d (cumulative in=%d out=%d over %d reqs)",
        resp.usage.input_tokens, resp.usage.output_tokens,
        TOTAL["input"], TOTAL["output"], TOTAL["requests"],
    )

    reply = "".join(b.text for b in resp.content if b.type == "text")
    return ChatResponse(
        reply=reply,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
    )


# 累計を確認するエンドポイント
@app.get("/usage")
def usage():
    return TOTAL
```

`GET /usage` を叩けば、このプロセスで使った累計トークンが見られます。

> 📊 **本番では**:この累計はプロセス再起動で消えます。実運用なら DB やメトリクス基盤(Prometheus 等)に記録します。まずは「**トークンを必ずログする**」習慣が大事。

### 11.2 入力の長さに上限を設ける(暴走防止)

巨大な入力をそのまま投げると、入力トークンが膨らみます。バリデーションで弾きましょう。

```python
from fastapi import HTTPException

MAX_INPUT_CHARS = 4000

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if len(req.message) > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"message が長すぎます(最大 {MAX_INPUT_CHARS} 文字)",
        )
    # ... 以下同じ
```

### 11.3 モデルを切り替えられるようにする

用途に応じてモデルを選べると、コストと品質のバランスが取りやすくなります。**許可リスト方式** にして、知らないモデル名を弾くのが安全です。

```python
ALLOWED_MODELS = {
    "haiku": "claude-haiku-4-5",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-7",
}

class ChatRequest(BaseModel):
    message: str
    model: str = "haiku"   # デフォルトは最安

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    model_id = ALLOWED_MODELS.get(req.model)
    if model_id is None:
        raise HTTPException(status_code=400, detail="未対応のモデルです")

    resp = client.messages.create(
        model=model_id,
        max_tokens=512,
        messages=[{"role": "user", "content": req.message}],
    )
    # ... 以下同じ
```

> 🎛️ これで `{"message": "...", "model": "sonnet"}` のように指定できます。**デフォルトを Haiku** にしておけば、指定忘れでも安く済みます。

---

## 12. ステップ6:セキュリティの最低ライン

自作バックエンドを「ちょっと外に公開する」前に、最低限これだけは押さえましょう。

### 12.1 API キーを絶対に漏らさない

- キーは **環境変数**(または Secrets Manager)に置く。コードに直書きしない
- フロントエンド(ブラウザ JS)に **キーを置かない**。だからこそ **バックエンド経由** にする意味がある
- `.env` は `.gitignore` へ。誤って push したキーは **即無効化して再発行**

### 12.2 入力を信用しない

- 文字数上限(11.2)で過大入力を弾く
- `message` が空でないかチェック
- 外部に公開するなら **レート制限**(同一IPからの連打を制限)を入れる

簡易レート制限の考え方(疑似コード):

```python
# 本格的には slowapi などのライブラリ、あるいはリバースプロキシ(nginx)側で。
# まずは「1分あたりN回まで」をメモリで数えるだけでも事故は減る。
```

### 12.3 エラーを握りつぶさない・晒しすぎない

- Claude API 側のエラー(認証失敗・残高切れ・レート超過)は **catch してログ**
- ただしエラーの詳細(スタックトレースや内部情報)を **そのままクライアントに返さない**

```python
from anthropic import APIError

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        resp = client.messages.create(...)
    except APIError as e:
        logger.error("Claude API error: %s", e)
        raise HTTPException(status_code=502, detail="AI サービスでエラーが発生しました")
    # ...
```

### 12.4 コストの暴走を止める

- ループや再帰で API を呼ぶ箇所には **必ず上限**(00番ハンドブックの `max_steps` と同じ思想)
- Console 側で **使用量上限・アラート** を設定(物理的な安全弁)

---

## 13. チェックリストと次のステップ

### 13.1 理解度チェック

次に自分の言葉で答えられたら合格です。

- [ ] Claude / Claude Code / Claude API の違いを説明できるか?
- [ ] サブスク契約と API課金、それぞれどんな人に向くか?
- [ ] 入力トークンと出力トークンの違いは?なぜ会話が長いと高くなる?
- [ ] `curl` と SDK の `messages.create` は何が同じで何が違う?
- [ ] 自作バックエンドを挟むと、なぜセキュリティ上良いのか?

### 13.2 写経したコードを拡張する課題

`main.py` をベースに挑戦してみてください。

1. **システムプロンプト対応**:`client.messages.create(..., system="あなたは丁寧な日本語アシスタントです")` を足して、口調を固定する
2. **`/chat/stream` に履歴対応**を入れる(ステップ3.5 と組み合わせる)
3. **概算コスト表示**:`/usage` に、トークン数から概算金額を計算して返す(単価は公式から)
4. **00番ハンドブックの自作エージェントを API 化**:`run_agent()` を `POST /agent` エンドポイントから呼べるようにする(ツール実行が走るので、入力検証とログを厚めに)

### 13.3 参照リソース

- 公式: [Claude Code クイックスタート](https://code.claude.com/docs/en/quickstart)
- 公式: [Anthropic Console](https://platform.claude.com/)(キー発行・残高・使用量)
- 公式: [料金・プラン](https://claude.com/pricing)
- 公式: [プランの選び方](https://support.claude.com/en/articles/11049762-choosing-a-claude-plan)
- 関連: 本リポジトリ `docs/00-claude-code-and-agents-handbook.md`(エージェントの作り方)

### 13.4 最後に

この教材で押さえたのは、**「Claude Code は入口にすぎず、その奥には必ず Claude API がいる」**「**自作アプリに組み込むなら API課金一択で、トークン課金を理解して設計する**」という運用とコストの視点でした。

00番で学んだ「エージェントの仕組み」と、本書で学んだ「認証・課金・自作バックエンド」を合わせれば、**自分のプロダクトに Claude を安全に・コストを管理しながら組み込む** ための基礎が揃います。

Happy building! 🚀

---

## 付録A:完成版バックエンド全文

ステップ3〜5の要素を1ファイルにまとめた写経用の完成版です。

```python
# main.py — 自作 Claude バックエンド(完成版)
# 起動: uv run uvicorn main:app --reload
# 前提: export ANTHROPIC_API_KEY="sk-ant-..."

import logging

from anthropic import Anthropic, APIError
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claude-backend")

app = FastAPI(title="My Claude Backend")
client = Anthropic()

ALLOWED_MODELS = {
    "haiku": "claude-haiku-4-5",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-7",
}
MAX_INPUT_CHARS = 4000
TOTAL = {"input": 0, "output": 0, "requests": 0}


class ChatRequest(BaseModel):
    message: str
    model: str = "haiku"


class ChatResponse(BaseModel):
    reply: str
    input_tokens: int
    output_tokens: int


def resolve_model(name: str) -> str:
    model_id = ALLOWED_MODELS.get(name)
    if model_id is None:
        raise HTTPException(status_code=400, detail="未対応のモデルです")
    return model_id


def validate_message(message: str) -> None:
    if not message.strip():
        raise HTTPException(status_code=400, detail="message が空です")
    if len(message) > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"message が長すぎます(最大 {MAX_INPUT_CHARS} 文字)",
        )


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/usage")
def usage():
    return TOTAL


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    validate_message(req.message)
    model_id = resolve_model(req.model)

    try:
        resp = client.messages.create(
            model=model_id,
            max_tokens=512,
            messages=[{"role": "user", "content": req.message}],
        )
    except APIError as e:
        logger.error("Claude API error: %s", e)
        raise HTTPException(status_code=502, detail="AI サービスでエラーが発生しました")

    TOTAL["input"] += resp.usage.input_tokens
    TOTAL["output"] += resp.usage.output_tokens
    TOTAL["requests"] += 1
    logger.info(
        "tokens in=%d out=%d (cumulative in=%d out=%d over %d reqs)",
        resp.usage.input_tokens, resp.usage.output_tokens,
        TOTAL["input"], TOTAL["output"], TOTAL["requests"],
    )

    reply = "".join(b.text for b in resp.content if b.type == "text")
    return ChatResponse(
        reply=reply,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
    )


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    validate_message(req.message)
    model_id = resolve_model(req.model)

    def generate():
        try:
            with client.messages.stream(
                model=model_id,
                max_tokens=512,
                messages=[{"role": "user", "content": req.message}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except APIError as e:
            logger.error("Claude API error (stream): %s", e)
            yield "\n[エラー: AI サービスで問題が発生しました]"

    return StreamingResponse(generate(), media_type="text/plain")
```

---

## 付録B:トラブルシューティング

| 症状 | 原因 / 対処 |
|---|---|
| `anthropic.AuthenticationError` | `ANTHROPIC_API_KEY` が未設定/無効。`echo $ANTHROPIC_API_KEY` で確認、Console で再発行 |
| `... credit balance is too low` | Console の残高切れ。クレジットをチャージ |
| `command not found: claude` | インストール直後は PATH が通っていないことがある。ターミナルを開き直す |
| `uv: command not found` | uv 未インストール。`curl -LsSf https://astral.sh/uv/install.sh | sh` |
| `curl` で `--reload` が効かない | `--reload` は uvicorn 側のオプション。`uv run uvicorn main:app --reload` で起動しているか確認 |
| ストリーミングがまとめて返る | `curl -N` を付ける。プロキシ/ロードバランサがバッファしている可能性も |
| `422 Unprocessable Entity` | リクエスト JSON が `ChatRequest` の型と合っていない。`content-type: application/json` と body を確認 |
| 料金が心配 | モデルを `haiku` に、`max_tokens` を小さく。Console で使用量上限/アラートを設定 |
| モデル名エラー | 利用可能モデルは時期で変わる。Console で確認して `ALLOWED_MODELS` を差し替え |

---

以上で **「Claude Code のセットアップ・認証方式・API課金 を理解して、自作バックエンドAPIに組み込む」** は完了です。
00番ハンドブックと合わせて、Claude を「使う」「作る」「運用する」の3視点を手に入れてください。
