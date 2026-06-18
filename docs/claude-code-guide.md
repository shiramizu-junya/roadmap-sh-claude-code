# Claude Code 実践ガイド — CLAUDE.md / Skills / Context / Modes を「手書き API」で学ぶ

> このドキュメント1枚で完結します。**上から順に読み、書いてあるコードを自分の手で打ち込みながら**進めてください。
> 解説とコードは分離していません。「なぜそうするのか」を読んだ直後に「実際に動くコード」を書く、という流れがずっと続きます。

---

## 0. この教材で何を学ぶのか

Claude Code(ターミナルで動く AI コーディングエージェント)を **"なんとなく使う"** から **"狙って使いこなす"** に引き上げるための、4つの中核概念を学びます。

| 概念 | 一言で | これを知らないと起きること |
|---|---|---|
| **CLAUDE.md** | プロジェクトの「永続ルール帳」。毎セッション冒頭に自動で読まれる | 同じ指示を毎回打つ羽目になる / AI が勝手な流儀で書く |
| **Skills** | 繰り返す手順を「モジュール化」したもの(`SKILL.md`) | 長い手順書を毎回コピペ。CLAUDE.md が肥大化する |
| **Context(コンテキスト)** | AI の「作業机の広さ」。会話・読んだファイル・コマンド出力が全部載る | 机が埋まると AI が指示を「忘れ」始め、精度が落ちる |
| **Modes(権限モード)** | AI にどこまで自律を許すかのスイッチ | 毎回承認ボタンを連打 or 危険な操作を野放し |

### この教材の進め方(重要)

1. **第1部**で、題材になる **「タスク管理 API」** を**標準ライブラリだけ**で手書きします(テンプレ・フレームワーク禁止)。
   - これは Claude Code の練習台です。まず "自分のプロジェクト" を持つことが出発点になります。
2. **第2部〜第5部**で、その API を題材に4概念を1つずつ実践します。
   - 各章は「**概念の解説 → その場で手を動かす**」の繰り返しです。
3. 出てくるコマンド・ファイルは**全部あなたが自分で打ち込みます**。コピペでも構いませんが、一度は手で写すと理解が段違いです。

### 完成イメージ

最終的に、あなたのプロジェクトはこうなります:

```text
my-task-api/
├── app.py                       # 手書きの API 本体(標準ライブラリのみ)
├── test_app.py                  # ユニットテスト
├── CLAUDE.md                    # ← 第2部で作る。AI への永続ルール
└── .claude/
    ├── settings.json            # ← 第4部で作る。権限(allow/deny)設定
    └── skills/
        ├── smoke-test/
        │   └── SKILL.md         # ← 第5部で作る。API を叩いて動作確認する skill
        └── add-endpoint/
            └── SKILL.md         # ← 第5部で作る。新エンドポイント追加の手順 skill
```

> **前提**: Python 3 と Claude Code がインストール済みであること。`python3 --version` と `claude --version` が通ればOKです。

---

# 第1部 — 題材を作る:標準ライブラリだけの「タスク管理 API」

ここではまだ Claude Code の機能は使いません。**学習の練習台**となる小さな API を、Flask や FastAPI のような**フレームワーク/テンプレートを一切使わず**、Python の標準ライブラリ `http.server` だけで手書きします。

> なぜテンプレートを使わないのか?
> テンプレートは「中で何が起きているか」を隠します。HTTP リクエストがどう来て、どう振り分けられ、どう JSON を返すのか——その**素の仕組み**を一度自分で書くと、後で AI が生成するコードの良し悪しを**自分で判断**できるようになります。これは AI 時代のエンジニアにとって最重要スキルです。

## 1-1. まず一番小さいサーバ(1エンドポイント)

新しい作業用フォルダを作り、`app.py` を作って以下を**手で書いて**ください。

```bash
mkdir my-task-api && cd my-task-api
```

`app.py`:

```python
# app.py — 最小の HTTP サーバ。まずは "動く1本" から始める
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class Handler(BaseHTTPRequestHandler):
    # do_GET という名前のメソッドを定義すると、GET リクエストがここに来る
    def do_GET(self):
        if self.path == "/health":
            # 返したい中身(辞書)を JSON 文字列 → bytes に変換
            body = json.dumps({"status": "ok"}).encode("utf-8")
            self.send_response(200)                      # ステータスライン(200 OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()                           # ヘッダ終端
            self.wfile.write(body)                       # 本文を書き込む
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), Handler)
    print("http://127.0.0.1:8000 で起動中")
    server.serve_forever()
```

**動かしてみる:**

```bash
python3 app.py
```

別のターミナルを開いて:

```bash
curl -s http://127.0.0.1:8000/health
# => {"status": "ok"}
```

ここまでで「リクエストが来る → 振り分ける → JSON を返す」という HTTP API の**最小単位**を自分で書けました。`Ctrl+C` で止めて先に進みます。

