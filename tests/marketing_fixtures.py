"""Offline provider fixtures and reusable, complete integration examples."""
import copy
import json

from scripts.build_marketing_examples import CASES, make_video, snapshot


def request_body(*, videos=False, variants=1):
    return {"product": snapshot(CASES[0]).model_dump(mode="json"),
        "objective": "introduce_product", "audience": CASES[0]["audience"],
        "variants": variants, **({"targets": [
            {"channel": "tiktok", "placement": "short_video", "content_type": "video_script"},
            {"channel": "facebook", "placement": "reels", "content_type": "video_script"},
            {"channel": "shopee", "placement": "video", "content_type": "video_script"}]} if videos else
            {"channels": ["facebook", "tiktok", "shopee"]})}


def model_draft(data):
    target = data["target"]
    name = data["product"]["name"]
    kind = target["content_type"]
    angle = data["required_angle"]
    if kind == "caption":
        content = {"content_type": kind, "angle": angle, "hook": "Bạn muốn xem chi tiết nào trước khi chọn?",
            "body": name + ". Xem thông tin sản phẩm để cân nhắc theo nhu cầu của bạn.",
            "cta": "Xem thông tin sản phẩm trong shop.", "hashtags": [], "plain_text": ""}
    elif kind == "listing":
        content = {"content_type": kind, "angle": angle, "title": name, "short_description": name,
            "highlights": ["Kiểu cổ tròn"], "detailed_description": "Xem thông tin " + name,
            "attributes": [], "cta": "Xem thông tin và phân loại trong shop.", "plain_text": ""}
    else:
        script = make_video(CASES[0], target["channel"]).model_dump(mode="json")
        options = data["effective_settings"]
        duration, mode = options["duration_seconds"], options["production_mode"]
        factor = duration / script["total_duration_seconds"]
        for scene in script["scenes"]:
            for field in ("start_seconds", "end_seconds", "duration_seconds"):
                scene[field] *= factor
            if mode == "text_only":
                scene["dialogue"] = scene["voiceover"] = None
            elif mode == "on_camera":
                scene["dialogue"], scene["voiceover"] = scene["voiceover"], None
            scene["shows_face"] = mode == "on_camera"
        script.update(angle=angle, total_duration_seconds=duration, production_mode=mode,
            video_style=options["video_style"], audience=data["audience"], objective=data["objective"])
        if data["variant"] > 1:
            script["hook"] = CASES[0]["faq"] if data["variant"] == 3 else "Cùng nhìn cận chi tiết sản phẩm."
            script["scenes"][0]["on_screen_text"] = script["hook"]
        if not options["include_post_caption"]:
            script["post_caption"] = None
        if not options["include_shot_list"]:
            script["production"] = None
        content = script
    return {"content": content, "fact_claims": [{"text": name, "fact_refs": ["product.name"]}],
            "warnings": [], "assumptions": []}


def strategy_fixture():
    return {"strategies": [dict(priority=i, name=name, problem="Khách cần xem rõ chi tiết.",
        suitable_when="Có sản phẩm thật và thông tin đã xác nhận.", conditions=["Shop kiểm tra dữ liệu sản phẩm."],
        message="Giúp khách xem chi tiết để lựa chọn.", channels=["facebook"],
        actions=["Chọn chi tiết cần giải thích.", "Chuẩn bị nội dung từ facts.", "Đo phản hồi và điều chỉnh."],
        resources=["điện thoại"], assumptions=["Chưa có baseline."],
        kpis_to_measure=["lượt xem thông tin sản phẩm", "câu hỏi cần giải đáp"],
        experiment="Đo baseline trước; chỉ đổi hook, giữ CTA và chỉ số chính, chưa kết luận từ vài lượt xem.",
        stop_or_adjust_when="Điều chỉnh khi thông tin không còn phù hợp hoặc công sức vượt nguồn lực.")
        for i, name in enumerate(["Demo chi tiết", "Giải đáp câu hỏi"], 1)], "assumptions": ["Nguồn lực chưa được cung cấp."]}


class FakeLLM:
    model = "offline-fixture"

    def __init__(self, transform=None):
        self.calls = []
        self.transform = transform

    def generate_json(self, **kwargs):
        data = json.loads(kwargs["user_message"])["untrusted_data"]
        self.calls.append((data, kwargs))
        output = strategy_fixture() if data["operation"] == "strategy" else model_draft(data)
        if self.transform:
            output = self.transform(data, output)
        return {"text": output if isinstance(output, str) else json.dumps(output, ensure_ascii=False),
                "model": self.model, "usage": None}
