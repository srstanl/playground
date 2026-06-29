from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import unittest

from job_scout import cli


class JobScoutCliTests(unittest.TestCase):
    def test_parser_exists(self) -> None:
        self.assertIsNotNone(cli.build_parser())

    def test_list_empty_database(self) -> None:
        temp_dir = Path(self.id().replace(".", "_"))
        temp_dir.mkdir(exist_ok=True)
        database_path = temp_dir / "job_scout.db"
        original_database_path = cli._database_path
        cli._database_path = lambda: database_path
        try:
            output = StringIO()
            with redirect_stdout(output):
                exit_code = cli.run(["list"])
        finally:
            cli._database_path = original_database_path
            if database_path.exists():
                database_path.unlink()
            temp_dir.rmdir()

        self.assertEqual(exit_code, 0)
        self.assertIn("No jobs ingested yet.", output.getvalue())

    def test_ingest_list_and_show(self) -> None:
        temp_dir = Path(self.id().replace(".", "_"))
        temp_dir.mkdir(exist_ok=True)
        database_path = temp_dir / "job_scout.db"
        job_file = temp_dir / "job.txt"
        job_file.write_text("Senior platform engineering role focused on CI/CD.", encoding="utf-8")

        original_database_path = cli._database_path
        cli._database_path = lambda: database_path
        try:
            ingest_output = StringIO()
            with redirect_stdout(ingest_output):
                ingest_exit = cli.run(
                    [
                        "ingest",
                        "--file",
                        str(job_file),
                        "--source-system",
                        "linkedin",
                        "--company",
                        "Example Co",
                        "--title",
                        "Senior Platform Engineer",
                        "--location",
                        "Remote",
                    ]
                )
            list_output = StringIO()
            with redirect_stdout(list_output):
                list_exit = cli.run(["list"])
            show_output = StringIO()
            with redirect_stdout(show_output):
                show_exit = cli.run(["show", "1"])
        finally:
            cli._database_path = original_database_path
            if database_path.exists():
                database_path.unlink()
            if job_file.exists():
                job_file.unlink()
            temp_dir.rmdir()

        self.assertEqual(ingest_exit, 0)
        self.assertIn("Ingested job 1", ingest_output.getvalue())
        self.assertEqual(list_exit, 0)
        self.assertIn("Senior Platform Engineer", list_output.getvalue())
        self.assertIn("Example Co", list_output.getvalue())
        self.assertEqual(show_exit, 0)
        self.assertIn("source_system: linkedin", show_output.getvalue())
        self.assertIn("Senior platform engineering role focused on CI/CD.", show_output.getvalue())

    def test_ingest_batch_jsonl(self) -> None:
        temp_dir = Path(self.id().replace(".", "_"))
        temp_dir.mkdir(exist_ok=True)
        database_path = temp_dir / "job_scout.db"
        batch_file = temp_dir / "jobs.jsonl"
        batch_file.write_text(
            "\n".join(
                [
                    '{"source_system":"linkedin","title":"Platform Engineer","company":"Example Co","raw_description":"Platform JD text"}',
                    '{"source_system":"indeed","title":"Senior DevOps Engineer","unknown_field":"ignored","raw_description":"DevOps JD text"}',
                    '{"source_system":"linkedin","title":"Broken Posting"}',
                ]
            ),
            encoding="utf-8",
        )

        original_database_path = cli._database_path
        cli._database_path = lambda: database_path
        try:
            batch_output = StringIO()
            with redirect_stdout(batch_output):
                batch_exit = cli.run(["ingest-batch", "--jsonl", str(batch_file)])
            list_output = StringIO()
            with redirect_stdout(list_output):
                list_exit = cli.run(["list"])
        finally:
            cli._database_path = original_database_path
            if database_path.exists():
                database_path.unlink()
            if batch_file.exists():
                batch_file.unlink()
            temp_dir.rmdir()

        self.assertEqual(batch_exit, 0)
        self.assertIn("line 1: ingested job 1", batch_output.getvalue())
        self.assertIn("line 2: warning: ignoring unknown fields: unknown_field", batch_output.getvalue())
        self.assertIn("line 2: ingested job 2", batch_output.getvalue())
        self.assertIn("line 3: error: raw_description is required", batch_output.getvalue())
        self.assertIn("summary: processed=3 ingested=2 failed=1 warnings=1", batch_output.getvalue())
        self.assertEqual(list_exit, 0)
        self.assertIn("Senior DevOps Engineer", list_output.getvalue())
        self.assertIn("Platform Engineer", list_output.getvalue())

    def test_evaluate_job(self) -> None:
        temp_dir = Path(self.id().replace(".", "_"))
        temp_dir.mkdir(exist_ok=True)
        database_path = temp_dir / "job_scout.db"
        job_file = temp_dir / "job.txt"
        job_file.write_text(
            "\n".join(
                [
                    "Senior Platform Engineer",
                    "Remote role building cloud platforms with Python, Kubernetes, Docker, Terraform, and AWS.",
                    "Responsibilities:",
                    "- Build CI/CD pipelines",
                    "- Maintain APIs and platform tooling",
                    "Preferred: React experience is a plus.",
                    "Compensation: $150,000 - $180,000 per year.",
                ]
            ),
            encoding="utf-8",
        )

        original_database_path = cli._database_path
        cli._database_path = lambda: database_path
        try:
            with redirect_stdout(StringIO()):
                ingest_exit = cli.run(
                    [
                        "ingest",
                        "--file",
                        str(job_file),
                        "--source-system",
                        "linkedin",
                        "--title",
                        "Senior Platform Engineer",
                        "--location",
                        "Remote",
                    ]
                )
            evaluate_output = StringIO()
            with redirect_stdout(evaluate_output):
                evaluate_exit = cli.run(["evaluate", "1"])
            json_output = StringIO()
            with redirect_stdout(json_output):
                json_exit = cli.run(["evaluate", "1", "--json"])
        finally:
            cli._database_path = original_database_path
            if database_path.exists():
                database_path.unlink()
            if job_file.exists():
                job_file.unlink()
            temp_dir.rmdir()

        self.assertEqual(ingest_exit, 0)
        self.assertEqual(evaluate_exit, 0)
        self.assertIn("recommendation:", evaluate_output.getvalue())
        self.assertIn("overall_score:", evaluate_output.getvalue())
        self.assertIn("narrative:", evaluate_output.getvalue())
        self.assertIn("semantic_shapes:", evaluate_output.getvalue())
        self.assertIn("- problem_shape_alignment:", evaluate_output.getvalue())
        self.assertIn("- role_scope_alignment:", evaluate_output.getvalue())
        self.assertIn("- environment_alignment:", evaluate_output.getvalue())
        self.assertEqual(json_exit, 0)
        self.assertIn('"contract_version": "v1"', json_output.getvalue())
        self.assertIn('"job_posting_id": 1', json_output.getvalue())
        self.assertIn('"semantic_shapes"', json_output.getvalue())

    def test_track_init_show_update_and_list(self) -> None:
        temp_dir = Path(self.id().replace(".", "_"))
        temp_dir.mkdir(exist_ok=True)
        database_path = temp_dir / "job_scout.db"
        job_file = temp_dir / "job.txt"
        job_file.write_text("Platform role with delivery systems work.", encoding="utf-8")

        original_database_path = cli._database_path
        cli._database_path = lambda: database_path
        try:
            with redirect_stdout(StringIO()):
                ingest_exit = cli.run(
                    [
                        "ingest",
                        "--file",
                        str(job_file),
                        "--source-system",
                        "linkedin",
                        "--title",
                        "Platform Engineer",
                    ]
                )
            init_output = StringIO()
            with redirect_stdout(init_output):
                init_exit = cli.run(
                    [
                        "track",
                        "init",
                        "1",
                        "--decision",
                        "apply",
                        "--status",
                        "application_ready",
                        "--next-follow-up-at",
                        "2026-07-01T09:00:00+00:00",
                    ]
                )
            show_output = StringIO()
            with redirect_stdout(show_output):
                show_exit = cli.run(["track", "show", "1"])
            update_output = StringIO()
            with redirect_stdout(update_output):
                update_exit = cli.run(
                    [
                        "track",
                        "update",
                        "1",
                        "--status",
                        "applied",
                        "--outcome",
                        "unknown",
                        "--notes",
                        "Applied through company portal.",
                    ]
                )
            list_output = StringIO()
            with redirect_stdout(list_output):
                list_exit = cli.run(["track", "list", "--status", "applied"])
        finally:
            cli._database_path = original_database_path
            if database_path.exists():
                database_path.unlink()
            if job_file.exists():
                job_file.unlink()
            temp_dir.rmdir()

        self.assertEqual(ingest_exit, 0)
        self.assertEqual(init_exit, 0)
        self.assertIn("Tracking initialized for job 1", init_output.getvalue())
        self.assertEqual(show_exit, 0)
        self.assertIn("decision: apply", show_output.getvalue())
        self.assertIn("status: application_ready", show_output.getvalue())
        self.assertEqual(update_exit, 0)
        self.assertIn("Tracking updated for job 1.", update_output.getvalue())
        self.assertEqual(list_exit, 0)
        self.assertIn("[1] apply | applied | unknown", list_output.getvalue())

    def test_track_init_rejects_duplicate_record(self) -> None:
        temp_dir = Path(self.id().replace(".", "_"))
        temp_dir.mkdir(exist_ok=True)
        database_path = temp_dir / "job_scout.db"
        job_file = temp_dir / "job.txt"
        job_file.write_text("Platform role.", encoding="utf-8")

        original_database_path = cli._database_path
        cli._database_path = lambda: database_path
        try:
            with redirect_stdout(StringIO()):
                cli.run(["ingest", "--file", str(job_file), "--title", "Platform Engineer"])
                cli.run(["track", "init", "1", "--decision", "saved", "--status", "not_started"])
            with self.assertRaises(SystemExit) as error:
                cli.run(["track", "init", "1", "--decision", "saved", "--status", "not_started"])
        finally:
            cli._database_path = original_database_path
            if database_path.exists():
                database_path.unlink()
            if job_file.exists():
                job_file.unlink()
            temp_dir.rmdir()

        self.assertIn("already exists", str(error.exception))

    def test_track_update_terminal_outcome_closes_record(self) -> None:
        temp_dir = Path(self.id().replace(".", "_"))
        temp_dir.mkdir(exist_ok=True)
        database_path = temp_dir / "job_scout.db"
        job_file = temp_dir / "job.txt"
        job_file.write_text("Platform role.", encoding="utf-8")

        original_database_path = cli._database_path
        cli._database_path = lambda: database_path
        try:
            with redirect_stdout(StringIO()):
                cli.run(["ingest", "--file", str(job_file), "--title", "Platform Engineer"])
                cli.run(
                    [
                        "track",
                        "init",
                        "1",
                        "--decision",
                        "apply",
                        "--status",
                        "applied",
                        "--next-follow-up-at",
                        "2026-07-03T09:00:00+00:00",
                    ]
                )
                cli.run(["track", "update", "1", "--outcome", "position_closed"])
            show_output = StringIO()
            with redirect_stdout(show_output):
                show_exit = cli.run(["track", "show", "1"])
        finally:
            cli._database_path = original_database_path
            if database_path.exists():
                database_path.unlink()
            if job_file.exists():
                job_file.unlink()
            temp_dir.rmdir()

        self.assertEqual(show_exit, 0)
        self.assertIn("status: closed", show_output.getvalue())
        self.assertIn("outcome: position_closed", show_output.getvalue())
        self.assertIn("next_follow_up_at: ", show_output.getvalue())

    def test_track_update_rejects_invalid_follow_up_for_terminal_outcome(self) -> None:
        temp_dir = Path(self.id().replace(".", "_"))
        temp_dir.mkdir(exist_ok=True)
        database_path = temp_dir / "job_scout.db"
        job_file = temp_dir / "job.txt"
        job_file.write_text("Platform role.", encoding="utf-8")

        original_database_path = cli._database_path
        cli._database_path = lambda: database_path
        try:
            with redirect_stdout(StringIO()):
                cli.run(["ingest", "--file", str(job_file), "--title", "Platform Engineer"])
            with self.assertRaises(SystemExit) as error:
                cli.run(
                    [
                        "track",
                        "init",
                        "1",
                        "--decision",
                        "saved",
                        "--status",
                        "not_started",
                        "--outcome",
                        "position_closed",
                        "--next-follow-up-at",
                        "2026-07-03T09:00:00+00:00",
                    ]
                )
        finally:
            cli._database_path = original_database_path
            if database_path.exists():
                database_path.unlink()
            if job_file.exists():
                job_file.unlink()
            temp_dir.rmdir()

        self.assertIn("terminal outcomes cannot keep an active follow-up date", str(error.exception))