> 🧩 **理解ポイント**: `BaseHTTPRequestHandler` を継承し、`do_GET` / `do_POST` / `do_DELETE` というメソッド名を定義するだけで、対応する HTTP メソッドの処理になります。フレームワークの "ルーティング" は、結局この振り分けを楽にしているだけ、という感覚を持てると強いです。

## 1-2. データの置き場所を分ける(関心の分離)

毎回 `do_GET` の中に処理をベタ書きすると破綻します。**「データを持つ係」**と**「HTTP を捌く係」**を分けましょう。`app.py` を次のように育てます。

```python
# app.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


# ============================================================
# データ層:タスクを保存する箱(メモリ上の辞書。再起動で消える)
# ============================================================
class TaskStore:
    def __init__(self):
        self._tasks = {}    # id(int) -> task(dict)
        self._next_id = 1   # 次に振る id

    def list(self):
        return list(self._tasks.values())

    def create(self, title):
        task = {"id": self._next_id, "title": title, "done": False}
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id):
        return self._tasks[task_id]   # 無ければ KeyError

    def delete(self, task_id):
        del self._tasks[task_id]      # 無ければ KeyError


# プロセス全体で1つだけ共有する箱
store = TaskStore()
```

> 🧩 **理解ポイント**: `TaskStore` は HTTP を一切知りません。「タスクを作る・一覧する・消す」だけに責任を持ちます。こうしておくと、**テストが簡単**(HTTP を立てずに `store.create(...)` を直接呼べる)で、後で保存先を DB に差し替えるのも楽です。

## 1-3. HTTP 層を足して CRUD を完成させる

続けて同じ `app.py` の下に HTTP 層を書きます。

```python
# ============================================================
# HTTP 層:リクエストを受けて store を呼び、JSON を返す
# ============================================================
class Handler(BaseHTTPRequestHandler):
    # --- ヘルパー:status と dict を JSON で返す ---
    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # --- ヘルパー:リクエスト本文を JSON として読む ---
    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        return json.loads(raw)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        elif self.path == "/tasks":
            self._send(200, {"tasks": store.list()})
        elif self.path.startswith("/tasks/"):
            task_id = int(self.path.split("/")[2])     # "/tasks/3" → 3
            try:
                self._send(200, store.get(task_id))
            except KeyError:
                self._send(404, {"error": "not found"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/tasks":
            data = self._read_json()
            task = store.create(data["title"])
            self._send(201, task)
        else:
            self._send(404, {"error": "not found"})

    def do_DELETE(self):
        if self.path.startswith("/tasks/"):
            task_id = int(self.path.split("/")[2])
            try:
                store.delete(task_id)
            except KeyError:
                self._send(404, {"error": "not found"})
                return
            self._send(200, {"deleted": task_id})
        else:
            self._send(404, {"error": "not found"})


def main():
    server = HTTPServer(("127.0.0.1", 8000), Handler)
    server.allow_reuse_address = True
    print("http://127.0.0.1:8000 で起動中")
    server.serve_forever()


if __name__ == "__main__":
    main()
```

**動作確認(API を一通り叩く):**

```bash
python3 app.py          # 別ターミナルで起動しておく

curl -s localhost:8000/health
curl -s -X POST localhost:8000/tasks -d '{"title":"牛乳を買う"}'
curl -s -X POST localhost:8000/tasks -d '{"title":"PRをレビュー"}'
curl -s localhost:8000/tasks
curl -s localhost:8000/tasks/1
curl -s -X DELETE localhost:8000/tasks/1
curl -s localhost:8000/tasks
```

これで **テンプレート無しの手書き API** が完成しました。これ以降、この `my-task-api` を題材に Claude Code の4概念を学びます。

> ✅ ここまでのチェック: `GET /tasks` で配列が返り、`POST` で `id` が 1,2... と増え、`DELETE` 後に消える。これが確認できたら第2部へ。

---

# 第2部 — CLAUDE.md:プロジェクトの「永続ルール帳」

## 2-1. CLAUDE.md とは何か

**CLAUDE.md** は、プロジェクトのルート等に置く特別な Markdown ファイルです。Claude Code は**毎セッションの開始時に、このファイルを自動で読み込みます**。コードからは読み取れない「永続的な前提知識」——ビルド/テストコマンド、コードスタイル、ワークフローの約束事、環境の癖——をここに書いておくと、AI が毎回それに沿って動いてくれます。

公式が挙げる本質はこの一文です:

> **For each line, ask: "Would removing this cause Claude to make mistakes?" If not, cut it.**
> (各行について「これを消したら Claude がミスするか?」を自問せよ。しないなら消せ。)

CLAUDE.md は**毎回コンテキストに載る**ため、**長すぎると逆効果**です。肥大化すると、AI は重要なルールを「ノイズの海」の中で見失い、**せっかく書いた指示を無視**し始めます。

