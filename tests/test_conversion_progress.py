import json

from app.conversion_progress import ConversionProgress, emit_progress, scoped_progress


def test_wait_is_a_milestone_not_a_time_based_prediction(tmp_path, monkeypatch):
    now = [100.0]
    monkeypatch.setattr("app.conversion_progress.time.monotonic", lambda: now[0])
    events = []
    sink = ConversionProgress(tmp_path, events.append)
    sink.stage("session", "open")
    sink.stage("upload", "attach")
    sink.stage("waiting", "wait")
    now[0] += 500
    sink("still waiting")
    assert events[-1]["percent"] == events[-2]["percent"] == 25
    assert events[-1]["waiting"] and events[-1]["elapsedSeconds"] == 500
    sink.stage("session", "recover Chrome")
    assert events[-1]["percent"] == 25
    sink.stage("quality", "review", 2, 4)
    assert events[-1]["percent"] == 66 and not events[-1]["waiting"]
    emit_progress(scoped_progress(sink, "refine_quality"), "quality", "fixed", 4, 4)
    assert events[-1]["percent"] == 86
    sink.stage("audio", "voice", 1, 3)
    assert events[-1]["percent"] == 91
    sink.stage("save", "save")
    assert events[-1]["percent"] < 100
    sink.stage("completed", "saved")
    assert events[-1]["percent"] == 100
    assert [e["percent"] for e in events] == sorted(e["percent"] for e in events)


def test_resume_keeps_progress_but_needs_a_new_library_commit_for_100(tmp_path):
    events = []
    first = ConversionProgress(tmp_path, events.append)
    first.stage("audio", "voices", 6, 10)
    resumed = ConversionProgress(tmp_path, events.append)
    resumed.stage("session", "resume")
    assert events[-1]["percent"] == 93
    resumed.stage("completed", "saved")
    next_run = ConversionProgress(tmp_path, events.append)
    next_run.stage("import", "verify cached file")
    assert events[-1]["percent"] == 99


def test_invalid_checkpoint_and_failed_persistence_do_not_fail_a_web_job(tmp_path):
    path = tmp_path / "conversion-progress.json"
    path.write_text(json.dumps({"version": 1, "percent": -2, "stage": "waiting", "elapsedSeconds": 4}))
    events = []
    sink = ConversionProgress(tmp_path, events.append)
    sink.stage("session", "open")
    assert events[-1]["percent"] == 2
    sink.path = tmp_path / "missing" / "conversion-progress.json"
    sink.stage("waiting", "sent once")
    assert events[-1]["percent"] == 25


def test_legacy_callbacks_still_receive_only_text():
    messages = []
    emit_progress(messages.append, "audio", "one voice", 1, 2)
    assert messages == ["one voice"]


def test_stage_timings_record_real_wait_without_advancing_percentage(tmp_path, monkeypatch):
    clock = [100.0]
    monkeypatch.setattr("app.conversion_progress.time.monotonic", lambda: clock[0])
    sink = ConversionProgress(tmp_path, lambda _: None)
    sink.stage("upload", "attach")
    clock[0] += 20
    sink.stage("waiting", "generation")
    clock[0] += 240
    sink.stage("download", "receive")
    saved = json.loads((tmp_path / "conversion-progress.json").read_text())
    assert saved["stageSeconds"]["upload"] == 20
    assert saved["stageSeconds"]["waiting"] == 240
    assert saved["percent"] == 55
