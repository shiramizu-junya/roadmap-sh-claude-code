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