### 何を書く / 何を書かないか(公式の指針)

| ✅ 書くべき | ❌ 書くべきでない |
|---|---|
| AI が推測できないコマンド(独自のビルド/テスト手順) | コードを読めば分かること |
| デフォルトと違うコードスタイル規則 | 言語の標準的な慣習(AI は既に知っている) |
| テスト方法・使うテストランナー | 詳細な API ドキュメント(リンクで十分) |
| リポジトリの作法(ブランチ命名、PR 規約) | 頻繁に変わる情報 |
| プロジェクト固有のアーキ判断 | ファイルごとの逐一説明 |
| 開発環境の癖(必要な環境変数) | 「きれいなコードを書け」のような自明な訓示 |

## 2-2. ハンズオン:`/init` で土台を作る

Claude Code には CLAUDE.md の**たたき台を自動生成**するコマンドがあります。`my-task-api` フォルダで Claude Code を起動し:

```text
/init
```

`/init` はコードベースを解析して、ビルドシステム・テストフレームワーク・コードパターンを検出し、CLAUDE.md の初版を作ってくれます。**ゼロから書くより、生成してから削る**のが定石です。

## 2-3. ハンズオン:この API 用の CLAUDE.md を手で書く

生成結果を見たら、今度は**自分で**意味を理解しながら書き直します。プロジェクトルートに `CLAUDE.md` を作成してください:

```markdown
# プロジェクト概要
Python 標準ライブラリ(http.server)だけで書いたタスク管理 API。
フレームワーク/外部 Web ライブラリは追加しない。

# コマンド
- 起動: `python3 app.py`(http://127.0.0.1:8000)
- テスト: `python3 -m unittest -v`
- 単体テストのみ流す方を優先(全体実行は遅いので避ける)

# コードスタイル
- 依存は標準ライブラリのみ。Flask/FastAPI などのフレームワークは使わない
- データ層(TaskStore)に HTTP の知識を持ち込まない(関心の分離を守る)
- レスポンスは必ず `_send(status, dict)` 経由で返す

# ワークフロー
- IMPORTANT: 変更後は必ず `python3 -m unittest` を実行し、結果を貼ること
- 振る舞いを変える修正と、振る舞いを変えないリファクタは別コミットにする
- コミットメッセージは Conventional Commits(feat/fix/refactor/test)
```

> 🧩 **理解ポイント**:
> - `IMPORTANT:` や `YOU MUST` のような**強調語**は、遵守率を上げる効果があります(公式記載)。本当に守ってほしい1〜2行にだけ使うのがコツ。
> - 「Flask を使わない」のように、**AI が放っておくとやりがちなこと**を明示的に禁止しておくのが効きます。

## 2-4. CLAUDE.md の置き場所(階層)

CLAUDE.md は1つではありません。**複数の場所**に置け、すべてが読み込まれます。

| 置き場所 | パス | 適用範囲 |
|---|---|---|
| ホーム | `~/.claude/CLAUDE.md` | **全プロジェクト**共通(個人の好み) |
| プロジェクトルート | `./CLAUDE.md` | チーム共有(**git にコミット**する) |
| プロジェクト個人用 | `./CLAUDE.local.md` | 自分専用(`.gitignore` に入れる) |
| 親ディレクトリ | `monorepo/CLAUDE.md` | モノレポ全体に効く |
| 子ディレクトリ | `pkg/foo/CLAUDE.md` | そのフォルダのファイルを触る時に**オンデマンド**で読まれる |

別ファイルを**取り込む(import)**こともできます:

```markdown
See @README.md for project overview and @package.json for available commands.

# 追加指示
- Git ワークフロー: @docs/git-instructions.md
- 個人設定: @~/.claude/my-project-instructions.md
```

## 2-5. `#` ショートカットでその場で追記

セッション中に「あ、これ毎回守ってほしい」と思ったら、プロンプトの先頭で `#` を打つと、その内容を CLAUDE.md(やメモリ)に**追記**できます。会話の流れを止めずにルールを育てられます。

## 2-6. よくある失敗と対処

- **CLAUDE.md が長すぎる** → AI が半分無視する。**容赦なく刈り込む**。「指示しなくても正しくやること」は削除、もしくは**フック(hook)に変換**する。
- **同じ間違いを繰り返す** → そのルールがノイズに埋もれている可能性。ファイルが長すぎないか疑う。
- **CLAUDE.md に書いたことを AI が質問してくる** → 表現が曖昧。言い回しを直す。

> **鉄則**: CLAUDE.md は**コードと同じように扱う**。うまくいかない時に見直し、定期的に剪定し、「AI の挙動が実際に変わったか」で効果をテストする。git にコミットすればチームで育てられ、価値が**複利**で増えていく。

---

# 第3部 — Context(コンテキスト):AI の「作業机」を管理する

