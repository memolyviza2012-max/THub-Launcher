# -*- coding: utf-8 -*-
"""
tstudio_analyzer.py
===================
Whole-File Game Localization Intelligence & Deep Analysis Engine.
Analyzes full game localization files across 6 critical dimensions:
1. Holistic Game Matrix & Content Breakdown
2. Cast Discovery & Dramatis Personae (Character line counts & voice)
3. Quests & Tactical Operations Dossier (Missions, Objectives, Lore & Walkthrough Search)
4. Semantic Asset Bundling (GAS Abilities, Items, Multi-part Assets)
5. Automated Entity & Glossary Miner (Proper Nouns & Keywords)
6. File-Wide Consistency, Conflict & Tag Integrity Auditor
"""

import re
import math
import time
import urllib.parse
from collections import Counter, defaultdict
from tstudio_core import TStudioCore

# Regex patterns for placeholder variables and tags
RE_TAGS = re.compile(
    r'\{[0-9a-zA-Z_\.\,\:\s\|]+\}|'   # {0}, {HeroGender}|gender(...), {name}
    r'%[0-9\.\-+ #]*[sdfxX]|'          # %s, %d, %.2f
    r'<[^>]+>|'                         # <color=#ff0000>, </color>, <b>
    r'\[\/?[a-zA-Z0-9_=#]+\]|'         # [b], [/b], [color=...]
    r'\\n|\\r|\\t'                     # explicit escaped line breaks
)

RE_PROPER_NOUNS = re.compile(r'\b[A-Z][a-zA-Z0-9\'-]*(?:\s+[A-Z][a-zA-Z0-9\'-]*){1,3}\b')
RE_SPEAKER_DIALOGUE = re.compile(r'^\[([A-Z][a-zA-Z0-9\s\.\-_]+)\][:\s]|^([A-Z][a-zA-Z0-9\s\.\-_]{1,20}):\s')

# English Stopwords to filter out of Entity Mining
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
    'by', 'from', 'up', 'about', 'into', 'over', 'after', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'this', 'that', 'these',
    'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her',
    'its', 'our', 'their', 'what', 'which', 'who', 'whom', 'whose', 'when', 'where',
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
    'just', 'don', 't', 's', 'm', 're', 've', 'll', 'd',
    # Common game UI noise
    'press', 'select', 'cancel', 'confirm', 'back', 'next', 'continue', 'loading',
    'apply', 'default', 'options', 'settings', 'quit', 'exit', 'resume', 'pause',
    'level', 'rank', 'stage', 'chapter', 'objective', 'mission', 'quest',
    'you can', 'if you', 'are you', 'do you', 'to the', 'in the', 'of the',
    'for the', 'with the', 'at the', 'on the', 'from the', 'this is', 'that is'
}

# Non-character speaker noise to prevent UI/mission headers from polluting Cast List
NOISE_SPEAKER_PREFIXES = {
    'launch operation', 'launch mission', 'mission', 'operation', 'objective',
    'primary objective', 'secondary objective', 'warning', 'notice', 'caution',
    'hint', 'tip', 'note', 'memo', 'target', 'requirement', 'reward', 'condition',
    'appearance', 'outfit', 'costume', 'unlocked', 'info', 'guide', 'press', 'action',
    'select', 'confirm', 'cancel', 'back', 'next', 'previous'
}


