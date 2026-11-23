"""Real MongoDB and Streamlit checks; no writes to the course database."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from pymongo import MongoClient
from streamlit.testing.v1 import AppTest
import aggregation_queries as q

ROOT = Path(__file__).resolve().parent
MONGOD = os.environ.get("MONGOD") or shutil.which("mongod")
EXPECTED = [
    {"year": 1990, "rated_movies": 2, "mean_rating": 7.0, "total_votes": 3000},
    {"year": 1991, "rated_movies": 1, "mean_rating": 7.5, "total_votes": 1500},
]

class ValidationTests(unittest.TestCase):
    def test_bad_inputs(self):
        for args in [(2000, 1990, 1000), (1700, 1990, 0), (1990, 1991, -1)]:
            with self.assertRaises(ValueError):
                q.build_pipeline(*args)

    def test_missing_connection_setting(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                q.connect()

@unittest.skipUnless(MONGOD, "Live checks require mongod on PATH or MONGOD")
class LiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="chapter17-")
        cls.addClassCleanup(cls.temp.cleanup)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        cls.process = subprocess.Popen(
            [MONGOD, "--dbpath", cls.temp.name, "--bind_ip", "127.0.0.1",
             "--port", str(port), "--logpath", str(Path(cls.temp.name)/"mongo.log")],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        def stop():
            cls.process.terminate()
            try:
                cls.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                cls.process.kill(); cls.process.wait()
        cls.addClassCleanup(stop)
        cls.uri = f"mongodb://127.0.0.1:{port}/?directConnection=true"
        cls.client = MongoClient(cls.uri, serverSelectionTimeoutMS=500)
        cls.addClassCleanup(cls.client.close)
        for _ in range(40):
            try:
                cls.client.admin.command("ping")
                break
            except Exception:
                if cls.process.poll() is not None:
                    raise RuntimeError((Path(cls.temp.name)/"mongo.log").read_text())
                time.sleep(.2)
        else:
            raise RuntimeError("Temporary MongoDB did not start")
        cls.db = cls.client.chapter17_test
        # Good rows, low votes, no rating, wrong kind/year, and missing values.
        cls.db.titles.insert_many([
            {"_id": key, "title_type": kind, "start_year": year}
            for key, kind, year in [
                ("A", "movie", 1990), ("B", "movie", 1990),
                ("C", "movie", 1991), ("D", "movie", 1991),
                ("E", "movie", 1991), ("F", "short", 1990),
                ("G", "movie", None), ("H", "movie", 2000),
                ("I", "movie", 1991), ("J", "movie", 1991)]])
        cls.db.ratings.insert_many([
            {"_id": key, "average_rating": rating, "num_votes": votes}
            for key, rating, votes in [
                ("A", 8.0, 2000), ("B", 6.0, 1000), ("C", 9.0, 500),
                ("D", 7.5, 1500), ("F", 10.0, 2000), ("G", 10.0, 2000),
                ("H", 10.0, 2000), ("I", None, 2000), ("J", 9.0, None)]])
        print("MongoDB", cls.client.server_info()["version"], "isolated fixture ready")

    def test_group_mean_counts_and_exclusions(self):
        self.assertEqual(q.summarize(self.db, q.build_pipeline()), EXPECTED)

    def test_threshold_and_inclusive_year(self):
        self.assertEqual(q.summarize(self.db, q.build_pipeline(1990, 1990, 1500)),
                         [{"year": 1990, "rated_movies": 1,
                           "mean_rating": 8.0, "total_votes": 2000}])

    def test_empty_result(self):
        self.assertEqual(q.summarize(self.db, q.build_pipeline(1990, 1999, 10000)), [])

    def test_fixture_index_and_explain(self):
        self.db.titles.create_index([("title_type", 1), ("start_year", 1)], name="fixture_type_year")
        started = time.perf_counter()
        rows = q.summarize(self.db, q.build_pipeline())
        elapsed = (time.perf_counter() - started) * 1000
        report = self.db.command("explain", {"aggregate": "titles", "pipeline": q.build_pipeline(),
                                             "cursor": {}, "hint": "fixture_type_year"}, verbosity="executionStats")
        self.assertIn("IXSCAN", json.dumps(report))
        self.assertEqual(rows, EXPECTED)
        print(f"Fixture only: {len(rows)} rows, {elapsed:.2f} ms; compound index present; hinted explain IXSCAN")

    def test_cli(self):
        env = dict(os.environ, MONGODB_URI=self.uri, MONGODB_DATABASE=self.db.name)
        result = subprocess.run([sys.executable, str(ROOT/"aggregation_queries.py")],
                                env=env, text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), EXPECTED)

    def test_streamlit_results_empty_and_bad_years(self):
        with patch.dict(os.environ, {"MONGODB_URI": self.uri, "MONGODB_DATABASE": self.db.name}):
            app = AppTest.from_file(str(ROOT/"imdb_aggregation.py"), default_timeout=30).run()
            app.button[0].click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.dataframe[0].value.to_dict("records"), EXPECTED)
            app.number_input[2].set_value(10000)
            app.button[0].click().run()
            self.assertIn("No qualifying movies", app.info[0].value)
            app.number_input[0].set_value(2000)
            app.button[0].click().run()
            self.assertIn("ordered year range", app.error[0].value)
            self.assertEqual(len(app.exception), 0)

if __name__ == "__main__":
    unittest.main()