## 3-1. コンテキストウィンドウとは

**コンテキストウィンドウ**は、モデルが一度に「active memory(作業中の記憶)」として保持できる情報の総量です。ここには次のすべてが載ります:

- 会話履歴(あなたの発言と AI の発言すべて)
- AI が**読んだファイルの中身**
- 実行した**コマンドの出力**
- CLAUDE.md、オートメモリ、読み込まれた skill、システム指示

これらは **トークン** という単位で数えられ、**容量には上限**があります。机にたとえると、書類(トークン)を積むほど机は埋まり、やがて溢れます。

### なぜこれが「最重要リソース」なのか

公式のベストプラクティスの大半は、たった1つの制約から導かれます:

> **Claude's context window fills up fast, and performance degrades as it fills.**
> (コンテキストはすぐ埋まり、埋まるほど性能が落ちる。)

机が埋まってくると、AI は**会話の初期の指示を「忘れ」始め、ミスが増えます**。1回のデバッグやコードベース探索だけで、数万トークンを消費することもあります。だからこそ、コンテキストを**意図的に管理する**ことが、Claude Code を使いこなす核心になります。

## 3-2. ハンズオン:`/context` で「今、机に何が載っているか」を見る

`my-task-api` で Claude Code を起動し、`app.py` をいくつか読ませた後に:

```text
/context
```

何がどれだけ容量を使っているかが可視化されます。「ファイルを読むと机が減る」という感覚を、数字で体感してください。

## 3-3. 机が埋まったらどうなるか(自動圧縮)

Claude Code は上限に近づくと**自動で対処**します:

1. まず**古いツール出力**(コマンド結果など)から削る
2. それでも足りなければ**会話を要約(compact)**する

要約では「あなたの要求」と「重要なコード片」は保たれますが、**会話の初期にあった細かい指示は失われ得ます**。だからこそ「ずっと守ってほしいルール」は会話履歴ではなく **CLAUDE.md に書く**——第2部とここが繋がります。

> ⚠️ 単一のファイルやツール出力が巨大すぎて、要約しても即座に机が埋まり直す場合、Claude Code は数回で自動圧縮を**停止してエラー**を出します(無限ループ防止)。その時は、その巨大な出力を避ける・分割する等で対処します。

## 3-4. ハンズオン:コンテキストを能動的に管理する4つの技

### ① `/clear` — タスクの切れ目で机を完全リセット

```text
/clear
```

**無関係なタスクに移る時**は、これで会話を全消去します。公式の最頻出アドバイスがこれです。「タスク A → 無関係な質問 → またタスク A」を1セッションでやると、机が無関係な情報で埋まり性能が落ちます(=「キッチンシンク・セッション」という典型的失敗)。

> 体験してみる: API について長く会話した後、全く別の話題に移る前に `/clear` を打つ。直後の応答が締まるのが分かります。

### ② `/compact` — 文脈は残しつつ要約

完全に消したくないが机を空けたい時:

```text
/compact
/compact focus on the API changes      ← 残す焦点を指定できる
```

CLAUDE.md に「圧縮時に何を必ず残すか」を書いておくこともできます:

```markdown
# Compact Instructions
- 圧縮時は、変更したファイルの一覧とテストコマンドを必ず保持すること
```

### ③ サブエージェントに「調べ物」を外注する

これは強力です。AI がコードベースを調査すると、**読んだファイルが全部あなたの机を埋めます**。代わりに**サブエージェント**に投げると、別の机(独立したコンテキスト)で調査し、**要約だけ**返してくれます:

```text
サブエージェントを使って、この API のルーティングが /tasks/{id} を
どう処理しているか調べて、要約だけ返して。
```

あなたの本筋の会話は汚れません。「調査は外注、実装は本会話」と覚えてください。

### ④ `/btw` — 履歴を汚さない小さな質問

文脈に残す必要のないちょっとした質問は `/btw` で。答えは消せるオーバーレイに出て、**会話履歴には入りません**。

## 3-5. チェックポイントで「巻き戻し」

Claude が**ファイルを編集する前**に、毎回自動でスナップショットを取っています。`Esc` を2回押す(または `/rewind`)と、会話・コード・両方を以前の状態に**巻き戻せます**。

> これにより「とりあえず大胆に試して、ダメなら巻き戻す」という攻めた使い方ができます。ただし**チェックポイントは Claude の変更しか追わず、git の代わりにはなりません**。

---

# 第4部 — Modes(権限モード):AI の自律レベルを切り替える

## 4-1. なぜモードが必要か

デフォルトでは、Claude Code は**システムを変更しうる操作**(ファイル書き込み、シェルコマンド、MCP ツール)の前に、いちいち**あなたの承認**を求めます。安全ですが、10回目の承認ともなると、もう中身を見ずにポチポチ押しているだけ——これでは意味がありません。

