import os
import shutil
import tempfile
import unittest
from ghost.core.coder import GhostCodeAgent
from ghost.ui.api import GhostBridgeAPI


class TestGhostCodeAgent(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="ghost_coder_test_")
        self.agent = GhostCodeAgent(workspace_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_and_read_file(self):
        rel_path = "src/demo.py"
        content = "print('Hello GhostOS v2.0')\n"
        res_write = self.agent.write_file(rel_path, content)
        self.assertTrue(res_write["success"])
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, rel_path)))

        res_read = self.agent.read_file(rel_path)
        self.assertTrue(res_read["success"])
        self.assertIn("Hello GhostOS v2.0", res_read["content"])

    def test_edit_file_with_diff(self):
        rel_path = "calc.py"
        initial_content = "def add(a, b):\n    return a - b\n"
        self.agent.write_file(rel_path, initial_content)

        target = "return a - b"
        replacement = "return a + b"
        res_edit = self.agent.edit_file(rel_path, target, replacement)

        self.assertTrue(res_edit["success"])
        self.assertIn("+    return a + b", res_edit["diff"])
        self.assertIn("-    return a - b", res_edit["diff"])

        res_read = self.agent.read_file(rel_path)
        self.assertIn("return a + b", res_read["content"])

    def test_list_dir_and_search_code(self):
        self.agent.write_file("app/main.py", "secret_token = 'ghost_token_xyz'\n")
        self.agent.write_file("app/utils.py", "def helper(): pass\n")

        res_list = self.agent.list_dir()
        self.assertTrue(res_list["success"])
        file_paths = [f["path"] for f in res_list["tree"]]
        self.assertIn("app/main.py", file_paths)
        self.assertIn("app/utils.py", file_paths)

        search_res = self.agent.search_code("secret_token")
        self.assertTrue(search_res["success"])
        self.assertEqual(search_res["count"], 1)
        self.assertEqual(search_res["matches"][0]["file"], "app/main.py")
        self.assertEqual(search_res["matches"][0]["line"], 1)

    def test_scaffold_project_fastapi(self):
        res = self.agent.scaffold_project("fastapi", "my_fastapi_app")
        self.assertTrue(res["success"])
        created = res["created_files"]
        self.assertIn("my_fastapi_app/main.py", created)
        self.assertIn("my_fastapi_app/requirements.txt", created)
        self.assertIn("my_fastapi_app/test_main.py", created)

        # Verify test file content
        test_file = self.agent.read_file("my_fastapi_app/test_main.py")
        self.assertTrue(test_file["success"])
        self.assertIn("TestClient", test_file["content"])

    def test_run_command_safe(self):
        res = self.agent.run_command("echo 'GhostCode Rocks'")
        self.assertTrue(res["success"])
        self.assertIn("GhostCode Rocks", res["stdout"])

    def test_run_command_destructive_blocked(self):
        res = self.agent.run_command("rm -rf /")
        self.assertFalse(res["success"])
        self.assertTrue(res.get("blocked", False))
        self.assertIn("blocked", res["error"])

    def test_run_task_autonomous(self):
        task = "создай файл hello.txt с текстом 'Привет GhostOS'"
        steps_log = []
        callback = lambda event: steps_log.append(event)

        res = self.agent.run_task(task, event_callback=callback)
        self.assertTrue(res["success"])
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "hello.txt")))
        read_res = self.agent.read_file("hello.txt")
        self.assertTrue(read_res["success"])
        self.assertIn("Привет GhostOS", read_res["content"])


class TestGhostStudioApi(unittest.TestCase):
    def setUp(self):
        self.api = GhostBridgeAPI()

    def test_get_coder_and_workspace(self):
        info = self.api.get_workspace_info()
        self.assertEqual(info["status"], "ok")
        self.assertIn("workspace", info)
        self.assertIn("files", info)
        self.assertIn("tree", info)
        self.assertIn("git", info)

    def test_save_and_read_code_file_api(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.api.set_workspace_path(tmp_dir)
            save_res = self.api.save_code_file("demo.py", "# Live Editor Test")
            self.assertEqual(save_res["status"], "ok")
            self.assertGreater(save_res["bytes"], 0)

            read_res = self.api.read_code_file("demo.py")
            self.assertEqual(read_res["status"], "ok")
            self.assertIn("# Live Editor Test", read_res["content"])

    def test_studio_terminal_api(self):
        res = self.api.run_studio_terminal("echo 'Terminal Online'")
        self.assertEqual(res["status"], "ok")
        self.assertIn("Terminal Online", res["output"])


if __name__ == "__main__":
    unittest.main()
