import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer


# ============================================================
# データ層:メモを保存する箱(今回はメモリ上の辞書。再起動で消える)
# ============================================================
class NotesStore:
    def __init__(self):
        self._notes = {}  # id(int) -> note(dict) の対応表
        self._next_id = 1  # 次に振る id

    def list(self):
        # 値(メモ)だけをリストにして返す
        print(self._notes)
        return list(self._notes.values())

    def create(self, title, body):
        note = {"id": self._next_id, "title": title, "body": body}
        self._notes[self._next_id] = note
        self._next_id += 1
        return note

    def get(self, note_id):
        return self._notes[note_id]

    def update(self, note_id, title=None, body=None):
        note = self._notes[note_id]  # 無ければ KeyError
        # 渡された項目だけ上書きする(None はそのまま据え置き)
        if title is not None:
            note["title"] = title
        if body is not None:
            note["body"] = body
        return note

    def delete(self, note_id):
        del self._notes[note_id]


# プロセス全体で1つだけ共有する箱
store = NotesStore()


# ============================================================
# HTTP 層:リクエストを受けて store を呼び、JSON を返す
# ============================================================
class Handler(BaseHTTPRequestHandler):
    # --- 共通のヘルパー:status と payload(dict)を JSON で返す ---
    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # --- 共通のヘルパー:リクエスト本文を JSON として読む ---
    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        return json.loads(raw)

    # --- 各エンドポイントの処理(引数 match は path に対する正規表現マッチ結果) ---
    def _health(self, match):
        self._send(200, {"status": "ok"})

    def _list_notes(self, match):
        self._send(200, {"notes": store.list()})

    def _get_note(self, match):
        # 正規表現で取り出した id を数値に変換(非数値なら ValueError → 500)
        note_id = int(match.group("id"))
        try:
            note = store.get(note_id)
        except KeyError:
            self._send(404, {"error": "not found"})
            return
        self._send(200, note)

    def _create_note(self, match):
        data = self._read_json()
        # ← "title" や "body" が無いと KeyError → 500
        note = store.create(data["title"], data["body"])
        self._send(201, note)

    def _update_note(self, match):
        note_id = int(match.group("id"))
        data = self._read_json()
        try:
            # title / body は任意。あるものだけ更新する
            note = store.update(note_id, data.get("title"), data.get("body"))
        except KeyError:
            self._send(404, {"error": "not found"})
            return
        self._send(200, note)

    def _delete_note(self, match):
        note_id = int(match.group("id"))
        try:
            store.delete(note_id)
        except KeyError:
            self._send(404, {"error": "not found"})
            return
        self._send(200, {"deleted": note_id})

    # --- ルーティングテーブル:(メソッド, パスの正規表現, ハンドラ) ---
    #   完全一致は "$" 付き、"/notes/{id}" は終端アンカー無しの [^/]* で、
    #   従来の == / startswith("/notes/") の挙動をそのまま再現する。
    ROUTES = [
        ("GET", re.compile(r"^/health$"), _health),
        ("GET", re.compile(r"^/notes$"), _list_notes),
        ("GET", re.compile(r"^/notes/(?P<id>[^/]*)"), _get_note),
        ("POST", re.compile(r"^/notes$"), _create_note),
        ("PUT", re.compile(r"^/notes/(?P<id>[^/]*)"), _update_note),
        ("DELETE", re.compile(r"^/notes/(?P<id>[^/]*)"), _delete_note),
    ]

    # --- 共通のディスパッチャ:メソッドと path から該当ハンドラを探して呼ぶ ---
    def _dispatch(self, method):
        for route_method, pattern, handler in self.ROUTES:
            if route_method == method:
                match = pattern.match(self.path)
                if match:
                    handler(self, match)
                    return
        self._send(404, {"error": "not found"})

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def do_PUT(self):
        self._dispatch("PUT")

    def do_DELETE(self):
        self._dispatch("DELETE")


def main():
    server = HTTPServer(("127.0.0.1", 8000), Handler)
    server.allow_reuse_address = True
    print("Starting server at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
