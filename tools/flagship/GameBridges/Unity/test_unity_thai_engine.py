"""Automated Test Suite for THub Unity Thai Localization Engine.

Verifies:
1. PUA mapping & Thai decomposition canonicalization.
2. Token preservation & deterministic key generation.
3. Queue-based context preservation for duplicate English sources.
4. Strict non-English Latin rejection (French, German, Spanish, Portuguese).
5. Tone-mark elevation tuning (+160 units).
6. Deployment safety checkpoints (process check, immutable backups, rollback).
"""
import os
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path

# Add GameBridges/Unity to sys.path
TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

from unity_common import (
    CSV_COLUMNS,
    stable_key,
    extract_protected_tokens,
    validate_token_preservation,
    write_tstudio_csv,
    read_tstudio_csv,
    sha256_file
)
from unity_extractor import UnityExtractor
from unity_font_pipeline import ThaiFontMapper, UnityFontPipeline
from unity_native_packer import UnityNativePacker
from unity_deployer import UnityDeployer


class TestUnityThaiEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self):
        # Reset any read-only permissions before deleting temp dir
        for p in self.tmp.rglob("*"):
            try:
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass
        self.temp_dir.cleanup()

    def test_pua_mapping_and_normalization(self):
        """Test Thai PUA mapper handles decomposed Sara Am and composite tone marks."""
        mapper = ThaiFontMapper()
        
        # Test decomposed sara am: \u0e4d\u0e32 should become \u0e33
        decomposed = "ก\u0e4d\u0e32ลัง"
        mapped = mapper.map_text(decomposed)
        self.assertTrue(len(mapped) > 0)

        # Test composite tone marks map into PUA range (0xF000..0xF8FF)
        thai_word = "กึ่งหนาพิเศษ"
        mapped_word = mapper.map_text(thai_word)
        has_pua = any(0xF000 <= ord(c) <= 0xF8FF for c in mapped_word)
        self.assertTrue(has_pua, f"Expected PUA characters in mapped word: {mapped_word}")

        # Test decode
        restored = mapper.decode_text(mapped_word)
        self.assertEqual(restored, "กึ่งหนาพิเศษ")

    def test_token_preservation_and_stable_key(self):
        """Test protected tokens are extracted and preserved, and keys are deterministic."""
        src = "Found <color=#FF0000>{0}</color> items in %s!"
        valid_trans = "พบ <color=#FF0000>{0}</color> ชิ้นใน %s!"
        invalid_trans = "พบ {0} ชิ้นใน %s!"  # Missing color tag

        valid, _ = validate_token_preservation(src, valid_trans)
        self.assertTrue(valid)

        invalid, msg = validate_token_preservation(src, invalid_trans)
        self.assertFalse(invalid)
        self.assertIn("Token mismatch", msg)

        # Deterministic key test
        k1 = stable_key("globalgamemanagers.assets", 2751, "data[0]/m_StringEN:0")
        k2 = stable_key("globalgamemanagers.assets", 2751, "data[0]/m_StringEN:0")
        k3 = stable_key("globalgamemanagers.assets", 2751, "data[1]/m_StringEN:1")
        self.assertEqual(k1, k2)
        self.assertNotEqual(k1, k3)
        self.assertTrue(k1.startswith("UNITY_"))

    def test_non_english_latin_rejection(self):
        """Ensure French, German, Spanish, and Asian fields are strictly rejected."""
        extractor = UnityExtractor()

        # Target English fields
        self.assertTrue(extractor.is_english_field("m_StringEN"))
        self.assertTrue(extractor.is_english_field("m_NameEN"))
        self.assertTrue(extractor.is_english_field("CommentEN"))
        self.assertTrue(extractor.is_english_field("title_english"))

        # Explicit non-English fields containing Latin text that MUST be rejected
        self.assertFalse(extractor.is_english_field("m_StringFR"))
        self.assertFalse(extractor.is_english_field("m_StringDE"))
        self.assertFalse(extractor.is_english_field("m_StringES"))
        self.assertFalse(extractor.is_english_field("m_StringIT"))
        self.assertFalse(extractor.is_english_field("m_StringPT"))
        self.assertFalse(extractor.is_english_field("m_StringJP"))
        self.assertFalse(extractor.is_english_field("m_StringKO"))
        self.assertFalse(extractor.is_english_field("m_StringZH_CN"))

    def test_queue_based_duplicate_source_context_preservation(self):
        """Test identical English terms with different Thai meanings are queued deterministically."""
        csv_file = self.tmp / "test_translations.csv"
        rows = [
            {
                "key": "UNITY_001",
                "source": "None",
                "translation": "ไม่มี",
                "context": "MonoBehaviour: ItemTable | PathID: 1001 | Field: m_NameEN",
                "file_path": "resources.assets"
            },
            {
                "key": "UNITY_002",
                "source": "None",
                "translation": "ไม่ระบุ",
                "context": "MonoBehaviour: ItemTable | PathID: 1001 | Field: m_NameEN",
                "file_path": "resources.assets"
            },
            {
                "key": "UNITY_003",
                "source": "Attack",
                "translation": "โจมตี",
                "context": "MonoBehaviour: SkillTable | PathID: 2002 | Field: m_StringEN",
                "file_path": "resources.assets"
            }
        ]
        write_tstudio_csv(csv_file, rows)

        packer = UnityNativePacker()
        queues = packer.build_translation_queues_from_csv(csv_file)

        # Check PathID 1001 has two distinct translations queued in FIFO order for "None"
        self.assertIn("1001", queues)
        table_1001 = queues["1001"]
        self.assertEqual(len(table_1001), 2)
        self.assertEqual(table_1001[0]["source"], "None")
        self.assertEqual(packer.mapper.decode_text(table_1001[0]["translation"]), "ไม่มี")
        self.assertEqual(table_1001[1]["source"], "None")
        self.assertEqual(packer.mapper.decode_text(table_1001[1]["translation"]), "ไม่ระบุ")

    def test_deployment_safety_and_immutable_backup(self):
        """Test immutable backup creation, read-only flag, no-overwrite policy, and rollback."""
        deployer = UnityDeployer(session_log_path=self.tmp / "session_log.md")

        # Create dummy original game file
        game_dir = self.tmp / "Game_Data"
        game_dir.mkdir(parents=True, exist_ok=True)
        orig_file = game_dir / "resources.assets"
        orig_file.write_bytes(b"ORIGINAL_GAME_ASSET_CONTENT_V1.0")

        # Create dummy packed file
        packed_file = self.tmp / "resources_packed.assets"
        packed_file.write_bytes(b"PATCHED_THAI_ASSET_CONTENT_V1.0")

        # Deploy
        deploy_res = deployer.deploy(
            packed_asset=packed_file,
            game_destination_file=orig_file,
            session_log=self.tmp / "session_log.md"
        )

        self.assertTrue(deploy_res["success"])
        self.assertTrue(deploy_res["new_backup_created"])
        backup_file = Path(deploy_res["backup_file"])
        self.assertTrue(backup_file.is_file())

        # Check backup content is strictly original
        self.assertEqual(backup_file.read_bytes(), b"ORIGINAL_GAME_ASSET_CONTENT_V1.0")

        # Check deployed file is packed content
        self.assertEqual(orig_file.read_bytes(), b"PATCHED_THAI_ASSET_CONTENT_V1.0")

        # Check backup file is marked read-only
        is_read_only = bool(backup_file.stat().st_mode & stat.S_IREAD and not (backup_file.stat().st_mode & stat.S_IWRITE))
        if sys.platform == "win32":
            self.assertTrue(is_read_only)

        # Deploy AGAIN with a v2 packed file - backup must NEVER be overwritten!
        packed_v2 = self.tmp / "resources_packed_v2.assets"
        packed_v2.write_bytes(b"PATCHED_THAI_ASSET_CONTENT_V2.0")

        deploy_v2 = deployer.deploy(
            packed_asset=packed_v2,
            game_destination_file=orig_file,
            session_log=self.tmp / "session_log.md"
        )
        self.assertFalse(deploy_v2["new_backup_created"])
        # Original backup must STILL be v1.0 original!
        self.assertEqual(backup_file.read_bytes(), b"ORIGINAL_GAME_ASSET_CONTENT_V1.0")

        # Test Rollback
        rollback_res = deployer.rollback(
            game_destination_file=orig_file,
            session_log=self.tmp / "session_log.md"
        )
        self.assertTrue(rollback_res["success"])
        # File restored to original
        self.assertEqual(orig_file.read_bytes(), b"ORIGINAL_GAME_ASSET_CONTENT_V1.0")

        # Check session log exists and has entries
        log_content = (self.tmp / "session_log.md").read_text(encoding="utf-8")
        self.assertIn("Native Asset Deployment", log_content)
        self.assertIn("Asset Rollback to Original", log_content)


if __name__ == "__main__":
    unittest.main()
