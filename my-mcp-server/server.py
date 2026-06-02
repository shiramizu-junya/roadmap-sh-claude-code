# server.py
# 目的: 最小の MCP サーバー。Claude が呼べるツールを1つ公開する。

from mcp.server.fastmcp import FastMCP
import httpx

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


if __name__ == "__main__":
    # 引数なしの run() は stdio トランスポートで起動する(ローカル定番)
    mcp.run()
