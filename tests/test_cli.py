"""Tests for CLI commands."""

import os

from click.testing import CliRunner

from corpuslab.cli import cli


class TestCli:
    def setup_method(self):
        self.runner = CliRunner()

    def test_version(self):
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_generate(self, tmp_path):
        output = str(tmp_path / "gen.txt")
        result = self.runner.invoke(cli, ["generate", "-n", "20", "-o", output])
        assert result.exit_code == 0
        assert os.path.exists(output)

    def test_import_and_summarize(self, tmp_path, sample_text_path):
        corpus = str(tmp_path / "corpus.jsonl")
        result = self.runner.invoke(cli, ["import", sample_text_path, "-o", corpus, "--overwrite"])
        assert result.exit_code == 0
        assert "Imported" in result.output

        result = self.runner.invoke(cli, ["summarize", corpus])
        assert result.exit_code == 0
        assert "Total records:" in result.output

    def test_filter(self, tmp_corpus):
        result = self.runner.invoke(cli, ["filter", tmp_corpus, "--tag", "cleartext"])
        assert result.exit_code == 0
        assert "Matched" in result.output

    def test_cluster(self, tmp_corpus, tmp_path):
        out = str(tmp_path / "clustered.jsonl")
        result = self.runner.invoke(cli, ["cluster", tmp_corpus, "-o", out])
        assert result.exit_code == 0
        assert "Clustered" in result.output

    def test_report(self, tmp_corpus, tmp_path):
        report_path = str(tmp_path / "report.md")
        result = self.runner.invoke(cli, ["report", tmp_corpus, "-o", report_path])
        assert result.exit_code == 0
        assert os.path.exists(report_path)

    def test_export_jsonl(self, tmp_corpus, tmp_path):
        out = str(tmp_path / "export.jsonl")
        result = self.runner.invoke(cli, ["export", tmp_corpus, "--format", "jsonl", "-o", out])
        assert result.exit_code == 0
        assert "Exported" in result.output

    def test_export_csv(self, tmp_corpus, tmp_path):
        out = str(tmp_path / "export.csv")
        result = self.runner.invoke(cli, ["export", tmp_corpus, "--format", "csv", "-o", out])
        assert result.exit_code == 0