**権限モード**は、「どこまで AI に任せ、どこで止めるか」を切り替えるスイッチです。

## 4-2. モードの種類と切り替え

ターミナルで **`Shift+Tab`** を押すと、主要なモードを循環できます:

| モード | 挙動 |
|---|---|
| **Default(デフォルト)** | ファイル編集とシェルコマンドの前に毎回確認する |
| **Auto-accept edits(編集自動承認)** | ファイル編集と `mkdir`/`mv`/`cp` 等の一般的なファイル操作は**確認なし**。その他のコマンドは確認する |
| **Plan mode(プランモード)** | **読み取り専用**。ファイルを編集せず、調査して計画を立てる。実装の前段に使う |
| **Auto mode** | 全操作を、背後の安全チェック(分類器)が検査しながら自動承認(リサーチプレビュー) |

設定ファイルで使える追加モード(`defaultMode` に指定):

| モード | 挙動 |
|---|---|
| `dontAsk` | 事前許可(allow ルール)以外は**自動で拒否** |
| `bypassPermissions` | 承認プロンプトを**全部スキップ**。**コンテナ/VM など隔離環境専用**。`rm -rf /` 等だけは安全装置として確認が残る |

> ⚠️ `bypassPermissions` は強力すぎます。**壊れても困らない隔離環境でだけ**使ってください。

## 4-3. ハンズオン:Plan モードで「設計してから書く」

公式が最も推す進め方が **「Explore → Plan → Implement → Commit」** です。`Shift+Tab` を2回押して**プランモード**に入り:

```text
（plan mode）app.py を読んで、いまのルーティングの仕組みを説明して。
そのうえで PUT /tasks/{id}（完了フラグ done を更新する)を足すなら、
どこをどう変える?計画を作って。
```

プランモードでは AI は**ファイルを触りません**。調査と計画だけ。計画に納得したら `Shift+Tab` でモードを抜け、実装させます:

```text
（default mode）さっきの計画どおり PUT /tasks/{id} を実装して。
テストも書いて、`python3 -m unittest` を流して結果を貼って。
```

> 🧩 **理解ポイント**: 「いきなりコードを書かせる」と、**間違った問題を解いてしまう**ことがあります。調査・計画と実装を分けると精度が上がります。ただしプランモードは**オーバーヘッド**でもあるので、「一文で差分を説明できる小さな変更(タイポ修正など)」は計画を飛ばして直接やらせるのが正解です。

## 4-4. 権限ルール:allow / ask / deny

モードとは別に、**個別のツール/コマンド単位**で許可を設定できます。これが**承認連打から解放される**本命です。

`/permissions` コマンドで現在のルールを確認・編集できます。3種類のルールがあります:

- **allow**: 確認なしで使ってよい
- **ask**: 使う時に毎回確認する
- **deny**: 使用を禁止する

**評価順は deny → ask → allow** で、最初にマッチしたものが勝ちます(deny が最優先)。

## 4-5. ハンズオン:`settings.json` に許可リストを書く

`my-task-api` の `.claude/settings.json` を作り、**この API 開発で頻出する安全なコマンド**を許可します。これで毎回の確認が消えます。

```json
{
  "permissions": {
    "allow": [
      "Bash(python3 app.py)",
      "Bash(python3 -m unittest *)",
      "Bash(curl localhost:8000 *)",
      "Bash(curl -s localhost:8000 *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git commit *)"
    ],
    "deny": [
      "Bash(git push *)",
      "Read(.env)"
    ]
  }
}
```

> 🧩 **理解ポイント(ルール構文)**:
> - `Bash(npm run *)` の `*` はワイルドカード。**スペースの有無**が効きます:`Bash(ls *)` は `ls -la` にマッチするが `lsof` にはマッチしない(語境界)。`Bash(ls*)` は両方にマッチ。
> - `Read(.env)` のような deny は、`.env` の**読み取りを禁止**(秘密情報の漏洩防止)。
> - ルールは**バージョン管理にコミットしてチームに配布**できます。組織全体の "managed settings" で上書き不可のポリシーにすることも可能。

### 設定の優先順位(強い順)

1. **Managed settings(組織ポリシー)** — 何にも上書きされない
2. **コマンドライン引数**(`--allowedTools` 等)
3. **プロジェクト個人設定** `.claude/settings.local.json`
4. **プロジェクト共有設定** `.claude/settings.json`
5. **ユーザ設定** `~/.claude/settings.json`

**どこかのレベルで deny されたら、他のどのレベルでも allow できません**(deny 最優先の原則)。

> 補足:権限ルールは **Claude Code(ハーネス)が強制**します。プロンプトや CLAUDE.md は「AI が何を**やろうとするか**」を変えますが、「何が**許されるか**」は変えません。境界はあくまで権限ルール/モード/フックで設けます。

---

