import unittest
from unittest.mock import patch
from argparse import Namespace
from devopstemplate.config import CommandsConfig
import devopstemplate.main


class TestMain(unittest.TestCase):

    @patch('devopstemplate.main.create')
    def test_parse_create(self, mock_create):
        # test with default parameters
        arg_list = ['create']
        devopstemplate.main.parse_args(arg_list)
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.package_name = None
        args_ns.project_version = '0.1.0'
        args_ns.project_url = ''
        args_ns.project_description = ''
        user, email = CommandsConfig.git_user()
        args_ns.author_name = user
        args_ns.author_email = email
        args_ns.no_gitignore_file = False
        args_ns.no_sonar = False
        args_ns.add_mongo = False
        args_ns.add_mlflow = False
        args_ns.overwrite_exists = False
        args_ns.skip_exists = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.version = False
        args_ns.dry_run = False
        args_ns.interactive = False
        args_ns.func = mock_create

        mock_create.assert_called_with(args_ns)

        # test with package name provided by user
        arg_list = ['create', '--package-name', 'test']
        devopstemplate.main.parse_args(arg_list)
        args_ns.package_name = 'test'

        mock_create.assert_called_with(args_ns)

    @patch('devopstemplate.main.manage')
    def test_parse_manage(self, mock_manage):
        arg_list = ['manage']
        devopstemplate.main.parse_args(arg_list)
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.add_gitignore_file = False
        args_ns.add_sonar = False
        args_ns.add_mongo = False
        args_ns.add_mlflow = False
        args_ns.overwrite_exists = False
        args_ns.skip_exists = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.version = False
        args_ns.dry_run = False
        args_ns.func = mock_manage

        mock_manage.assert_called_with(args_ns)

    @patch('devopstemplate.main.cookiecutter')
    def test_parse_cookiecutter(self, mock_cookiecutter):
        arg_list = ['cookiecutter']
        devopstemplate.main.parse_args(arg_list)
        args_ns = Namespace()
        args_ns.project_dir = '.'
        args_ns.project_name = ''
        args_ns.project_version = '0.1.0'
        args_ns.project_url = ''
        args_ns.project_description = ''
        args_ns.author_name = ''
        args_ns.author_email = ''
        args_ns.overwrite_exists = False
        args_ns.skip_exists = False
        args_ns.verbose = False
        args_ns.quiet = False
        args_ns.version = False
        args_ns.dry_run = False
        args_ns.interactive = False
        args_ns.func = mock_cookiecutter

        mock_cookiecutter.assert_called_with(args_ns)


if __name__ == "__main__":
    unittest.main()
