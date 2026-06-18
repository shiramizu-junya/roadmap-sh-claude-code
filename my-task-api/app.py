from http.server import BaseHTTPRequestHandler, HTTPServer
import json


# ============================================================
# データ層:タスクを保存する箱(メモリ上の辞書。再起動で消える)
# ============================================================
class TaskStore:
    def __init__(self):
        self._tasks = {}  # id(int) -> task(dict)
        self._next_id = 1  # 次に振る id

    def list(self):
        return list(self._tasks.values())

    def create(self, title):
        task = {"id": self._next_id, "title": title, "done": False}
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id):
        return self._tasks[task_id]  # 無ければ KeyError

    def delete(self, task_id):
        del self._tasks[task_id]  # 無ければ KeyError


# プロセス全体で1つだけ共有する箱
store = TaskStore()


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
            task_id = int(self.path.split("/")[2])  # "/tasks/3" → 3
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