# 第5部 — Skills:繰り返す手順を「モジュール化」する

## 5-1. Skill とは何か

**Skill** は、特定の繰り返し作業のための「指示・スクリプト・素材」をまとめたパッケージです。中核は **`SKILL.md`** という1ファイル。YAML フロントマターで「名前」と「いつ使うか(description)」を定義しておくと、Claude が**関連する場面で自動的に読み込み**ます。あるいは `/skill-name` で**手動起動**もできます。

### CLAUDE.md との決定的な違い

| | CLAUDE.md | Skill |
|---|---|---|
| 読み込み | **毎セッション必ず**全文がコンテキストに載る | **使う時だけ**本体が載る(普段は description だけ) |
| 向いている中身 | 常に効く短い**事実**(スタイル、コマンド) | たまにしか使わない**手順**や長い**参照資料** |

公式の指針:

> **CLAUDE.md の一節が、"事実" ではなく "手順" に育ってきたら、それは Skill にすべきサイン。**

Skill の本体は**使う時だけ**ロードされるので、長い参照資料を持っていても**普段はほぼゼロコスト**です。これは第3部のコンテキスト管理と直結します。

## 5-2. ハンズオン①:`SKILL.md` の構造を理解する

Skill は「ディレクトリ + その中の `SKILL.md`」です。**ディレクトリ名がコマンド名**になります。

```text
.claude/skills/smoke-test/
└── SKILL.md          # ← /smoke-test というコマンドになる
```

`SKILL.md` は2部構成です:

```yaml
---
# ↓ ここが YAML フロントマター(設定)
description: 何をするか + いつ使うか。Claude はこれを見て自動起動するか判断する
---

ここから下が Markdown 本文。Skill が起動した時に Claude が従う指示。
```

### フロントマターの主要フィールド(公式リファレンス抜粋)

| フィールド | 説明 |
|---|---|
| `description` | **推奨**。何をするか + いつ使うか。**使うケースを先頭に**書く(listing は 1,536 文字で切られる) |
| `name` | 一覧での表示名。省略時はディレクトリ名 |
| `argument-hint` | 補完時に出る引数ヒント。例 `[id]` |
| `disable-model-invocation` | `true` で**手動起動のみ**に(Claude が勝手に動かさない)。デプロイ等の副作用がある手順に使う |
| `user-invocable` | `false` で `/` メニューから隠す(Claude 専用の背景知識に) |
| `allowed-tools` | この skill が有効な間、確認なしで使えるツール |
| `context` | `fork` でサブエージェントの隔離コンテキストで実行 |
| `agent` | `context: fork` の時にどのサブエージェント種別を使うか |

## 5-3. ハンズオン②:API を叩いて動作確認する Skill を作る

毎回手で `curl` を6回打つのは面倒です。これを **`/smoke-test`** という Skill にします。

`.claude/skills/smoke-test/SKILL.md` を作成:

````markdown
---
description: タスク API を一通り叩いて動作確認する。動いているか確かめたい、スモークテストして、と言われたら使う。
allowed-tools: Bash(curl *)
---

## いまのサーバ状態
```!
curl -s -m 2 localhost:8000/health || echo "サーバが起動していません(別ターミナルで python3 app.py を実行)"
```

## あなたのタスク

上の health チェックが ok でなければ、サーバ未起動の旨だけ報告して終了する。
ok の場合は、以下を順に実行し、各レスポンスと最後に総評(全部期待どおりか)を返す:

1. `curl -s -X POST localhost:8000/tasks -d '{"title":"smoke-1"}'` (201 と id が返るはず)
2. `curl -s localhost:8000/tasks` (作ったタスクが配列で返るはず)
3. 1 で返った id を使って `curl -s localhost:8000/tasks/<id>` (そのタスクが返るはず)
4. `curl -s -X DELETE localhost:8000/tasks/<id>` (deleted が返るはず)
5. `curl -s localhost:8000/tasks/<id>` (404 not found が返るはず)
````

> 🧩 **理解ポイント(動的コンテキスト注入)**: `` ```! `` で囲んだブロック(やインラインの `` !`コマンド` ``)は、**Claude が読む前に実行**され、その**出力に置き換わって**から本文がモデルに渡されます。つまり Claude は「最新のサーバ状態」を**事実として**受け取った状態で動き始めます。これは「Claude が実行するコマンド」ではなく**前処理**である点がポイントです。

**使ってみる**: 別ターミナルで `python3 app.py` を起動した状態で、Claude Code に:

```text
/smoke-test
```

あるいは、description にマッチする自然文でも自動起動します:

```text
このAPI、ちゃんと動いてるか確認して
```

## 5-4. ハンズオン③:手順を持つ Skill(手動起動限定)

「新しいエンドポイントを追加する」決まった手順を **`/add-endpoint`** にします。これは**副作用(コード変更)がある**ので、Claude が勝手に発火しないよう `disable-model-invocation: true` を付け、引数を受け取れるようにします。

`.claude/skills/add-endpoint/SKILL.md`:

```markdown
---
description: タスク API に新しいエンドポイントを追加する手順
argument-hint: [HTTPメソッド] [パス] [やること]
disable-model-invocation: true
allowed-tools: Bash(python3 -m unittest *)
---

