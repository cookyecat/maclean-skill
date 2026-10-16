#!/usr/bin/env python3
"""Synthetic, privacy-scoped Playwright .links parser regressions."""
import json,pathlib,tempfile,unittest
from client_reference_guard import scan_fixture_links,LinkDenied

class ClientLinkTests(unittest.TestCase):
    def fixture(self):
        t=tempfile.TemporaryDirectory(prefix="maclean-v06-links-")
        root=pathlib.Path(t.name).resolve();root.chmod(0o700)
        (root/"browser-cache"/".links").mkdir(parents=True)
        p=root/"clients"/"client-ALPHA";p.mkdir(parents=True)
        (p/"package.json").write_text('{"version":"1.64.1"}')
        (p/"browsers.json").write_text('{"browsers":[{"name":"chromium","revision":"1248"}]}')
        (root/"browser-cache"/".links"/"one").write_text(str(p))
        return t,root,p

    def test_expected_client_yields_metadata_only(self):
        t,r,p=self.fixture()
        with t:
            o=scan_fixture_links(r,expected_clients={"client-ALPHA"})
            self.assertEqual(o["client_links_verified"],1)
            self.assertEqual(o["browser_descriptor_counts"],[1])
            self.assertFalse(o["deletion_authorized"])
            self.assertFalse(o["full_host_client_universe_proven"])

    def test_home_not_scannable(self):
        with self.assertRaises(LinkDenied):
            scan_fixture_links(pathlib.Path.home(),expected_clients={"client-ALPHA"})

    def test_external_target_denied_before_read(self):
        t,r,p=self.fixture()
        with t:
            (r/"browser-cache"/".links"/"one").write_text(str(pathlib.Path.home()))
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_unapproved_peer_client_denied(self):
        t,r,p=self.fixture()
        with t:
            (r/"browser-cache"/".links"/"one").write_text(str(p.parent/"client-OTHER"))
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_link_symlink_denied(self):
        t,r,p=self.fixture()
        with t:
            q=r/"browser-cache"/".links"/"one";q.unlink();q.symlink_to(pathlib.Path.home())
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_manifest_symlink_denied(self):
        t,r,p=self.fixture()
        with t:
            f=p/"package.json";f.unlink();f.symlink_to(pathlib.Path.home())
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_broken_or_missing_manifest_denied(self):
        for filename in ("package.json","browsers.json"):
            t,r,p=self.fixture()
            with t:
                (p/filename).unlink()
                with self.assertRaises(LinkDenied):
                    scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_invalid_browsers_manifest_denied(self):
        t,r,p=self.fixture()
        with t:
            (p/"browsers.json").write_text('{"browsers":{}}')
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_duplicate_client_link_denied(self):
        t,r,p=self.fixture()
        with t:
            (r/"browser-cache"/".links"/"two").write_text(str(p))
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_oversized_link_denied(self):
        t,r,p=self.fixture()
        with t:
            (r/"browser-cache"/".links"/"one").write_text("x"*513)
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_newline_link_denied(self):
        t,r,p=self.fixture()
        with t:
            (r/"browser-cache"/".links"/"one").write_text(str(p)+"\n")
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_world_readable_root_denied(self):
        t,r,p=self.fixture()
        with t:
            r.chmod(0o755)
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_no_links_denied_as_incomplete(self):
        t,r,p=self.fixture()
        with t:
            (r/"browser-cache"/".links"/"one").unlink()
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"client-ALPHA"})

    def test_unknown_client_allowlist_denied(self):
        t,r,p=self.fixture()
        with t:
            with self.assertRaises(LinkDenied):
                scan_fixture_links(r,expected_clients={"../../../anything"})

if __name__=="__main__":unittest.main(verbosity=2)
