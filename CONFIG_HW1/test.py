import unittest
import tarfile
import tempfile
from main import VirtualFileSystem

class TestVirtualFileSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tar_file = tempfile.NamedTemporaryFile(delete=False)
        with tarfile.open(cls.tar_file.name, 'w') as tar:
            structure = [
                "vfs/",
                "vfs/home/",
                "vfs/home/user/",
                "vfs/home/user/file1.txt",
                "vfs/home/user/file2.txt",
                "vfs/home/user/games/",
                "vfs/home/user/games/gta",
                "vfs/home/user/games/skyrim",
                "vfs/home/user/images/",
                "vfs/home/user/images/2023/",
                "vfs/home/user/images/2023/winter",
                "vfs/home/user/images/2024/",
                "vfs/home/user/images/2024/summer",
            ]
            for item in structure:
                tarinfo = tarfile.TarInfo(item)
                tarinfo.size = 0
                tar.addfile(tarinfo)

    def setUp(self):
        self.vfs = VirtualFileSystem(self.tar_file.name)

    # Тесты для команды 'ls'
    def test_ls_root(self):
        self.assertEqual(self.vfs.ls(), ['vfs'])

    def test_ls_home_user(self):
        self.vfs.cd('vfs')
        self.vfs.cd('home')
        self.vfs.cd('user')
        self.assertEqual(sorted(self.vfs.ls()), ['file1.txt', 'file2.txt', 'games', 'images'])

    def test_ls_games(self):
        self.vfs.cd('vfs')
        self.vfs.cd('home')
        self.vfs.cd('user')
        self.vfs.cd('games')
        self.assertEqual(sorted(self.vfs.ls()), ['gta', 'skyrim'])

    # Тесты для команды 'cd'
    def test_cd_to_home(self):
        self.vfs.cd('vfs')
        self.vfs.cd('home')
        self.assertEqual(self.vfs.pwd(), '/vfs/home')

    def test_cd_to_games(self):
        self.vfs.cd('vfs')
        self.vfs.cd('home')
        self.vfs.cd('user')
        self.vfs.cd('games')
        self.assertEqual(self.vfs.pwd(), '/vfs/home/user/games')

    def test_cd_to_parent(self):
        self.vfs.cd('vfs')
        self.vfs.cd('home')
        self.vfs.cd('user')
        self.vfs.cd('games')
        self.vfs.cd('..')
        self.assertEqual(self.vfs.pwd(), '/vfs/home/user')

    # Тесты для команды 'pwd'
    def test_pwd_root(self):
        self.assertEqual(self.vfs.pwd(), '/')

    def test_pwd_in_user_dir(self):
        self.vfs.cd('vfs')
        self.vfs.cd('home')
        self.vfs.cd('user')
        self.assertEqual(self.vfs.pwd(), '/vfs/home/user')

    def test_pwd_in_images_2024_summer(self):
        self.vfs.cd('vfs')
        self.vfs.cd('home')
        self.vfs.cd('user')
        self.vfs.cd('images')
        self.vfs.cd('2024')
        self.vfs.cd('summer')
        self.assertEqual(self.vfs.pwd(), '/vfs/home/user/images/2024/summer')

    # Тесты для команды 'tree'
    def test_tree_root(self):
        expected_tree = "vfs\n  home\n    user\n      file1.txt\n      file2.txt\n      games\n        gta\n        skyrim\n      images\n        2023\n          winter\n        2024\n          summer\n"
        self.assertEqual(self.vfs.tree(), expected_tree)

    def test_tree_user(self):
        self.vfs.cd('vfs')
        self.vfs.cd('home')
        self.vfs.cd('user')
        expected_tree = "file1.txt\nfile2.txt\ngames\n  gta\n  skyrim\nimages\n  2023\n    winter\n  2024\n    summer\n"
        self.assertEqual(self.vfs.tree(), expected_tree)

    def test_tree_games(self):
        self.vfs.cd('vfs')
        self.vfs.cd('home')
        self.vfs.cd('user')
        self.vfs.cd('games')
        expected_tree = "gta\nskyrim\n"
        self.assertEqual(self.vfs.tree(), expected_tree)

if __name__ == '__main__':
    unittest.main()
