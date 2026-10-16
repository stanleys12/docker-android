import os
import shutil
import tempfile
import mock

from helper import convert_str_to_bool, get_env_value_or_raise, get_log_file, symlink_force
from tests import BaseTest


class TestHelperMethods(BaseTest):
    def test_boolean_converter_with_valid_str(self):
        self.assertEqual(convert_str_to_bool("TRUE"), True)
        self.assertEqual(convert_str_to_bool("true"), True)
        self.assertEqual(convert_str_to_bool("T"), True)
        self.assertEqual(convert_str_to_bool("Yes"), True)
        self.assertEqual(convert_str_to_bool("1"), True)
        self.assertEqual(convert_str_to_bool("False"), False)
        self.assertEqual(convert_str_to_bool("f"), False)
        self.assertEqual(convert_str_to_bool("0"), False)

    def test_boolean_converter_with_empty(self):
        self.assertEqual(convert_str_to_bool(None), False)
        self.assertEqual(convert_str_to_bool(""), False)

    def test_boolean_converter_with_invalid_str(self):
        self.assertEqual(convert_str_to_bool(" "), False)
        self.assertEqual(convert_str_to_bool("test"), False)

    def test_boolean_converter_with_invalid_format(self):
        with self.assertRaises(AttributeError):
            convert_str_to_bool(True)

    def test_get_env_value_from_valid_key(self):
        env_key = "env_key01"
        os.environ[env_key] = "env_value01"
        get_env_value_or_raise(env_key)
        del os.environ[env_key]

    def test_get_env_value_with_empty_string(self):
        with self.assertRaises(RuntimeError):
            env_key = "env_key01"
            os.environ[env_key] = "    "
            get_env_value_or_raise(env_key)
            del os.environ[env_key]

    def test_get_env_value_from_invalid_key(self):
        with self.assertRaises(RuntimeError):
            get_env_value_or_raise("env_key02")

    def test_symlink(self):
        s = os.path.join("source.txt")
        t = os.path.join("target_file.txt")
        open(s, "a").close()
        symlink_force(s, t)
        os.remove(s)
        os.remove(t)

    def test_symlink_already_exist(self):
        s = os.path.join("source.txt")
        t = os.path.join("target_file.txt")
        open(s, "a").close()
        open(t, "a").close()
        symlink_force(s, t)
        os.remove(s)
        os.remove(t)

    def test_symlink_file_not_exists(self):
        s = os.path.join("source.txt")
        t = os.path.join("target_file.txt")
        symlink_force(s, t)
        os.remove(t)

    def test_get_log_file(self):
        log_path = tempfile.mkdtemp()
        open(os.path.join(log_path, "device.stdout.log"), "a").close()
        os.mkdir(os.path.join(log_path, "subdir"))
        self.assertEqual(get_log_file(log_path, "/device.stdout.log"),
                         os.path.realpath(os.path.join(log_path, "device.stdout.log")))
        self.assertIsNone(get_log_file(log_path, "/missing.log"))
        self.assertIsNone(get_log_file(log_path, "/subdir"))
        shutil.rmtree(log_path)

    def test_get_log_file_outside_log_path(self):
        parent = tempfile.mkdtemp()
        log_path = os.path.join(parent, "logs")
        os.mkdir(log_path)
        secret = os.path.join(parent, "secret.txt")
        open(secret, "a").close()
        os.symlink(secret, os.path.join(log_path, "link.log"))
        self.assertIsNone(get_log_file(log_path, "/../secret.txt"))
        self.assertIsNone(get_log_file(log_path, "/%2e%2e/secret.txt"))
        self.assertIsNone(get_log_file(log_path, "/%2e%2e%2fsecret.txt"))
        self.assertIsNone(get_log_file(log_path, "//" + secret))
        self.assertIsNone(get_log_file(log_path, "/link.log"))
        self.assertIsNone(get_log_file(log_path, "/a%00b"))
        shutil.rmtree(parent)