新しいエンドポイントを追加する: $ARGUMENTS

このプロジェクトの約束に従って、次の順で進めること:

1. まず app.py の該当する do_XXX を読み、既存のルーティング(if/elif 分岐)の流儀を把握する
2. データ層が必要なら TaskStore にメソッドを足す(HTTP の知識を持ち込まない)
3. HTTP 層に分岐を1つ足す。レスポンスは必ず `_send(status, dict)` 経由で返す
4. 存在しない id 等のエラーは KeyError を捕捉して 404 を返す(既存の流儀に合わせる)
5. test_app.py にテストを足す
6. `python3 -m unittest` を実行し、結果を貼る
7. 振る舞いを変える変更なので、fix: または feat: でコミットメッセージ案を出す
```

**使ってみる**(引数が `$ARGUMENTS` に入ります):

```text
/add-endpoint PUT /tasks/{id} doneフラグを切り替える
```

> 🧩 **理解ポイント(引数)**:
> - `$ARGUMENTS` … 渡した全引数。`/add-endpoint PUT /tasks/{id} ...` の後ろ全部。
> - `$0`, `$1`, `$2` … 0始まりの個別引数(`$ARGUMENTS[0]` の短縮形)。複数語は `"..."` で囲む。
> - `${CLAUDE_SKILL_DIR}` … その SKILL.md があるディレクトリ。バンドルしたスクリプトを呼ぶ時に使う。

## 5-5. Skill の置き場所と発見

| 場所 | パス | 適用範囲 |
|---|---|---|
| 個人 | `~/.claude/skills/<name>/SKILL.md` | 自分の全プロジェクト |
| プロジェクト | `.claude/skills/<name>/SKILL.md` | このプロジェクトのみ(git 共有) |
| プラグイン | `<plugin>/skills/<name>/SKILL.md` | プラグインが有効な所 |

- 同名なら **enterprise > personal > project** の順で上書き。
- プロジェクトの `.claude/skills/` は、**起動ディレクトリから親をたどってリポジトリルートまで**自動発見されます(モノレポ対応)。
- **ライブ更新**: セッション中に `SKILL.md` を追加・編集・削除すると、再起動なしで反映されます(新規のトップレベル skills ディレクトリ作成時のみ再起動が必要)。

## 5-6. 補助ファイルでさらに強く

`SKILL.md` は本体を簡潔に保ち、詳細は別ファイルに逃がせます。これらは**必要な時だけ**ロードされます:

```text
my-skill/
├── SKILL.md          # 必須。概要とナビゲーション
├── reference.md      # 詳細リファレンス(必要時だけ読む)
├── examples.md       # 使用例(必要時だけ読む)
└── scripts/
    └── helper.py     # 実行するスクリプト(コンテキストには載らない)
```

`SKILL.md` から「このファイルには何があるか」を参照しておくと、Claude が適切なタイミングで読みます。**`SKILL.md` 本体は 500 行以内**に保つのが目安です。

> 🧩 **コンテキストとの接続**: ここが第3部と繋がります。長い API 仕様や設計資料を `reference.md` に置けば、**普段はコンテキストを消費せず**、必要な時だけ load される。これが「Skill は安い」の正体です。

---

# 第6部 — 4つの使い分け(全体像の総括)

ここまでの4概念は独立した機能ではなく、**「コンテキストという1つの制約」を中心に噛み合っています**。

```text
            ┌──────────────────────────────────────────┐
            │   制約: コンテキストはすぐ埋まり、         │
            │   埋まるほど AI の性能は落ちる(第3部)    │
            └──────────────────────────────────────────┘
                         ▲              ▲
        毎回必ず必要な    │              │   たまにしか要らない
        "短い事実" は…    │              │   "長い手順/資料" は…
                         │              │
                  ┌──────┴─────┐  ┌─────┴──────┐
                  │ CLAUDE.md  │  │   Skills    │
                  │  (第2部)   │  │   (第5部)   │
                  │ 常時ロード  │  │ 使う時だけ   │
                  └────────────┘  └─────────────┘

        そして「AIにどこまで任せ、どこで止めるか」を
        制御するのが Modes / Permissions(第4部)。
