"""Fill only missing language drafts, keeping existing bilingual work intact."""


def plan_batch(library, lesson, limit=50):
    plans = []
    subject = lesson["subject"]
    for segment in lesson["segments"]:
        language = segment.get("source_language", lesson.get("source_language", "vi"))
        target = "en" if language == "vi" else "vi"
        if segment.get("locked") or segment.get("approved") or segment.get(target, "").strip():
            continue
        text = segment.get(language, "")
        if not text.strip():
            continue
        plan = {"id": segment["id"], "locator": segment["locator"], "language": language, "source": text}
        exact = library.exact_translation(subject, text, source_language=language)
        choices = library.approved_translations(subject, text, language, exclude=(lesson["id"], segment["id"])) if not exact else []
        if exact:
            plan.update(draft=exact, provenance="teacher_glossary")
        elif len(choices) == 1:
            plan.update(draft=choices[0]["text"], provenance="teacher_memory")
        elif choices:
            plan["error"] = "Có nhiều bản thầy cô đã duyệt; chọn bản phù hợp ở từng đoạn."
        else:
            knowledge = library.knowledge_translation(subject, text, language)
            if knowledge:
                plan.update(draft=knowledge["text"], provenance=knowledge["tier"])
        plans.append(plan)
        if len(plans) >= limit:
            break
    return plans


def translate_batch(plans, terms, cancelled=None):
    from .translation import draft_resources, translate_with_resources

    results, warnings = [], []
    for language in ("vi", "en"):
        resources = None
        cached = {}
        try:
            for plan in (p for p in plans if p["language"] == language):
                if cancelled and cancelled.is_set():
                    return {"drafts": [], "warnings": []}
                if plan.get("error"):
                    warnings.append(plan["locator"] + ": " + plan["error"])
                    continue
                try:
                    draft = plan.get("draft")
                    if draft is None:
                        text = plan["source"]
                        if text not in cached:
                            if resources is None:
                                resources = draft_resources(language)
                            cached[text] = translate_with_resources(text, language, terms, *resources)
                        draft = cached[text]
                    results.append({**plan, "draft": draft, "provenance": plan.get("provenance", "machine_draft")})
                except (ValueError, RuntimeError) as exc:
                    warnings.append(plan["locator"] + ": " + str(exc))
        finally:
            if resources:
                resources[1].unload_model()
    return {"drafts": results, "warnings": warnings}
