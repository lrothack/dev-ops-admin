import unittest
from unittest.mock import patch
from argparse import Namespace
import devopstemplate.main


class TestMain(unittest.TestCase):

    @patch('devopstemplate.main.create')
    def test_parse_create(self, mock_create):
        arg_list = ['create', 'test']
        devopstemplate.main.parse_args(arg_list)
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.projectname = 'test'
        args_ns.add_scripts_dir = False
        args_ns.add_docs_dir = False
        args_ns.no_gitignore_file = False
        args_ns.no_readme_file = False
        args_ns.no_sonar = False
        args_ns.no_docker = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.func = mock_create

        mock_create.assert_called_with(args_ns)

        # mock_create.assert_called()
        # args, _ = mock_create.call_args
        # self.assertEqual(vars(args[0]), vars(args_ns))

    @patch('devopstemplate.main.manage')
    def test_parse_manage(self, mock_manage):
        arg_list = ['manage']
        devopstemplate.main.parse_args(arg_list)
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.add_scripts_dir = False
        args_ns.add_docs_dir = False
        args_ns.add_gitignore_file = False
        args_ns.add_readme_file = False
        args_ns.add_sonar = False
        args_ns.add_docker = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.func = mock_manage

        mock_manage.assert_called_with(args_ns)


if __name__ == "__main__":
    unittest.main()
