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
        from job_scout.profile_loader import load_user_profile

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
        from job_scout.capability_model_loader import load_capability_model

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
