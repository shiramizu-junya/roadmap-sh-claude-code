import unittest

from app import NotesStore


class NotesStoreTest(unittest.TestCase):
    def setUp(self):
        # 各テストごとにまっさらな箱を用意する(テスト間で状態を共有しない)
        self.store = NotesStore()

    # --- create:id は 1 から連番で振られる ---
    def test_create_assigns_sequential_ids_from_1(self):
        first = self.store.create("a", "body-a")
        second = self.store.create("b", "body-b")
        third = self.store.create("c", "body-c")

        self.assertEqual(first["id"], 1)
        self.assertEqual(second["id"], 2)
        self.assertEqual(third["id"], 3)

    def test_create_returns_stored_fields(self):
        note = self.store.create("title", "body")
        self.assertEqual(note, {"id": 1, "title": "title", "body": "body"})

    # --- list:作った分だけ返す ---
    def test_list_empty_returns_empty_list(self):
        self.assertEqual(self.store.list(), [])

    def test_list_returns_only_created_notes(self):
        self.store.create("a", "1")
        self.store.create("b", "2")

        notes = self.store.list()
        self.assertEqual(len(notes), 2)
        titles = [n["title"] for n in notes]
        self.assertEqual(titles, ["a", "b"])

    # --- get:存在しない id は KeyError(HTTP 層で 404 相当に変換される) ---
    def test_get_missing_id_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.store.get(999)

    def test_get_returns_created_note(self):
        created = self.store.create("a", "1")
        fetched = self.store.get(created["id"])
        self.assertEqual(fetched, created)

    # --- delete:削除後に get すると「無い」扱いになる ---
    def test_get_after_delete_raises_keyerror(self):
        created = self.store.create("a", "1")
        self.store.delete(created["id"])

        with self.assertRaises(KeyError):
            self.store.get(created["id"])

    def test_delete_removes_only_target(self):
        keep = self.store.create("keep", "1")
        drop = self.store.create("drop", "2")

        self.store.delete(drop["id"])

        self.assertEqual(len(self.store.list()), 1)
        self.assertEqual(self.store.get(keep["id"]), keep)

    def test_delete_missing_id_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.store.delete(123)

    # ============================================================
    # エッジケース
    # ============================================================

    # 空文字の title でも作成できる(バリデーションは store の責務ではない)
    def test_create_allows_empty_title(self):
        note = self.store.create("", "body")
        self.assertEqual(note["title"], "")
        self.assertEqual(self.store.get(note["id"]), note)

    # 同じ内容を2回 create しても id は別になる(中身は同じでも別レコード)
    def test_create_same_content_twice_gets_distinct_ids(self):
        a = self.store.create("same", "same")
        b = self.store.create("same", "same")

        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual([a["id"], b["id"]], [1, 2])
        self.assertEqual(len(self.store.list()), 2)

    # 削除しても次の id は欠番を埋め直さず増え続ける(id の使い回しをしない)
    def test_ids_do_not_get_reused_after_delete(self):
        first = self.store.create("a", "1")
        self.store.delete(first["id"])
        second = self.store.create("b", "2")

        self.assertEqual(second["id"], 2)

    # update:渡した項目だけ上書きし、None は据え置く
    def test_update_overwrites_only_given_fields(self):
        note = self.store.create("old-title", "old-body")

        updated = self.store.update(note["id"], title="new-title")
        self.assertEqual(updated["title"], "new-title")
        self.assertEqual(updated["body"], "old-body")  # None なので据え置き

    def test_update_missing_id_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.store.update(999, title="x")


if __name__ == "__main__":
    unittest.main()
