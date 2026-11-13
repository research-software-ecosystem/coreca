"""Проверки изоляции артефактов сообществ в реальном workflow фильтрации."""

import unittest
from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/filter_curate_commu_resources.yml"
COMMUNITIES = ("biodiversity", "microbiome")


class TestCommunityArtifacts(unittest.TestCase):
    def setUp(self) -> None:
        self.jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]
        self.uploads = [
            step["with"]
            for job in self.jobs.values()
            for step in job.get("steps", [])
            if step.get("uses", "").startswith("actions/upload-artifact@")
        ]
        self.downloads = [
            step["with"]
            for step in self.jobs["merge-resources"]["steps"]
            if step.get("uses", "").startswith("actions/download-artifact@")
        ]

    @staticmethod
    def _render(value: str, community: str) -> str:
        return value.replace("${{ matrix.community }}", community)

    def test_every_source_has_a_matching_download(self) -> None:
        self.assertEqual(len(self.uploads), 3)
        self.assertCountEqual([item["name"] for item in self.uploads], [item["name"] for item in self.downloads])

    def test_artifact_names_do_not_collide_between_communities(self) -> None:
        names = [self._render(item["name"], community) for item in self.uploads for community in COMMUNITIES]
        self.assertEqual(len(names), len(set(names)), "Артефакты разных сообществ не должны иметь одинаковые имена")

    def test_download_selects_only_the_requested_community(self) -> None:
        artifacts = [
            {
                "name": self._render(item["name"], community),
                "community": community,
                "directory": Path(self._render(item["path"], community)).parent,
            }
            for item in self.uploads
            for community in COMMUNITIES
        ]
        for download in self.downloads:
            for community in COMMUNITIES:
                with self.subTest(source=download["name"], community=community):
                    requested = self._render(download["name"], community)
                    matches = [item for item in artifacts if item["name"] == requested]
                    self.assertEqual(len(matches), 1, "Выбор по имени должен однозначно определять артефакт")
                    self.assertEqual(matches[0]["community"], community)
                    destination = Path(self._render(download["path"], community))
                    self.assertEqual(destination.parts[:2], ("communities", community))
                    self.assertEqual(matches[0]["directory"], destination)


if __name__ == "__main__":
    unittest.main()
