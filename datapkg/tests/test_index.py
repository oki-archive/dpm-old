import os
import tempfile

import datapkg.tests.base
import datapkg.index
import datapkg.package

class TestSimpleIndex(datapkg.tests.base.TestCase):
    def setup(self):
        self.index = datapkg.index.SimpleIndex()

    def test_has_register_update(self):
        pkg_name = u'blah'
        assert not self.index.has(pkg_name)

        pkg = datapkg.package.Package(name=pkg_name)
        self.index.register(pkg)
        assert self.index.has(pkg_name)
        self.index.update(pkg)

    def test_get(self):
        pkg_name = u'blah'
        pkg = datapkg.package.Package(name=pkg_name)
        self.index.register(pkg)
        out = self.index.get(pkg_name)
        assert out.name == pkg_name
        

class TestFileIndex(TestSimpleIndex):
    def setup(self):
        self.make_tmpdir()
        self.index = datapkg.index.FileIndex(self.tmpdir)


class TestDbIndex(TestSimpleIndex):
    tmpfile = '/tmp/datapkg.db'
    dburi = 'sqlite:///%s' % tmpfile

    def setup(self):
        if os.path.exists(self.tmpfile):
            os.remove(self.tmpfile)
        self.index = datapkg.index.DbIndex(self.dburi)
        self.index.init()

    def test_db_ok(self):
        assert self.index.dburi is not None
        assert os.path.exists(self.tmpfile)

    def test_list(self):
        pkgs = self.index.list()
        assert len(pkgs) == 0

        pkg = datapkg.package.Package(name=u'blah')
        self.index.register(pkg)
        pkgs = self.index.list()
        assert len(pkgs) == 1

    def test_get_when_loaded_as_new_and_init_not_called(self):
        pkg_name = u'blah'
        pkg = datapkg.package.Package(name=pkg_name)
        self.index.register(pkg)

        # clear session so we know this is loaded from db
        self.index.session.clear()

        out = self.index.get(pkg_name)
        assert out.name == pkg_name