class LocalizationAnalyzer:
    """
    State-of-the-Art Whole-File Analyzer for Video Game Localization.
    """

    @classmethod
    def analyze(cls, data, glossary=None, project_name="Game Project"):
        """
        Runs comprehensive full-file analysis on data.
        data: list of dicts with keys 'id', 'source', 'trans', 'tag'
        glossary: dict of {term: [trans, tag]} or {term: trans}
        Returns AnalysisReport dictionary.
        """
        t_start = time.time()
        if not data:
            return cls._empty_report(project_name)

        if glossary is None:
            glossary = {}

        # Normalized glossary lookup
        glossary_lookup = {}
        for k, v in glossary.items():
            norm_k = str(k).strip().lower()
            if isinstance(v, (list, tuple)) and v:
                glossary_lookup[norm_k] = str(v[0]).strip()
            elif isinstance(v, str):
                glossary_lookup[norm_k] = v.strip()

        total_rows = len(data)
        total_words = 0
        total_chars = 0
        translated_rows = 0
        untranslated_rows = 0

        # Category Counters
        category_counts = Counter()
        category_trans_counts = Counter()

        # 1. Cast & Speakers
        speaker_mentions = Counter()
        speaker_sample_rows = {}
        character_names = {}  # en_name -> trans_name

        # 2. Bundles
        raw_bundles = defaultdict(dict)
        re_bundle_suffix = re.compile(r'^(.*?)_(Name|Desc|Description|Tooltip|Summary|Objective|Title|Detail|Info)$', re.I)

        # 2.5 Quests & Tactical Operations Dossier
        raw_quests = defaultdict(lambda: {
            "type": "Quest", "title_en": "", "title_th": "", "root_id": "", "first_row": 0, "rows": [], "done_count": 0
        })

        # 3. Entity Mining
        proper_nouns_counter = Counter()
        noun_sample_rows = {}

        # 4. Consistency & Conflicts
        source_translations = defaultdict(lambda: defaultdict(list))  # clean_src -> {clean_trans: [indices]}
        tag_errors = []
        cjk_leaks = []
        eng_leftovers = []
        glossary_violations = []

        # Iterate through every single row
        for idx, item in enumerate(data):
            uid = str(item.get("id", "") or "")
            src = str(item.get("source", "") or "")
            trans = str(item.get("trans", "") or "")
            tag = str(item.get("tag", "") or "❓")

            clean_src = src.strip()
            clean_trans = trans.strip()
            src_lower = clean_src.lower()
            uid_lower = uid.lower()

            # Word and Char metrics
            words = clean_src.split()
            word_count = len(words)
            total_words += word_count
            total_chars += len(clean_src)

            # Translation status
            is_trans = bool(clean_trans)
            if is_trans:
                translated_rows += 1
            else:
                untranslated_rows += 1

            # Category categorization
            cat_name = "Unclassified"
            if "Talk" in tag: cat_name = "Dialogues"
            elif "Skill" in tag: cat_name = "Skills"
            elif "Item" in tag: cat_name = "Items"
            elif "Quest" in tag: cat_name = "Quests"
            elif "Char" in tag: cat_name = "Characters"
            elif "Loc" in tag: cat_name = "Locations"
            elif "Sys" in tag: cat_name = "System"

            category_counts[cat_name] += 1
            if is_trans:
                category_trans_counts[cat_name] += 1

            # ----------------------------------------------------
            # Pillar 1: Cast & Speaker Discovery
            # ----------------------------------------------------
            if cat_name == "Characters" and clean_src and len(clean_src) < 40:
                char_name_clean = clean_src.strip()
                if char_name_clean not in character_names:
                    character_names[char_name_clean] = clean_trans
                speaker_mentions[char_name_clean] += 1
                if char_name_clean not in speaker_sample_rows:
                    speaker_sample_rows[char_name_clean] = (idx, uid, clean_src, clean_trans)

            # Extract dialogue speaker prefix [Speaker]: text (Filter out noise prefixes)
            m_spk = RE_SPEAKER_DIALOGUE.match(clean_src)
            if m_spk:
                spk = (m_spk.group(1) or m_spk.group(2)).strip()
                spk_l = spk.lower()
                if (len(spk) > 1 and 
                    spk_l not in STOP_WORDS and 
                    spk_l not in NOISE_SPEAKER_PREFIXES and 
                    not spk_l.startswith(('launch ', 'press ', 'warning', 'hint', 'tip', 'note', 'objective', 'mission'))):
                    speaker_mentions[spk] += 1
                    if spk not in speaker_sample_rows:
                        speaker_sample_rows[spk] = (idx, uid, clean_src, clean_trans)

            # Also check UE / Unity ConsequenceDatabaseCharacterName_ / Speaker_ in UID
            if "charactername_" in uid_lower:
                extracted = re.sub(r'^.*charactername_', '', uid, flags=re.I).split('_')[0].strip().title()
                if len(extracted) > 1 and extracted.lower() not in NOISE_SPEAKER_PREFIXES:
                    speaker_mentions[extracted] += 1
                    if extracted not in speaker_sample_rows:
                        speaker_sample_rows[extracted] = (idx, uid, clean_src, clean_trans)

            # ----------------------------------------------------
            # Pillar 2: Semantic Asset Bundles
            # ----------------------------------------------------
            m_b = re_bundle_suffix.match(uid)
            if m_b:
                root_id = m_b.group(1)
                role = m_b.group(2).lower()
                if role in ["desc", "description"]: role = "description"
                if role in ["tooltip", "detail", "info"]: role = "tooltip"
                if role in ["name", "title"]: role = "name"
                raw_bundles[root_id][role] = {
                    "idx": idx,
                    "uid": uid,
                    "src": clean_src,
                    "trans": clean_trans,
                    "tag": tag
                }

            # ----------------------------------------------------
            # Pillar 2.5: Quest & Tactical Operations Dossier
            # ----------------------------------------------------
            if cat_name == "Quests" or tag == "📜 Quest" or "strategy_objective" in uid_lower or "crisis" in uid_lower or "ot_" in uid_lower:
                m_launch = re.match(r'^Launch\s+(?:Mission|Operation)(?:\s+for\s+([^:\n\r]+))?:\s*(?:<[^>]+>)?\s*(.*?)(?:<\/[^>]*>)?\s*$', clean_src, re.I | re.DOTALL)
                if m_launch:
                    comp = (m_launch.group(1) or '').strip()
                    title = re.sub(r'<[^>]+>', '', m_launch.group(2)).strip()
                    qtype = f"Companion ({comp})" if comp else "Main Mission"
                    th_title = re.sub(r'<[^>]+>', '', clean_trans).strip()
                    m_th = re.match(r'^(?:เริ่มปฏิบัติการ|เปิดภารกิจ)(?:\s*(?:ให้|สำหรับ)\s*[^:\n\r]+)?:\s*(?:<[^>]+>)?\s*(.*?)(?:<\/[^>]*>)?\s*$', th_title, re.I | re.DOTALL)
                    if m_th:
                        th_title = m_th.group(1).strip()
                    entry = raw_quests[uid]
                    entry["root_id"] = uid
                    if not entry["rows"]: entry["first_row"] = idx
                    entry["rows"].append(idx)
                    if is_trans: entry["done_count"] += 1
                    entry["title_en"] = title or clean_src
                    entry["title_th"] = th_title or clean_trans
                    entry["type"] = qtype

                elif 'crisis' in uid_lower and any(k in uid_lower for k in ['_title', '_name']):
                    title = re.sub(r'<[^>]+>', '', clean_src).strip()
                    entry = raw_quests[uid]
                    entry["root_id"] = uid
                    if not entry["rows"]: entry["first_row"] = idx
                    entry["rows"].append(idx)
                    if is_trans: entry["done_count"] += 1
                    entry["title_en"] = title
                    entry["title_th"] = re.sub(r'<[^>]+>', '', clean_trans).strip()
                    entry["type"] = "Crisis Operation"

                elif 'ot_' in uid_lower:
                    m_ot = re.search(r'ot_([a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*)', uid, re.I)
                    if m_ot:
                        ot_id = m_ot.group(0)
                        parts = ot_id.split('_')
                        rid = "_".join(parts[:-1]) if len(parts) > 2 else ot_id
                        entry = raw_quests[rid]
                        entry["root_id"] = rid
                        if not entry["rows"]: entry["first_row"] = idx
                        entry["rows"].append(idx)
                        if is_trans: entry["done_count"] += 1
                        if any(parts[-1].lower().startswith(x) for x in ['name', 'title', 'intro', 'header']):
                            entry["title_en"] = re.sub(r'<[^>]+>', '', clean_src).strip()
                            entry["title_th"] = re.sub(r'<[^>]+>', '', clean_trans).strip()
                            entry["type"] = "Tactical Operation"

                elif 'strategy_objective' in uid_lower and any(k in uid_lower for k in ['_name', '_title', 'primaryobjective', 'secondaryobjective']):
                    title = re.sub(r'<[^>]+>', '', clean_src).strip()
                    if title and not title.lower().startswith('launch '):
                        entry = raw_quests[uid]
                        entry["root_id"] = uid
                        if not entry["rows"]: entry["first_row"] = idx
                        entry["rows"].append(idx)
                        if is_trans: entry["done_count"] += 1
                        entry["title_en"] = title
                        entry["title_th"] = re.sub(r'<[^>]+>', '', clean_trans).strip()
                        entry["type"] = "Primary Objective" if "primary" in uid_lower else "Secondary Objective"

                elif any(k in uid_lower for k in ['quest', 'bounty', 'contract', 'campaign_']) and any(k in uid_lower for k in ['_name', '_title', 'title_', 'name_']):
                    title = re.sub(r'<[^>]+>', '', clean_src).strip()
                    if title and len(title) < 90:
                        entry = raw_quests[uid]
                        entry["root_id"] = uid
                        if not entry["rows"]: entry["first_row"] = idx
                        entry["rows"].append(idx)
                        if is_trans: entry["done_count"] += 1
                        entry["title_en"] = title
                        entry["title_th"] = re.sub(r'<[^>]+>', '', clean_trans).strip()
                        entry["type"] = "Quest / Bounty"

            # ----------------------------------------------------
            # Pillar 3: Entity & Proper Noun Mining
            # ----------------------------------------------------
            if 3 < len(clean_src) < 200:
                # Proper Nouns (e.g. "Jedi Council", "Death Star")
                matches = RE_PROPER_NOUNS.findall(clean_src)
                for pn in matches:
                    pn_clean = pn.strip()
                    pn_lower = pn_clean.lower()
                    if pn_lower not in STOP_WORDS and len(pn_clean) > 3:
                        # Avoid phrases starting with stop words
                        first_word = pn_clean.split()[0].lower()
                        if first_word not in STOP_WORDS:
                            proper_nouns_counter[pn_clean] += 1
                            if pn_clean not in noun_sample_rows:
                                noun_sample_rows[pn_clean] = (idx, uid, clean_src, clean_trans)

            # ----------------------------------------------------
            # Pillar 4: Consistency & Integrity Auditor
            # ----------------------------------------------------
            # A. 1-to-Many Conflict Detector (Significant phrases: 3-120 chars)
            if 3 <= len(clean_src) <= 120 and clean_trans:
                source_translations[clean_src][clean_trans].append(idx)

            # B. Tag & Variable Guardian
            if is_trans:
                src_tags = sorted(RE_TAGS.findall(clean_src))
                trans_tags = sorted(RE_TAGS.findall(clean_trans))
                if src_tags != trans_tags:
                    missing = [t for t in src_tags if t not in trans_tags]
                    extra = [t for t in trans_tags if t not in src_tags]
                    if missing or extra:
                        tag_errors.append({
                            "idx": idx,
                            "uid": uid,
                            "src": clean_src,
                            "trans": clean_trans,
                            "missing": missing,
                            "extra": extra
                        })

            # C. CJK Leak Auditor
            if is_trans and TStudioCore.has_cjk(clean_trans):
                cjk_leaks.append({
                    "idx": idx,
                    "uid": uid,
                    "src": clean_src,
                    "trans": clean_trans,
                    "cjk_chars": "".join(TStudioCore.extract_cjk(clean_trans))
                })

            # D. English Leftovers (translated rows that are purely English letters/numbers)
            if is_trans and len(clean_trans) > 5:
                clean_no_tags = re.sub(r'\{.*?\}|<.*?>|\[.*?\]', '', clean_trans)
                has_thai = bool(re.search(r'[฀-๿]', clean_no_tags))
                has_eng = bool(re.search(r'[a-zA-Z]', clean_no_tags))
                if has_eng and not has_thai and len(clean_no_tags.strip()) > 3:
                    eng_leftovers.append({
                        "idx": idx,
                        "uid": uid,
                        "src": clean_src,
                        "trans": clean_trans
                    })

            # E. Glossary Violation Auditor
            if is_trans and glossary_lookup:
                for term_lower, expected_thai in glossary_lookup.items():
                    if len(term_lower) >= 3 and term_lower in src_lower:
                        if expected_thai not in clean_trans:
                            glossary_violations.append({
                                "idx": idx,
                                "uid": uid,
                                "term": term_lower,
                                "expected": expected_thai,
                                "src": clean_src,
                                "trans": clean_trans
                            })
                            break

        # ----------------------------------------------------
        # Post-Process & Assemble Results
        # ----------------------------------------------------
        # Assemble Cast List
        cast_list = []
        for name, mentions in speaker_mentions.most_common(50):
            sample = speaker_sample_rows.get(name, (0, "", "", ""))
            thai_name = character_names.get(name, "")
            if not thai_name and sample[3]:
                thai_name = sample[3]
            cast_list.append({
                "name": name,
                "thai_name": thai_name,
                "mentions": mentions,
                "first_row": sample[0],
                "sample_source": sample[2],
                "sample_trans": sample[3]
            })

        # Assemble Asset Bundles (Grouped by Root ID)
        asset_bundles = []
        for root_id, roles in raw_bundles.items():
            if len(roles) >= 2:  # Must have at least 2 associated parts (e.g. Name + Desc)
                b_type = "Asset"
                if any("Skill" in r["tag"] for r in roles.values()) or root_id.lower().startswith("ga_"):
                    b_type = "Skill"
                elif any("Item" in r["tag"] for r in roles.values()):
                    b_type = "Item"
                elif any("Quest" in r["tag"] for r in roles.values()) or root_id.lower().startswith("ot_"):
                    b_type = "Quest"

                name_part = roles.get("name", {})
                desc_part = roles.get("description", {})
                tooltip_part = roles.get("tooltip", {})

                asset_bundles.append({
                    "root_id": root_id,
                    "type": b_type,
                    "parts_count": len(roles),
                    "name_en": name_part.get("src", ""),
                    "name_th": name_part.get("trans", ""),
                    "desc_en": desc_part.get("src", ""),
                    "desc_th": desc_part.get("trans", ""),
                    "tooltip_en": tooltip_part.get("src", ""),
                    "tooltip_th": tooltip_part.get("trans", ""),
                    "all_indices": [r["idx"] for r in roles.values()],
                    "is_complete": all(bool(r["trans"]) for r in roles.values())
                })

        # Sort asset bundles: incomplete first, then by root_id
        asset_bundles.sort(key=lambda b: (b["is_complete"], b["type"], b["root_id"]))

        # Assemble Quests & Operations Dossier
        quest_dossier = []
        for rid, q in raw_quests.items():
            title_en = q["title_en"] or rid
            title_th = q["title_th"] or "-"
            total_r = len(q["rows"])
            done_r = q["done_count"]
            quest_dossier.append({
                "type": q["type"],
                "title_en": title_en,
                "title_th": title_th,
                "root_id": rid,
                "first_row": q["first_row"],
                "total_rows": total_r,
                "done_rows": done_r,
                "is_complete": done_r == total_r and total_r > 0,
                "search_url": cls.generate_quest_search_url(project_name, title_en),
                "wiki_url": cls.generate_quest_wiki_url(project_name, title_en),
                "row_indices": q["rows"]
            })

        # Sort quests: incomplete first, then by type, then title
        quest_dossier.sort(key=lambda x: (x["is_complete"], x["type"], x["title_en"]))

        # Assemble Entity Mining Results
        mined_entities = []
        for entity, count in proper_nouns_counter.most_common(80):
            if count >= 2:
                sample = noun_sample_rows.get(entity, (0, "", "", ""))
                in_glos = entity.lower() in glossary_lookup
                mined_entities.append({
                    "term": entity,
                    "frequency": count,
                    "in_glossary": in_glos,
                    "existing_glossary_trans": glossary_lookup.get(entity.lower(), ""),
                    "sample_row": sample[0],
                    "sample_src": sample[2],
                    "sample_trans": sample[3]
                })

        # Assemble Translation Conflicts (1 English text translated into multiple different Thai strings)
        translation_conflicts = []
        for src_text, variants in source_translations.items():
            if len(variants) > 1:
                total_occurrences = sum(len(indices) for indices in variants.values())
                var_list = []
                for t_text, idx_list in variants.items():
                    var_list.append({
                        "trans": t_text,
                        "count": len(idx_list),
                        "row_indices": idx_list
                    })
                var_list.sort(key=lambda x: x["count"], reverse=True)
                translation_conflicts.append({
                    "source": src_text,
                    "variant_count": len(variants),
                    "total_count": total_occurrences,
                    "variants": var_list
                })

        # Sort conflicts by highest total count first
        translation_conflicts.sort(key=lambda x: (x["total_count"], x["variant_count"]), reverse=True)

        # Integrity Score Calculation (0 to 100)
        conflict_penalty = min(20, len(translation_conflicts) * 0.2)
        tag_penalty = min(30, len(tag_errors) * 1.0)
        cjk_penalty = min(30, len(cjk_leaks) * 2.0)
        leftover_penalty = min(10, len(eng_leftovers) * 0.1)

        raw_score = 100 - (conflict_penalty + tag_penalty + cjk_penalty + leftover_penalty)
        integrity_score = max(0, min(100, round(raw_score, 1)))

        scan_duration = round(time.time() - t_start, 2)

        return {
            "project_name": project_name,
            "scan_duration": scan_duration,
            "metrics": {
                "total_rows": total_rows,
                "total_words": total_words,
                "total_chars": total_chars,
                "translated_rows": translated_rows,
                "untranslated_rows": untranslated_rows,
                "progress_percent": round((translated_rows / total_rows * 100), 1) if total_rows > 0 else 0,
                "integrity_score": integrity_score,
                "categories": dict(category_counts),
                "category_trans": dict(category_trans_counts),
            },
            "cast": cast_list,
            "quests": quest_dossier,
            "bundles": asset_bundles,
            "entities": mined_entities,
            "conflicts": translation_conflicts,
            "tag_errors": tag_errors,
            "cjk_leaks": cjk_leaks,
            "eng_leftovers": eng_leftovers,
            "glossary_violations": glossary_violations,
        }

    @classmethod
    def _empty_report(cls, project_name):
        return {
            "project_name": project_name,
            "scan_duration": 0,
            "metrics": {
                "total_rows": 0, "total_words": 0, "total_chars": 0,
                "translated_rows": 0, "untranslated_rows": 0,
                "progress_percent": 0, "integrity_score": 100,
                "categories": {}, "category_trans": {}
            },
            "cast": [], "quests": [], "bundles": [], "entities": [],
            "conflicts": [], "tag_errors": [], "cjk_leaks": [],
            "eng_leftovers": [], "glossary_violations": []
        }

    @classmethod
    def generate_quest_search_url(cls, game_title, quest_title):
        """
        Generates a direct Google Walkthrough Search URL for a specific quest.
        """
        clean_title = re.sub(r'<[^>]+>', '', str(quest_title or '')).strip()
        clean_game = str(game_title or '').strip()
        query = f'{clean_game} "{clean_title}" walkthrough guide'
        return f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"

    @classmethod
    def generate_quest_wiki_url(cls, game_title, quest_title):
        """
        Generates a direct Lore Wiki Search URL.
        """
        clean_title = re.sub(r'<[^>]+>', '', str(quest_title or '')).strip()
        clean_game = str(game_title or '').strip()
        query = f'{clean_game} {clean_title} wiki'
        return f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"

    @classmethod
    def build_quest_lore_prompt(cls, game_title, quest_item):
        """
        Builds a high-precision prompt for online LLM / lore cross-referencing.
        """
        q_title = quest_item.get("title_en", "")
        q_type = quest_item.get("type", "")
        rid = quest_item.get("root_id", "")
        return (
            f"You are a master lore scholar and video game localization director for '{game_title}'.\n"
            f"Analyze the following quest/operation:\n"
            f"- Quest Title: \"{q_title}\"\n"
            f"- Category: {q_type}\n"
            f"- Internal ID: {rid}\n\n"
            f"Please provide:\n"
            f"1. **Canonical Lore & Faction Context**: Explain the background, factions involved, and setting.\n"
            f"2. **Characters & Objectives**: Who is the quest giver, companions, or key targets involved?\n"
            f"3. **Localization Recommendations (Thai)**: Provide the ideal Thai translation for the quest title and explain tone, nuances, and specific lore terms to keep consistent.\n"
            f"4. **Locked Glossary Terms**: Key proper nouns that must be standardized across the team."
        )

    @classmethod
    def generate_markdown_dossier(cls, report, game_title=None):
        """
        Generates a comprehensive Markdown Localization Dossier/Bible from the report.
        """
        title = game_title or report.get("project_name", "Game Localization Dossier")
        m = report.get("metrics", {})
        total_r = m.get("total_rows", 0)
        trans_r = m.get("translated_rows", 0)
        pct = m.get("progress_percent", 0)
        score = m.get("integrity_score", 100)

        lines = [
            f"# รายงานวิเคราะห์โครงสร้างและคุณภาพงานแปลทั้งเกม: {title}",
            f"> วิเคราะห์โดย **TStudio Localization Intelligence Engine** | ใช้เวลาสแกน: `{report.get('scan_duration', 0)}` วินาที",
            "",
            "## 1. ดัชนีชี้วัดภาพรวม (Executive Overview)",
            "",
            f"- **จำนวนแถวทั้งหมด (Total Rows)**: `{total_r:,}` แถว",
            f"- **จำนวนคำต้นฉบับ (Total Words)**: `{m.get('total_words', 0):,}` คำ",
            f"- **ความคืบหน้าการแปล (Progress)**: `{trans_r:,} / {total_r:,}` แถว (**{pct}%**)",
            f"- **คะแนนคุณภาพและความถูกต้อง (Integrity Score)**: **`{score}/100`**",
            "",
            "### สัดส่วนเนื้อหาในเกม (Content Breakdown by Category)",
            "",
            "| หมวดหมู่ (Category) | จำนวนแถว | แปลแล้ว | ความคืบหน้า (%) |",
            "| :--- | :---: | :---: | :---: |"
        ]

        cats = m.get("categories", {})
        c_trans = m.get("category_trans", {})
        for c_name, count in sorted(cats.items(), key=lambda x: x[1], reverse=True):
            done = c_trans.get(c_name, 0)
            c_pct = round((done / count * 100), 1) if count > 0 else 0
            lines.append(f"| **{c_name}** | {count:,} | {done:,} | {c_pct}% |")

        lines.extend([
            "",
            "---",
            "",
            "## 2. ทำเนียบตัวละครสำคัญ (Dramatis Personae & Cast Discovery)",
            "",
            "| ตัวละคร (Character) | ชื่อไทย (Thai Name) | บทพูด/ความถี่ (Lines) | ตัวอย่างบทสนทนา (Sample Quote) |",
            "| :--- | :--- | :---: | :--- |"
        ])

        cast = report.get("cast", [])
        for char in cast[:25]:
            name = char["name"]
            th = char["thai_name"] or "-"
            mentions = char["mentions"]
            quote = char["sample_source"]
            if len(quote) > 60: quote = quote[:57] + "..."
            lines.append(f'| **{name}** | {th} | {mentions:,} | *"{quote}"* |')

        lines.extend([
            "",
            "---",
            "",
            "## 3. สารบบเควสต์และภารกิจทั้งหมดในเกม (Quest & Mission Dossier)",
            f"ตรวจพบเควสต์และปฏิบัติการทั้งหมด: **{len(report.get('quests', [])):,} ภารกิจ**",
            "",
            "| ประเภท (Type) | ชื่อเควสต์ (EN) | คำแปลภาษาไทย (TH) | รหัสอ้างอิง | จำนวนแถว | สถานะ |",
            "| :---: | :--- | :--- | :--- | :---: | :---: |"
        ])

        quests = report.get("quests", [])
        for q in quests[:35]:
            q_type = q["type"]
            t_en = q["title_en"]
            t_th = q["title_th"]
            rid = q["root_id"]
            progress = f"{q['done_rows']}/{q['total_rows']}"
            status = "✅ ครบ" if q["is_complete"] else "⏳ กำลังแปล"
            lines.append(f"| {q_type} | **{t_en}** | {t_th} | `{rid}` | {progress} | {status} |")

        lines.extend([
            "",
            "---",
            "",
            "## 4. ชุดสกิลและไอเทมสำคัญ (Asset Bundles)",
            f"ตรวจพบชุดข้อมูล Asset Bundles ทั้งหมด: **{len(report.get('bundles', [])):,} ชุด**",
            "",
            "| ประเภท | รหัสอ้างอิง (Root ID) | ชื่อสกิล/ไอเทม (Name) | คำอธิบาย (Description) | สถานะ |",
            "| :---: | :--- | :--- | :--- | :---: |"
        ])

        bundles = report.get("bundles", [])
        for b in bundles[:20]:
            b_type = b["type"]
            rid = b["root_id"]
            name = b["name_th"] or b["name_en"] or "-"
            desc = b["desc_th"] or b["desc_en"] or "-"
            if len(desc) > 50: desc = desc[:47] + "..."
            status = "✅ ครบ" if b["is_complete"] else "⏳ ขาด"
            lines.append(f"| {b_type} | `{rid}` | **{name}** | {desc} | {status} |")

        lines.extend([
            "",
            "---",
            "",
            "## 5. คำศัพท์และ Proper Noun สำคัญที่ควรทำ Glossary (Mined Entities)",
            "",
            "| คำศัพท์ภาษาอังกฤษ (Entity) | ความถี่ (Frequency) | สถานะ Glossary | ตัวอย่างที่พบ (Sample Context) |",
            "| :--- | :---: | :---: | :--- |"
        ])

        entities = report.get("entities", [])
        for ent in entities[:25]:
            term = ent["term"]
            freq = ent["frequency"]
            status = "✅ มีใน Glossary" if ent["in_glossary"] else "⚠️ ยังไม่มี"
            ctx = ent["sample_src"]
            if len(ctx) > 50: ctx = ctx[:47] + "..."
            lines.append(f"| **{term}** | {freq:,} | {status} | {ctx} |")

        lines.extend([
            "",
            "---",
            "",
            "## 6. การตรวจสอบความขัดแย้งและแท็กโค้ดเสียหาย (Quality & Consistency Audit)",
            "",
            f"- **ประโยคที่แปลขัดแย้งกัน (1-to-Many Conflicts)**: `{len(report.get('conflicts', [])):,}` จุด",
            f"- **แท็กตัวแปรเกมเสียหาย/ไม่ตรง (Tag Errors)**: `{len(report.get('tag_errors', [])):,}` จุด",
            f"- **ข้อความภาษาจีนหลุดมา (CJK Leaks)**: `{len(report.get('cjk_leaks', [])):,}` จุด",
            f"- **ภาษาอังกฤษตกค้างในช่องแปล (Leftovers)**: `{len(report.get('eng_leftovers', [])):,}` จุด",
            ""
        ])

        conflicts = report.get("conflicts", [])
        if conflicts:
            lines.extend([
                "### ตัวอย่างประโยคที่แปลขัดแย้งกัน (Top Inconsistent Translations)",
                ""
            ])
            for c in conflicts[:10]:
                src_txt = c['source']
                lines.append(f'#### 🔸 "{src_txt}" (พบ {c["total_count"]} ครั้ง มี {c["variant_count"]} คำแปล)')
                for v in c["variants"]:
                    lines.append(f"  - `{v['trans']}` (ใช้ {v['count']} จุด)")
                lines.append("")

        return "\n".join(lines)
