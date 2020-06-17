import unittest
import os
import itertools
import tempfile
import json
from pathlib import Path
from jinja2 import Template
from tests.conftest import ref_file_head
from tests.conftest import ref_template_head
import devopstemplate.pkg as pkg
from devopstemplate.template import DevOpsTemplate


class TestDevOpsTemplate(unittest.TestCase):

    def setUp(self):
        self.__ref_template_index_head = ref_file_head()

    def test_version(self):
        import devopstemplate
        version = devopstemplate.__version__
        ver_parts = version.split('.')
        self.assertEqual(len(ver_parts), 3)
        for part in ver_parts:
            self.assertGreaterEqual(int(part), 0)

    def test_render_file(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname)
            tmp_fname = 'tmp_file'
            tmp_fpath = os.path.join(tmpdirname, tmp_fname)
            template._DevOpsTemplate__render('MANIFEST.in', tmp_fpath,
                                             context={})
            with open(tmp_fpath, 'r') as tmp_fh:
                contents = tmp_fh.read()
                content_list = contents.splitlines()

        self.assertEqual(content_list[:len(self.__ref_template_index_head)],
                         self.__ref_template_index_head)

    def test_render_template(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname)
            tmp_fname = 'tmp_file'
            tmp_fpath = os.path.join(tmpdirname, tmp_fname)
            project_slug = 'project'
            context = {'project_slug': project_slug}
            template._DevOpsTemplate__render('{{project_slug}}/__init__.py',
                                             tmp_fpath,
                                             context=context)
            with open(tmp_fpath, 'r') as tmp_fh:
                contents = tmp_fh.read()
                content_list = contents.splitlines()
        ref_template_list = ref_template_head(project_slug)
        self.assertEqual(content_list[:len(ref_template_list)],
                         ref_template_list)

    def test_render_exists(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname)
            tmp_fname = 'tmp_file'
            tmp_path = Path(os.path.join(tmpdirname, tmp_fname))
            tmp_path.touch()
            with self.assertRaises(FileExistsError):
                template._DevOpsTemplate__render('MANIFEST.in', tmp_path,
                                                 context={})

    def test_render_skip(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname,
                                      skip_exists=True)
            tmp_fname = 'tmp_file'
            tmp_path = Path(os.path.join(tmpdirname, tmp_fname))
            tmp_path.touch()
            template._DevOpsTemplate__render('MANIFEST.in', tmp_path,
                                             context={})
            with open(tmp_path, 'r') as tmp_fh:
                contents = tmp_fh.read()
                self.assertEqual(contents, '')

    def test_render_overwrite(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname,
                                      overwrite_exists=True)
            tmp_fname = 'tmp_file'
            tmp_path = Path(os.path.join(tmpdirname, tmp_fname))
            tmp_path.touch()
            template._DevOpsTemplate__render('MANIFEST.in', tmp_path,
                                             context={})
            with open(tmp_path, 'r') as tmp_fh:
                contents = tmp_fh.read()
                content_list = contents.splitlines()

        self.assertEqual(content_list[:len(self.__ref_template_index_head)],
                         self.__ref_template_index_head)

    def test_render_pkgexists(self):
        template = DevOpsTemplate()
        with self.assertRaises(FileNotFoundError):
            template._DevOpsTemplate__render('non_existing_file', None,
                                             context={})

    def test_create(self):

        # Define test project
        projectconfig = {'project_name': 'project',
                         'project_slug': 'project',
                         'project_version': '0.1.0',
                         'project_url': '',
                         'project_description': '',
                         'author_name': 'full name',
                         'author_email': 'full.name@mail.com',
                         'add_scripts_dir': True,
                         'add_docs_dir': True,
                         'no_gitignore_file': False,
                         'no_readme_file': False,
                         'no_sonar': False}
        # Generate reference data
        project_file_list = []
        with pkg.stream('template.json') as fh:
            template_dict = json.load(fh)
            for fpath in itertools.chain(*template_dict.values()):
                # Render path
                fpath_template = Template('{{project_slug}}/__init__.py')
                fpath = fpath_template.render(**projectconfig)
                project_file_list.append(fpath)

        # Create test project
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname)
            template.create(projectconfig)
            # Make sure all files exist
            for fpath in project_file_list:
                fpath = os.path.join(tmpdirname, fpath)
                self.assertTrue(os.path.exists(fpath))
            # Check additional dirs
            self.assertTrue(os.path.exists(os.path.join(tmpdirname,
                                                        'scripts')))
            self.assertTrue(os.path.exists(os.path.join(tmpdirname,
                                                        'docs')))


class Jinja2RenderTest(unittest.TestCase):

    def test_render(self):
        context = {'project_slug': 'projectname', 'project_name': 'Name'}
        text = Template('{{project_slug}}/__init__.py').render(**context)
        self.assertEqual(text, 'projectname/__init__.py')

    def test_render_cc_templatevar(self):
        context = {'project_slug': '{{cookiecutter.project_name}}',
                   'project_name': 'Name'}
        text = Template('{{project_slug}}/__init__.py').render(**context)
        self.assertEqual(text, '{{cookiecutter.project_name}}/__init__.py')


if __name__ == "__main__":
    unittest.main()
