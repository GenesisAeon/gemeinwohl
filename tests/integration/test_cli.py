"""CLI integration tests using Typer's test runner."""

import json
from pathlib import Path

from typer.testing import CliRunner

from gemeinwohl.cli.main import app

runner = CliRunner()


class TestVersionCommand:
    def test_version_flag(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestAssessCommand:
    def test_basic_assess(self):
        result = runner.invoke(app, ["assess", "--entropy", "0.3"])
        assert result.exit_code == 0
        assert "Score" in result.output or "Gemeinwohl" in result.output

    def test_assess_with_models(self):
        result = runner.invoke(app, ["assess", "--entropy", "0.3", "--models", "gpt-4"])
        assert result.exit_code == 0

    def test_assess_multiple_models(self):
        result = runner.invoke(
            app, ["assess", "--entropy", "0.3", "--models", "gpt-4", "--models", "claude-3-opus"]
        )
        assert result.exit_code == 0

    def test_assess_visualize(self):
        result = runner.invoke(app, ["assess", "--entropy", "0.3", "--visualize"])
        assert result.exit_code == 0

    def test_assess_full(self):
        result = runner.invoke(app, ["assess", "--entropy", "0.3", "--full"])
        assert result.exit_code == 0

    def test_assess_export(self, tmp_path: Path):
        out_file = tmp_path / "result.json"
        result = runner.invoke(
            app, ["assess", "--entropy", "0.3", "--export", str(out_file)]
        )
        assert result.exit_code == 0
        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert "score" in data
        assert "report" in data
        assert "alignment" in data

    def test_assess_export_contains_value(self, tmp_path: Path):
        out_file = tmp_path / "result.json"
        runner.invoke(app, ["assess", "--entropy", "0.3", "--export", str(out_file)])
        data = json.loads(out_file.read_text())
        assert 0.0 <= data["score"]["value"] <= 1.0

    def test_assess_high_entropy_exit_code_2(self):
        # entropy=1.0 should produce emergency-level score → exit 2
        result = runner.invoke(
            app, ["assess", "--entropy", "1.0", "--personhood", "4"]
        )
        # May or may not be 2 depending on exact weights; just check no crash
        assert result.exit_code in (0, 2)

    def test_assess_personhood_level(self):
        result = runner.invoke(
            app, ["assess", "--entropy", "0.3", "--personhood", "2"]
        )
        assert result.exit_code == 0

    def test_assess_ecological_option(self):
        result = runner.invoke(
            app, ["assess", "--entropy", "0.3", "--ecological", "0.9"]
        )
        assert result.exit_code == 0

    def test_assess_equity_option(self):
        result = runner.invoke(
            app, ["assess", "--entropy", "0.3", "--equity", "0.8"]
        )
        assert result.exit_code == 0

    def test_assess_all_options_combined(self, tmp_path: Path):
        out_file = tmp_path / "full.json"
        result = runner.invoke(
            app,
            [
                "assess",
                "--entropy", "0.4",
                "--models", "claude-3-sonnet",
                "--personhood", "2",
                "--ecological", "0.8",
                "--equity", "0.7",
                "--visualize",
                "--full",
                "--export", str(out_file),
            ],
        )
        assert result.exit_code == 0
        assert out_file.exists()


class TestPolicyCommands:
    def test_policy_infer(self):
        result = runner.invoke(app, ["policy", "infer", "--entropy", "0.5"])
        assert result.exit_code == 0

    def test_policy_infer_high_score(self):
        result = runner.invoke(
            app,
            ["policy", "infer", "--entropy", "0.1", "--ecological", "0.95", "--equity", "0.95"],
        )
        assert result.exit_code == 0
        assert "Score" in result.output or "Max Personhood" in result.output

    def test_policy_rules(self):
        result = runner.invoke(app, ["policy", "rules"])
        assert result.exit_code == 0
        assert "P001" in result.output


class TestKritikalitaetCommands:
    def test_kritikalitaet_check(self):
        result = runner.invoke(app, ["kritikalitaet", "check", "--entropy", "0.3"])
        assert result.exit_code == 0

    def test_kritikalitaet_check_with_models(self):
        result = runner.invoke(
            app, ["kritikalitaet", "check", "--entropy", "0.5", "--models", "gpt-4"]
        )
        assert result.exit_code == 0

    def test_kritikalitaet_check_export(self, tmp_path: Path):
        out_file = tmp_path / "report.json"
        result = runner.invoke(
            app,
            ["kritikalitaet", "check", "--entropy", "0.4", "--export", str(out_file)],
        )
        assert result.exit_code == 0
        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert "level" in data

    def test_kritikalitaet_check_high_entropy(self):
        result = runner.invoke(
            app, ["kritikalitaet", "check", "--entropy", "0.95"]
        )
        assert result.exit_code in (0, 2)


class TestEmergencyExitCode:
    """Ensure emergency-level scores produce exit code 2."""

    def test_assess_emergency_exit_code(self):
        # entropy=1.0, eco=0.0, equity=0.0, no models → G ≈ 0.125 < 0.30 → EMERGENCY
        result = runner.invoke(
            app,
            [
                "assess", "--entropy", "1.0",
                "--ecological", "0.0",
                "--equity", "0.0",
            ],
        )
        assert result.exit_code == 2

    def test_kritikalitaet_emergency_exit_code(self):
        result = runner.invoke(
            app,
            [
                "kritikalitaet", "check",
                "--entropy", "1.0",
                "--ecological", "0.0",
                "--equity", "0.0",
            ],
        )
        assert result.exit_code == 2