```

判断に迷ったら、この問いを使ってください:

| 入れたい情報の性質 | 置き場所 |
|---|---|
| 常に効く短い事実(スタイル、コマンド、禁止事項) | **CLAUDE.md** |
| たまに使う手順・長い参照資料 | **Skill** |
| 毎回必ず・例外なく実行したい決定的な処理(lint 等) | **Hook**(本教材では概説のみ) |
| 「いま会話に載っている情報」を減らしたい | **/clear・/compact・サブエージェント**(第3部) |
| 「AI の自律レベル」を上げ下げしたい | **Modes / permissions**(第4部) |

---

# 第7部 — チートシート(手元に置く用)

### コンテキスト管理
```text
/context                 いま机に何が載っているか可視化
/clear                   タスクの切れ目で会話を全消去(最頻出の技)
/compact [focus]         会話を要約して机を空ける(焦点指定可)
Esc Esc  /  /rewind      チェックポイントに巻き戻す
/btw <質問>              履歴を汚さずに小さな質問
「サブエージェントで調べて」  調査を別コンテキストに外注、要約だけ受け取る
```

### 権限モード(Shift+Tab で循環)
```text
Default            毎回確認
Accept-Edits       編集と一般ファイル操作は自動、他は確認
Plan               読み取り専用。調査と計画のみ
Auto               背後の安全チェック付きで自動承認(プレビュー)
bypassPermissions  全スキップ(隔離環境専用!)
/permissions       allow/ask/deny ルールを確認・編集
```

### CLAUDE.md
```text
/init                          コードベースから雛形生成
# <文章>                        その場でルールを追記
各行テスト: 「消したら AI がミスする?」しないなら消す
強調語(IMPORTANT/YOU MUST)は本当に守らせたい数行だけ
```

### Skills
```text
.claude/skills/<name>/SKILL.md  →  /<name> コマンドになる
description                      いつ使うかを Claude に伝える(自動起動の鍵)
disable-model-invocation: true  手動起動のみ(副作用のある手順向け)
allowed-tools                   有効な間だけ確認をスキップするツール
!`cmd` / ```! ブロック           前処理として実行し出力を埋め込む(動的注入)
$ARGUMENTS / $0 $1              引数の受け取り
context: fork + agent           サブエージェントで隔離実行
```

---

# 付録A — 推奨ワークフロー(Explore → Plan → Implement → Commit)

公式が最も推す4フェーズ。`my-task-api` で通して練習しましょう。

1. **Explore(探索)**: プランモードに入り、コードを読ませて理解させる(まだ書かせない)。
   ```text
   （plan mode）app.py を読んで、ルーティングと TaskStore の関係を説明して
   ```
2. **Plan(計画)**: 詳細な実装計画を作らせる。`Ctrl+G` でエディタに開いて直接修正も可。
   ```text
   （plan mode）done を切り替える PUT を足す計画を、変更ファイルと手順付きで
   ```
3. **Implement(実装)**: モードを抜けて実装。**計画と照合させながら**。
   ```text
   計画どおり実装し、テストを書いて unittest を流し、結果を貼って
   ```
4. **Commit(コミット)**: 説明的なメッセージでコミット。
   ```text
   Conventional Commits でコミットメッセージ案を出して
   ```

> **AI に「検証手段」を必ず渡す**のが品質の鍵です(テスト、ビルド、スクリーンショット)。AI は「できたっぽい」で止まります。合否を返す検証があれば、AI 自身がループを回して直し切ってくれます。「検証できないものは出荷しない」。

---

# 付録B — 出典(一次情報)

本教材は以下の Anthropic 公式ドキュメントを一次情報として作成しました(2026-06 時点)。

- Best practices for Claude Code(CLAUDE.md / ワークフロー / 失敗パターン)
  https://code.claude.com/docs/en/best-practices
- Extend Claude with skills(Skills / SKILL.md / フロントマター)
  https://code.claude.com/docs/en/skills
- How Claude Code works(エージェントループ / コンテキストウィンドウ)
  https://code.claude.com/docs/en/how-claude-code-works
- Configure permissions(権限システム / モード / ルール構文)
  https://code.claude.com/docs/en/permissions

補助記事(より広い視点が欲しい時に):
- The Complete Guide to CLAUDE.md(builder.io)
- Writing a good CLAUDE.md(HumanLayer Blog)
- What is a context window?(IBM)
- A complete guide to Claude Code permissions(eesel.ai)

---

## 次の一歩

この教材を終えたら、`my-task-api` に対して実際に手を動かしてみてください:

1. `/init` で CLAUDE.md を生成 → 第2部の指針で**刈り込む**
2. `.claude/settings.json` を書いて**承認連打から解放**される
3. `/smoke-test` と `/add-endpoint` の Skill を作って**手順をモジュール化**する
4. `PUT /tasks/{id}`(done の切り替え)を **Explore→Plan→Implement→Commit** で追加する
5. 長いセッションで `/context` を眺め、`/clear` と**サブエージェント**で机を管理する感覚を掴む

「上から順に読めば全部わかる」——ここまでがその全部です。あとは**あなたのプロジェクトで回す**だけです。
```