class EvaluationModelTests(unittest.TestCase):
    def test_job_evaluation_defaults(self) -> None:
        from job_scout.models import EvaluationSummary, JobEvaluation

        evaluation = JobEvaluation(
            job_posting_id=7,
            summary=EvaluationSummary(
                headline="Strong backend fit",
                recommendation="consider",
                overall_score=78,
                confidence_score=64,
            ),
        )

        self.assertEqual(evaluation.contract_version, "v1")
        self.assertEqual(evaluation.job_posting_id, 7)
        self.assertEqual(evaluation.summary.recommendation, "consider")
        self.assertEqual(evaluation.extraction.role_title_normalized, "unknown")
        self.assertEqual(evaluation.scoring.dimensions, [])
        self.assertIsNone(evaluation.provenance)


class UserProfileLoaderTests(unittest.TestCase):
    def test_load_user_profile_example(self) -> None:
        from job_scout.loaders.profile import load_user_profile

        profile = load_user_profile(
            Path("/Users/srstanl/FAFO/playground/job_scout/profiles/user_profile.example.json")
        )

        self.assertEqual(profile.profile_version, "v2")
        self.assertEqual(profile.identity.headline, "Senior Platform & Software Engineer")
        self.assertIn("Platform Engineering", profile.problem_spaces.primary)
        self.assertIn("Platform Engineer", profile.targeting.target_roles)
        self.assertIn("Python", profile.skills.languages)
        self.assertEqual(profile.preferences.compensation.currency, "USD")
        self.assertIn("problem_shape", profile.evaluation_preferences.weights)
        self.assertTrue(profile.artifact_preferences.generate_pdf)


class CapabilityModelLoaderTests(unittest.TestCase):
    def test_load_capability_model(self) -> None:
        from job_scout.loaders.capability import load_capability_model

        model = load_capability_model(
            Path("/Users/srstanl/FAFO/playground/job_scout/profiles/capability_model.json")
        )

        self.assertEqual(model.model_version, "v1")
        capability_names = [capability.name for capability in model.capabilities]
        self.assertIn("continuous_delivery", capability_names)
        self.assertIn("observability", capability_names)
        self.assertTrue(any("terraform" in capability.tools for capability in model.capabilities))


if __name__ == "__main__":
    unittest.main()
