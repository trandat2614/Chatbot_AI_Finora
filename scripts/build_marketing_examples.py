"""Rebuild original synthetic editorial examples; never calls a provider.

Run from repo root: python scripts/build_marketing_examples.py
The authored scenarios below are examples, never templates for real SKU facts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.schemas.marketing import ProductSnapshot, VideoScript
from src.services.marketing.validation import render_content

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "knowledge" / "marketing"
DATE = "2026-11-06"
VERSION = "1.0.0"
TARGETS = {"tiktok": ["tiktok", "short_video", "video_script"],
           "facebook": ["facebook", "reels", "video_script"], "shopee": ["shopee", "video", "video_script"]}

# Each scenario has its own product, audience, action, question and demonstrable facts.
CASES = [
    dict(sku="AT001", name="Áo thun cổ tròn", industry="fashion", audience="người thích trang phục đơn giản",
         attrs={"material": "cotton", "color": "trắng", "neck": "cổ tròn"}, duration=15, mode="hands_only", style="product_demo",
         hook="Muốn nhìn rõ cổ áo trước khi chọn?", reels="Một góc quay để xem rõ chiếc áo cổ tròn.", shopee="Xem cổ và màu áo trước khi chọn phân loại.",
         actions=["Đặt áo lên mặt bàn, kéo phần cổ vào khung hình.", "Hai tay mở phẳng cổ áo rồi quay cận bề mặt vải.", "Giữ toàn bộ áo trong khung hình, đặt thẻ tên bên cạnh."],
         words=["Đây là áo thun cổ tròn.", "Chất liệu cotton, màu trắng.", "Xem thông tin áo trong shop."], texts=["Áo thun cổ tròn", "Cotton · trắng", "Xem thông tin sản phẩm"], prop="mặt bàn", faq="Áo có kiểu cổ nào?",
         caption="Bạn muốn xem rõ phần cổ trước khi chọn áo?\n\nÁo thun cổ tròn màu trắng có chất liệu cotton. Nhìn từ tổng thể đến cận cảnh phần cổ giúp bạn hình dung kiểu áo trước khi phối với đồ đang có.\n\nXem thông tin áo để cân nhắc lựa chọn phù hợp với bạn.",
         listing="Áo thun cổ tròn cotton màu trắng"),
    dict(sku="TUI002", name="Túi đeo chéo", industry="accessories", audience="người cần sắp xếp đồ mang theo",
         attrs={"color": "đen", "compartments": "hai ngăn", "strap": "dây điều chỉnh được"}, duration=30, mode="voiceover", style="tutorial",
         hook="Bạn thường để đồ nhỏ ở ngăn nào?", reels="Cùng xem cách chia đồ trong túi đeo chéo.", shopee="Mở từng ngăn của túi trước khi chọn mua.",
         actions=["Quay từ trên xuống túi đang đóng, bàn tay đặt cạnh túi.", "Mở ngăn phía trước rồi ngăn phía sau, giữ mỗi ngăn trong khung hình.", "Tay điều chỉnh dây, dừng để thấy vị trí thay đổi.", "Đóng túi, đặt ngay ngắn dưới máy quay."],
         words=["Đây là túi đeo chéo màu đen.", "Túi có hai ngăn để bạn chọn cách chia đồ.", "Dây điều chỉnh được. Hãy xem chi tiết dây khi lựa chọn.", "Tìm túi đeo chéo trong shop để xem thông tin."], texts=["Túi đeo chéo", "Hai ngăn", "Dây điều chỉnh được", "Xem chi tiết trong shop"], prop="bàn trống", faq="Dây túi có điều chỉnh được không?",
         caption="Đồ nhỏ nên để ở đâu để bạn dễ nhớ?\n\nTúi đeo chéo màu đen có hai ngăn. Bạn có thể tự chọn cách chia đồ theo thói quen mang theo. Phần dây điều chỉnh được cũng là chi tiết nên xem kỹ khi cân nhắc.\n\nXem thông tin túi và hình các ngăn trước khi lựa chọn.", listing="Túi đeo chéo màu đen hai ngăn dây điều chỉnh được"),
    dict(sku="KHAY003", name="Khay để bàn", industry="household", audience="người muốn bố trí góc làm việc",
         attrs={"material": "gỗ", "shape": "hình chữ nhật", "color": "nâu"}, duration=60, mode="text_only", style="scenario",
         hook="Thử chọn một vị trí cố định cho đồ trên bàn.", reels="Một góc bàn, một khay để bạn tự sắp xếp.", shopee="Xem hình dáng và chất liệu khay để bàn.",
         actions=["Quay góc bàn trống, đưa khay vào giữa khung hình.", "Quay cạnh dài và cạnh ngắn để thấy hình chữ nhật.", "Đổi sang góc nghiêng, giữ cận bề mặt gỗ.", "Đặt khay vào vị trí dự kiến sử dụng, quay tổng thể.", "Đưa thẻ tên sản phẩm cạnh khay, giữ khung hình tĩnh."],
         words=[None, None, None, None, None], texts=["Khay để bàn", "Hình chữ nhật", "Gỗ · màu nâu", "Bạn sẽ đặt khay ở góc nào?", "Xem thông tin trong shop"], prop="góc bàn", faq="Khay có hình dạng gì?",
         caption="Bạn sẽ dành góc nào trên bàn cho một chiếc khay?\n\nKhay để bàn bằng gỗ, màu nâu, có hình chữ nhật. Hãy nhìn tổng thể bàn và vị trí bạn muốn đặt trước khi lựa chọn; ảnh cận giúp bạn xem bề mặt sản phẩm rõ hơn.\n\nXem thông tin khay để cân nhắc cách bố trí phù hợp với góc của bạn.", listing="Khay để bàn gỗ hình chữ nhật màu nâu"),
    dict(sku="BINH004", name="Bình gốm trang trí", industry="handmade_decor", audience="người thích trang trí kệ nhỏ",
         attrs={"material": "gốm", "color": "kem", "finish": "bề mặt nhám"}, duration=30, mode="on_camera", style="presenter",
         hook="Một chiếc bình có thể bắt đầu từ góc kệ trống.", reels="Xem bề mặt nhám của chiếc bình màu kem.", shopee="Cận cảnh bình gốm trước khi chọn đồ trang trí.",
         actions=["Người dẫn cầm bình ngang ngực, đứng cạnh kệ trống.", "Đưa bình lại gần máy để thấy màu và bề mặt.", "Đặt bình lên kệ, lùi ra để thấy vị trí.", "Chỉ tay về bình, giữ tên sản phẩm trên khung hình."],
         words=["Bạn đang tìm đồ trang trí cho góc kệ?", "Đây là bình gốm trang trí màu kem, bề mặt nhám.", "Hãy nhìn màu bình cạnh đồ bạn đang có.", "Xem thông tin bình trong shop."], texts=["Góc kệ của bạn", "Gốm · kem · bề mặt nhám", "Cân nhắc vị trí đặt", "Xem thông tin sản phẩm"], prop="kệ trống", faq="Bề mặt bình bóng hay nhám?",
         caption="Bạn thích một góc kệ có màu sắc nhẹ nhàng?\n\nBình gốm trang trí màu kem có bề mặt nhám. Hãy xem ảnh tổng thể cùng ảnh cận bề mặt để chọn theo cách bạn muốn bố trí không gian. Đây là gợi ý trang trí, bạn vẫn là người quyết định vị trí đặt.\n\nXem thông tin bình trước khi lựa chọn.", listing="Bình gốm trang trí màu kem bề mặt nhám"),
    dict(sku="KEP005", name="Kẹp tóc", industry="accessories", audience="người muốn xem thao tác kẹp tóc",
         attrs={"color": "nâu", "mechanism": "dạng càng cua", "surface": "bề mặt trơn"}, duration=15, mode="hands_only", style="faq",
         hook="Kẹp mở ra như thế nào?", reels="Xem thao tác mở kẹp bằng tay.", shopee="Cận cảnh cơ chế kẹp tóc dạng càng cua.",
         actions=["Giữ kẹp trên nền sáng, nhìn từ cạnh bên.", "Bàn tay bóp rồi thả kẹp, giữ rõ phần càng.", "Đặt kẹp xuống, quay cận màu và thẻ tên."],
         words=["Kẹp tóc dạng càng cua.", "Xem thao tác mở và khép kẹp.", "Chọn theo nhu cầu của bạn."], texts=["Kẹp tóc", "Dạng càng cua", "Xem thông tin trong shop"], prop="tấm nền sáng", faq="Kẹp có cơ chế nào?",
         caption="Muốn chọn kẹp tóc, bạn có thể bắt đầu bằng cách xem cơ chế mở.\n\nMẫu kẹp này có dạng càng cua, màu nâu và bề mặt trơn. Hình cận cùng thao tác bóp, thả giúp bạn nhìn rõ sản phẩm trước khi quyết định.\n\nXem thông tin kẹp để cân nhắc theo cách bạn thường dùng.", listing="Kẹp tóc dạng càng cua màu nâu bề mặt trơn"),
    dict(sku="HOP006", name="Hộp đựng đồ", industry="household", audience="người cần phân loại đồ nhỏ",
         attrs={"material": "nhựa", "lid": "nắp rời", "color": "trong suốt"}, duration=60, mode="voiceover", style="unboxing",
         hook="Hộp và nắp rời trông như thế nào khi mở?", reels="Xem hộp đựng đồ từ tổng thể đến phần nắp.", shopee="Kiểm tra hộp và nắp rời trước khi chọn.",
         actions=["Đặt hộp trên bàn, quay toàn bộ hộp và nắp.", "Nhấc nắp rời ra, đặt cạnh thân hộp.", "Quay góc nghiêng của thân hộp trong suốt.", "Đặt nắp trở lại rồi mở lần nữa thật chậm.", "Xếp hộp và nắp cạnh nhau cùng thẻ tên."],
         words=["Đây là hộp đựng đồ bằng nhựa.", "Nắp rời được nhấc ra riêng khi mở hộp.", "Màu trong suốt giúp bạn nhìn hình dáng phần thân.", "Hãy xem cách mở nắp trước khi cân nhắc lựa chọn.", "Xem thông tin hộp đựng đồ trong shop."], texts=["Hộp đựng đồ", "Nắp rời", "Nhựa · trong suốt", "Xem thao tác mở nắp", "Thông tin trong shop"], prop="bàn sáng", faq="Nắp có gắn liền với hộp không?",
         caption="Bạn quen dùng hộp có nắp rời hay nắp liền?\n\nHộp đựng đồ này bằng nhựa trong suốt và có nắp rời. Trước khi chọn, hãy xem ảnh thân hộp cùng phần nắp để hình dung thao tác mở, đóng theo thói quen của bạn.\n\nXem thông tin hộp để lựa chọn đúng nhu cầu.", listing="Hộp đựng đồ nhựa trong suốt có nắp rời"),
    dict(sku="SO007", name="Sổ tay bìa vải", industry="handmade_decor", audience="người thích ghi chép bằng tay",
         attrs={"cover": "bìa vải", "pages": "giấy kẻ ngang", "color": "xanh"}, duration=30, mode="text_only", style="tutorial",
         hook="Mở sổ và xem trang giấy trước khi viết.", reels="Một góc nhìn rõ bìa và giấy của sổ tay.", shopee="Xem bìa vải và dòng kẻ của sổ tay.",
         actions=["Đặt sổ đóng trên bàn, tay vuốt nhẹ bìa.", "Mở sổ từ từ, dừng ở trang giấy kẻ ngang.", "Đặt bút cạnh trang giấy, giữ dòng kẻ trong khung hình.", "Khép sổ, đưa thẻ tên vào cạnh bìa."],
         words=[None, None, None, None], texts=["Sổ tay bìa vải", "Giấy kẻ ngang", "Bạn sẽ ghi điều gì?", "Xem chi tiết trong shop"], prop="bàn và bút", faq="Giấy trong sổ có dòng kẻ không?",
         caption="Trang giấy đầu tiên của bạn sẽ dành cho điều gì?\n\nSổ tay có bìa vải màu xanh và giấy kẻ ngang. Bạn có thể xem ảnh bìa, trang mở để cân nhắc theo cách ghi chép thường ngày. Không cần bắt đầu bằng một kế hoạch lớn; chỉ cần một điều bạn muốn ghi lại.\n\nXem thông tin sổ trước khi lựa chọn.", listing="Sổ tay bìa vải màu xanh giấy kẻ ngang"),
    dict(sku="AO008", name="Áo khoác có mũ", industry="fashion", audience="người muốn kiểm tra chi tiết áo trước khi chọn",
         attrs={"hood": "có mũ", "closure": "khóa kéo", "color": "xám"}, duration=60, mode="hands_only", style="objection_handling",
         hook="Bạn muốn xem chi tiết nào trước khi chọn áo khoác?", reels="Cùng kiểm tra mũ và khóa kéo của áo.", shopee="Xem mũ, khóa kéo và màu áo trước khi chọn phân loại.",
         actions=["Trải áo trên bàn, quay toàn bộ mặt trước.", "Mở phần mũ, giữ góc nhìn từ trên xuống.", "Kéo khóa chậm từ dưới lên, quay cận phần khóa.", "Mở áo trở lại, giữ màu vải trong ánh sáng tự nhiên.", "Gấp áo, để thẻ tên bên cạnh."],
         words=["Đây là áo khoác có mũ màu xám.", "Mở phần mũ để bạn nhìn rõ chi tiết.", "Áo dùng khóa kéo. Cùng xem thao tác kéo khóa.", "Nhìn tổng thể áo và từng chi tiết trước khi lựa chọn.", "Xem thông tin áo trong shop để cân nhắc."], texts=["Áo khoác có mũ", "Chi tiết mũ", "Khóa kéo", "Màu xám", "Xem thông tin trong shop"], prop="mặt bàn rộng", faq="Áo dùng khóa kéo hay cúc?",
         caption="Bạn thường xem mũ hay khóa áo trước khi chọn áo khoác?\n\nMẫu áo khoác màu xám này có mũ và khóa kéo. Ảnh tổng thể giúp bạn xem kiểu áo, còn ảnh cận dành cho những chi tiết bạn quan tâm. Hãy xem kỹ thông tin trước khi quyết định theo nhu cầu riêng.\n\nXem thông tin áo và phần phân loại trong shop.", listing="Áo khoác có mũ màu xám khóa kéo"),
]


def snapshot(case):
    return ProductSnapshot(sku=case["sku"], name=case["name"], source="synthetic_fixture",
        updated_at=DATE + "T09:00:00+07:00", industry=case["industry"],
        attributes=[{"key": key, "value": value, "source": "synthetic_fixture"} for key, value in case["attrs"].items()])


def make_video(case, channel):
    duration = case["duration"]
    count = len(case["actions"])
    boundaries = {15: [0, 4, 10, 15], 30: [0, 5, 14, 24, 30], 60: [0, 6, 20, 36, 50, 60]}[duration]
    hook = case["hook"] if channel == "tiktok" else case["reels"] if channel == "facebook" else case["shopee"]
    scenes = []
    for i in range(count):
        action = case["actions"][i]
        text = case["texts"][i]
        speech = case["words"][i]
        if channel == "facebook":
            action += " Giữ khung hình tĩnh để xem rõ khi tắt âm." if i == 1 else ""
            text = case["name"] if i == 0 else text
        elif channel == "shopee":
            action += " Đặt nhãn tên sản phẩm cùng khung hình." if i == 0 else ""
            if i == count - 1:
                text = "Tìm sản phẩm trong shop"
                if speech:
                    speech = "Tìm sản phẩm trong shop để xem chi tiết."
        else:
            action += " Chuyển từ toàn cảnh sang cận bằng một nhịp cắt." if i == 1 else ""
        scenes.append(dict(scene_id=f"s{i+1}", start_seconds=boundaries[i], end_seconds=boundaries[i+1],
            duration_seconds=boundaries[i+1] - boundaries[i], visual_action=action,
            shot_type="cận cảnh" if i not in (0, count - 1) else "toàn cảnh sản phẩm",
            camera_direction="Máy cố định, lấy nét vào sản phẩm.",
            dialogue=speech if case["mode"] == "on_camera" else None,
            voiceover=speech if case["mode"] not in ("on_camera", "text_only") else None,
            on_screen_text=text, audio_direction="Âm thanh thao tác thật; không cần nhạc." if not speech else "Giọng rõ, để khoảng nghỉ cho thao tác.",
            editing_notes="Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
            people_required=1, shows_face=case["mode"] == "on_camera"))
    script = VideoScript(title=case["name"] + " — " + case["faq"], concept=hook, angle="Xem chi tiết để lựa chọn",
        objective="introduce_product", audience=case["audience"], hook=hook, key_message=case["name"],
        total_duration_seconds=duration, production_mode=case["mode"], video_style=case["style"], scenes=scenes,
        cta={"text": "Tìm sản phẩm trong shop để xem chi tiết." if channel == "shopee" else "Xem thông tin sản phẩm trong shop.",
             "action": "view_product", "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."},
        product_attachment_note="Kiểm tra quyền gắn đúng SKU trước khi đăng; chưa xác nhận đã gắn.",
        post_caption=(case["faq"] + " Xem chi tiết sản phẩm trong shop."), hashtags=[], cover_text=case["name"],
        production={"shot_list": case["actions"], "props": [case["name"], case["prop"]], "location": case["prop"],
                    "actors": 1, "filming_checklist": ["Lau ống kính.", "Đọc lại facts và kiểm tra sản phẩm đúng SKU.", "Quay dọc, kiểm tra chữ không bị giao diện che."],
                    "editing_guide": ["Ghép đúng timeline.", "Đồng bộ chữ với thao tác.", "Kiểm tra âm thanh và phụ đề trước khi xuất."]})
    script.plain_text = render_content(script)
    return script


def example(case, channel, index, content):
    return {"example_id": f"{channel}_{content['content_type']}_{index:02d}", "channel": channel,
        "industry": case["industry"], "audience": case["audience"], "objective": "introduce_product",
        "input_facts": snapshot(case).model_dump(mode="json"), "tone": "friendly",
        "framework": "FAB" if index % 2 else "AIDA", "synthetic_example": True,
        "content": content, "cta": content["cta"],
        "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."}


def write_doc(name, title, body, *, channels=None, targets=None, kind="guide", sources=None, synthetic=False):
    front = {"doc_id": "marketing." + name.removesuffix(".md"), "title": title, "language": "vi",
        "scope": "public", "channels": channels or ["facebook", "tiktok", "shopee"],
        "industries": ["fashion", "accessories", "household", "handmade_decor"],
        "objectives": ["introduce_product", "drive_sales", "promote_offer", "answer_questions"],
        "content_kind": kind, "synthetic_example": synthetic, "source_ids": sources or [],
        "updated_at": DATE, "version": VERSION, "tone": "friendly"}
    if targets:
        front["targets"] = targets
    (DIRECTORY / name).write_text("---\n" + json.dumps(front, ensure_ascii=False, indent=2) + "\n---\n\n# " + title + "\n\n" + body.strip() + "\n", encoding="utf-8")


def json_section(title, data):
    return f"## {title}\n\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n\n"


def build():
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    for channel, filename in (("tiktok", "04_tiktok_scripts.md"), ("facebook", "12_facebook_reels_scripts.md"), ("shopee", "13_shopee_video_scripts.md")):
        body = ""
        for i, case in enumerate(CASES, 1):
            content = make_video(case, channel).model_dump(mode="json")
            body += json_section(f"Mẫu {i}: {case['name']}", example(case, channel, i, content))
        write_doc(filename, f"Kịch bản video: {channel}", body, channels=[channel], targets=[TARGETS[channel]], kind="video_examples",
                  sources=["TT01", "TT02"] if channel == "tiktok" else ["SP02", "SP03"] if channel == "shopee" else [], synthetic=True)
    captions, listings = "", ""
    for i, case in enumerate(CASES, 1):
        hook, body, cta = case["caption"].split("\n\n")
        content = {"content_type": "caption", "angle": "Xem chi tiết để lựa chọn", "hook": hook,
                   "body": body, "cta": cta, "hashtags": [], "plain_text": case["caption"]}
        captions += json_section(f"Bài {i}: {case['name']}", example(case, "facebook", i, content))
        details = "\n".join(f"- {value}" for value in case["attrs"].values())
        listing = {"content_type": "listing", "angle": "Thông tin để lựa chọn", "title": case["listing"],
            "short_description": case["name"] + ". " + ", ".join(case["attrs"].values()) + ".",
            "highlights": list(case["attrs"].values()), "detailed_description": case["name"] + "\n" + details,
            "attributes": [{"fact_ref": "attributes." + key, "value": value} for key, value in case["attrs"].items()],
            "cta": "Xem thông tin và phân loại của sản phẩm trong shop.", "plain_text": ""}
        from src.schemas.marketing import Listing
        listing["plain_text"] = render_content(Listing.model_validate(listing))
        listings += json_section(f"Listing {i}: {case['name']}", example(case, "shopee", i, listing))
    write_doc("03_facebook_examples.md", "Bài Facebook nguyên bản", captions, channels=["facebook"], targets=[["facebook", "feed", "caption"]], kind="caption_examples", synthetic=True)
    write_doc("05_shopee_listings.md", "Listing Shopee nguyên bản", listings, channels=["shopee"], targets=[["shopee", "product_listing", "listing"]], kind="listing_examples", sources=["SP01"], synthetic=True)
    adaptations = ""
    for i, case in enumerate([CASES[0], CASES[2], CASES[3]], 1):
        data = {"example_id": f"adaptation_{i}", "synthetic_example": True,
            "input_facts": snapshot(case).model_dump(mode="json"),
            "audience": case["audience"], "objective": "introduce_product", "tone": "friendly", "framework": "FAB",
            "explanation": "TikTok mở bằng câu hỏi/thao tác và cắt vào chi tiết; Reels giữ hình và chữ để hiểu khi tắt âm; Shopee cho xem thông tin lựa chọn và CTA tìm sản phẩm trong shop, không giả định quyền gắn sản phẩm.",
            "scripts": [{"channel": c, "placement": TARGETS[c][1], "content_type": "video_script",
                         "content": make_video(case, c).model_dump(mode="json")} for c in TARGETS]}
        adaptations += json_section(f"Bộ {i}: {case['name']}", data)
    write_doc("15_cross_platform_video_adaptations.md", "Chuyển thể cùng facts theo ba placement", adaptations,
              targets=list(TARGETS.values()), kind="adaptation_examples", synthetic=True)
    write_guides()


def write_guides():
    write_doc("README.md", "Tri thức marketing Finora", """
## Mục lục và cách dùng
01: văn phong; 02: framework; 03: 8 caption; 04: 8 TikTok; 05: 8 listing;
06: 20 hook và 20 CTA; 07: 8 chiến lược; 08: 3 lịch 7 ngày; 09: trung thực và nền tảng;
10: 10 cặp sửa; 11: nguồn; 12: 8 Reels; 13: 8 Shopee Video; 14: quay/dựng;
15: 3 bộ chuyển thể, mỗi bộ có 3 kịch bản hoàn chỉnh cùng snapshot.
Mọi mẫu là nguyên bản giả lập, không gán cho thương hiệu thật, không có dữ liệu chứng minh hiệu quả chuyển đổi.
## Nạp, cập nhật và phân quyền
Chạy `python -m src.services.marketing.knowledge --dry-run` để kiểm tra offline;
bỏ `--dry-run` để embedding bằng provider đang cấu hình. Dùng Chroma namespace/collection riêng trong data/marketing_vectors.
Front matter là JSON trong dấu --- (JSON là tập con YAML); mỗi heading cấp 2 là một đơn vị trọn vẹn.
Giữ input facts, toàn bộ timeline và CTA dưới cùng heading. Không cắt ví dụ bằng số ký tự.
Không nhập dữ liệu shop vào scope public. CLI private cần directory riêng, --scope private --tenant-id --shop-id và front matter khớp.
Chỉ quản trị viên server chạy CLI; không có endpoint ingest công khai.
Chạy lại upsert theo hash, sửa/xóa sẽ bỏ chunk cũ đúng scope sau khi upsert thành công. Dùng đầy đủ directory cho một scope.
## Ranh giới facts
Ví dụ hướng dẫn cấu trúc, không cung cấp facts SKU thật. RAG không fine-tune model.
Khi sửa sources/rules, cập nhật version và updated_at theo lần kiểm tra thật; không tự đánh dấu nguồn đã xác minh.
Quy tắc bắt buộc còn nằm trong system prompt và validator, không phụ thuộc retrieval.
""")
    write_doc("01_voice_and_style.md", "Văn phong tự nhiên, rõ ý", """
## Quy tắc biên tập Finora
Xưng hô theo brand/audience, mặc định “bạn”; không gọi mọi khách là Gen Z. Nói điều người mua cần biết.
Một góc tiếp cận, hook cụ thể, lợi ích có cơ sở và một CTA. Đoạn ngắn, dòng trống, bullet khi cần.
Mặc định không emoji; chỉ dùng tối đa 2 nếu yêu cầu bật, không dùng làm bullet hoặc che điều kiện.
Hashtag ít và liên quan, chỉ khi bật. Không ALL CAPS, font Unicode trang trí, dấu chấm than liên tiếp.
Không lạm dụng “siêu phẩm”, “bùng nổ”, “đỉnh của chóp”, “chốt đơn ngay kẻo lỡ”.
Facebook standard hướng tới 60–120 đơn vị tách bởi khoảng trắng, short khoảng dưới 60; ít facts có thể ngắn hơn.
Đây là mục tiêu biên tập Finora, không phải giới hạn Facebook. Tiêu đề Shopee không emoji/hashtag/giá/khuyến mãi.
Ba phương án cần khác ý tưởng tình huống, chi tiết, FAQ; không chỉ đổi từ.
## Nên và tránh
Tránh: “SIÊU PHẨM ai cũng mê!!!” vì thiếu chi tiết và tự gán sự yêu thích.
Nên khi fact có hai ngăn: “Bạn thường chia đồ trong túi thế nào? Xem từng ngăn trước khi chọn.”
Tránh: “Mặc là tự tin ngay” vì hứa trải nghiệm không xác minh.
Nên: “Xem kiểu cổ và màu áo để cân nhắc theo cách phối của bạn.”
Mẫu là tổng hợp tự viết, không quote nguồn. Tham khảo nguyên tắc rõ ràng, hữu ích, phù hợp tình huống của Mailchimp.
""", sources=["MC02"])
    write_doc("02_copywriting_frameworks.md", "Chọn AIDA, PAS hoặc FAB", """
## AIDA
Tạo sự chú ý → thông tin đáng quan tâm → lý do cân nhắc → hành động. Dùng khi giới thiệu SKU cần dẫn vào một bước tiếp theo.
Ví dụ giả lập: fact túi hai ngăn. “Đồ nhỏ thường để lẫn ở đâu? Túi có hai ngăn để bạn chọn cách chia đồ. Xem ảnh từng ngăn trước khi chọn.”
Không phải mọi người mua đi qua các bước theo cùng thứ tự; không ép viết dài hoặc dựng bằng chứng xã hội.
## PAS
Nêu trở ngại thật → giải thích bất tiện cụ thể → đề xuất cách xử lý có cơ sở. Dùng cho FAQ/ngại chọn, không gây sợ hoặc dựng vấn đề.
Ví dụ giả lập: fact nắp rời. “Bạn quen nhấc nắp riêng khi lấy đồ? Xem thao tác mở hộp nắp rời để cân nhắc theo thói quen.”
Không nói đồ khác nguy hiểm/kém chất lượng khi không có chứng cứ. Không khuếch đại nỗi đau để thúc ép.
## FAB
Thuộc tính → ý nghĩa trực tiếp của thuộc tính → điều người mua có thể cân nhắc. Dùng cho listing hoặc demo chi tiết.
Ví dụ giả lập: fact dây túi điều chỉnh được. “Dây điều chỉnh được; bạn có thể xem cách thay đổi dây để chọn theo cách đeo.”
Không suy từ chất liệu sang công dụng chưa kiểm chứng. Không hiển thị nhãn framework trong plain_text.
Tóm tắt ý tưởng framework bằng lời Finora; ví dụ do Finora tự viết, không phải mẫu của nguồn.
""", sources=["HS01", "BF01"], synthetic=True)
    hooks = [
        ("Áo có thông tin cổ áo", "Bạn muốn xem rõ phần cổ trước khi chọn?"),
        ("Túi có ngăn đã xác nhận", "Bạn thường chia đồ trong túi thế nào?"),
        ("Khay trang trí bàn", "Góc nào trên bàn đang chờ một chiếc khay?"),
        ("Bình có bề mặt xác nhận", "Nhìn gần bề mặt bình sẽ thấy gì?"),
        ("Kẹp có cơ chế xác nhận", "Kẹp mở và khép như thế nào?"),
        ("Hộp có nắp rời", "Bạn quen dùng nắp rời hay nắp liền?"),
        ("Sổ có giấy xác nhận", "Bạn muốn xem trang giấy trước khi viết?"),
        ("Áo có khóa kéo", "Cùng xem thao tác kéo khóa thật chậm."),
        ("Có ảnh màu thật", "Màu này trông thế nào trong ảnh sản phẩm?"),
        ("Có bảng kích thước", "Trước khi chọn, bạn đã xem bảng kích thước chưa?"),
        ("Có phân loại", "Phân loại nào phù hợp với điều bạn đang tìm?"),
        ("Có đồ thật để demo", "Từ tổng thể đến cận cảnh, cùng xem sản phẩm."),
        ("Có hướng dẫn sử dụng", "Bắt đầu từ thao tác trong hướng dẫn nhé."),
        ("Có thông tin bao gồm trong bộ", "Trong bộ này có những gì?"),
        ("Có dữ liệu vật liệu", "Chất liệu là chi tiết bạn xem đầu tiên?"),
        ("Có FAQ thật", "Đây là câu hỏi shop cần giải thích rõ hơn."),
        ("Có nguồn mô tả chi tiết", "Một chi tiết nhỏ để bạn xem kỹ trước khi chọn."),
        ("Có sản phẩm trang trí", "Bạn hình dung sản phẩm ở vị trí nào?"),
        ("Có ảnh nhiều góc", "Đổi góc nhìn, xem thêm phần cạnh bên."),
        ("Có danh mục SKU thật", "Bạn đang tìm mẫu nào trong shop?"),
    ]
    ctas = ["Xem thông tin sản phẩm trong shop.", "Xem ảnh cận trước khi lựa chọn.", "Đọc bảng kích thước của sản phẩm.",
        "Chọn phân loại phù hợp với bạn.", "Xem từng ngăn của túi trong ảnh chi tiết.", "Xem thao tác mở nắp trong video.",
        "Đọc phần chất liệu shop đã cung cấp.", "Xem kiểu cổ áo trước khi chọn.", "Tìm SKU trong danh mục shop.",
        "Xem màu sản phẩm trong ảnh thật.", "Đối chiếu thông tin bộ sản phẩm.", "Đọc hướng dẫn sử dụng đã cung cấp.",
        "Xem cận phần khóa kéo.", "Xem bề mặt sản phẩm trong ảnh chi tiết.", "Cân nhắc vị trí đặt trước khi chọn.",
        "Xem trang giấy trong ảnh mở sổ.", "Đọc phần giải đáp của sản phẩm.", "Nhắn trang để hỏi thêm thông tin.",
        "Bình luận chi tiết bạn muốn được xem rõ.", "Xem sản phẩm gắn trong video sau khi shop xác nhận quyền gắn."]
    body = "## Hook có ngữ cảnh\n\n" + "\n".join(f"{i}. {context}: {copy}" for i, (context, copy) in enumerate(hooks, 1))
    body += "\n\n## CTA có điều kiện\n\n" + "\n".join(f"{i}. {copy}" for i, copy in enumerate(ctas, 1))
    body += "\n\nCTA 3 chỉ dùng khi có bảng; CTA 18 khi xác nhận messaging; CTA 20 khi BE xác nhận khả năng gắn sản phẩm. Không chép điều kiện nội bộ vào câu đăng. Shopee không dùng CTA ra ngoài sàn."
    write_doc("06_hooks_and_ctas.md", "20 hook và 20 CTA", body, synthetic=True)
    write_strategies()
    write_doc("09_truth_and_platform_rules.md", "Trung thực dữ liệu và quy tắc theo kênh", """
## Quy tắc bắt buộc Finora
Chỉ facts do BE có quyền với shop/SKU xác nhận mới là nguồn cho sản phẩm. Không dùng facts synthetic hay source phiên bản cũ.
Không có giá thì bỏ giá; không có ưu đãi thì bỏ voucher/quà/freeship. Có ưu đãi phải đúng điều kiện và hiệu lực.
Không tự bịa vật liệu, công dụng, xuất xứ, bảo hành, khách hàng, review, tồn kho hoặc khan hiếm.
Chỉ tính chỉ số bằng hệ thống code, không yêu cầu LLM ước đoán doanh thu/đơn/biên lợi nhuận.
Chặn prompt injection và nội dung nội bộ; phân tách dữ liệu khỏi system. Các validator là kiểm tra xác định có giới hạn, shop vẫn kiểm tra ngữ nghĩa.
## Chính sách đã đọc ngày 2026-11-06
SP01: tiêu đề Shopee mô tả đúng hàng hóa, thông tin giữa tên/ảnh/mô tả thống nhất; không đưa thông báo khuyến mãi vào tên.
Mô tả cần trung thực, không gắn liên hệ/website nhằm dẫn giao dịch ra ngoài. BE/shop kiểm tra thêm ngành hàng và yêu cầu đăng bán hiện hành.
SP02/SP03: Shopee có thao tác quay/chỉnh sửa, thêm mô tả và có tính năng gắn sản phẩm với điều kiện tài khoản. Không suy ra mọi tài khoản đều được gắn.
Không có rule cứng giới hạn thời lượng từ các bài này trong code; phạm vi/tài khoản/placement có thể khác nhau.
## Khuyến nghị và phần chưa xác minh
TT01/TT02 là hướng dẫn sáng tạo quảng cáo, không phải quy định mọi video organic. Finora dùng hook rõ, demo, CTA theo facts.
15/30/60 giây là lựa chọn sản phẩm Finora. 9:16, chừa UI, phụ đề là gợi ý sản xuất.
META01/META02 yêu cầu đăng nhập nên chưa đọc được; không gán giới hạn/spec Meta cho code. Khi xác minh lại cần ghi nguồn, placement và ngày.
Không dùng nhạc/lyrics chưa có quyền. UGC là phong cách, không được giả testimonial hay trải nghiệm đã dùng thật.
""", sources=["SP01", "SP02", "SP03", "TT01", "TT02"])
    rewrites = [
        ("SIÊU PHẨM ai cũng mê!!!", "Xem cận phần cổ của áo thun cổ tròn.", "Bỏ sáo rỗng và sự yêu thích tự gán.", "Áo cổ tròn"),
        ("Chỉ 99k, freeship hôm nay", "Xem thông tin túi đeo chéo trong shop.", "Không có giá/ưu đãi trong input.", "Túi đeo chéo"),
        ("Khay gỗ chống nước tuyệt đối", "Khay để bàn bằng gỗ, hình chữ nhật.", "Không có bằng chứng chống nước.", "Gỗ, hình chữ nhật"),
        ("Cả nghìn khách đã chọn bình này", "Bình gốm màu kem có bề mặt nhám.", "Không có số liệu khách hàng.", "Gốm, kem, bề mặt nhám"),
        ("Kẹp tóc bền nhất thị trường", "Xem thao tác mở kẹp tóc dạng càng cua.", "Bỏ so sánh không kiểm chứng.", "Kẹp dạng càng cua"),
        ("Hộp giúp bàn gọn ngay lập tức", "Hộp nhựa trong suốt có nắp rời.", "Chỉ giữ thuộc tính, không hứa kết quả.", "Nhựa, trong suốt, nắp rời"),
        ("Sổ truyền cảm hứng mỗi ngày", "Sổ bìa vải màu xanh, giấy kẻ ngang.", "Bỏ hứa trải nghiệm, thêm thông tin thật.", "Bìa vải, xanh, kẻ ngang"),
        ("Áo chống lạnh mọi thời tiết", "Áo khoác màu xám có mũ và khóa kéo.", "Không có bằng chứng công dụng.", "Xám, mũ, khóa kéo"),
        ("Mua trên Shopee rồi nhắn Zalo trả tiền", "Xem phân loại và thông tin sản phẩm trong shop.", "Giữ thao tác trong sàn.", "Listing Shopee"),
        ("Mình dùng một tháng rồi, tốt lắm", "Cùng xem thao tác mở nắp hộp.", "UGC không hợp thức hóa trải nghiệm giả.", "Hộp nắp rời"),
    ]
    body = "".join(json_section(f"Sửa {i}", {"example_id": f"rewrite_{i}", "synthetic_example": True,
        "channel": "shopee" if i == 9 else "facebook", "industry": "general", "audience": "khách đang cân nhắc",
        "objective": "introduce_product", "tone": "friendly", "framework": "FAB", "input_facts": facts,
        "before": before, "after": after, "cta": "Xem thông tin sản phẩm trong shop.", "reason": reason})
        for i, (before, after, reason, facts) in enumerate(rewrites, 1))
    write_doc("10_before_after_rewrites.md", "10 cặp sửa bài", body, synthetic=True)
    write_sources()
    write_doc("14_short_video_production_guide.md", "Quay và dựng video bằng điện thoại", """
## Chuẩn bị một buổi quay tối giản
Giả định một người và điện thoại, sản phẩm thật, mặt bàn cạnh nguồn sáng sẵn có; hỏi shop nếu thiếu sản phẩm/đạo cụ.
Chọn một chi tiết có fact; viết hook, thao tác demo và một CTA. Tự thử thao tác trước khi quay, không diễn lại testimonial.
Lau ống kính, kiểm tra lấy nét, quay một đoạn rồi xem lại. Không giả định shop có studio hoặc nhiều diễn viên.
## Chia cảnh theo thời lượng
15/30/60 giây là lựa chọn Finora. Timeline từ 0 đến đúng tổng, không hở/chồng. Ít cảnh nhưng quay được là đủ.
Với 30 giây có thể dành đầu video cho hook, phần giữa demo, cuối CTA; không ép mọi video cùng số giây mỗi cảnh.
Ước lượng lời nói theo khoảng thời gian có thể đọc, chừa nhịp tay thao tác; chỉ thu âm thực mới biết thời lượng chính xác.
## Chế độ quay và dựng
on_camera: người dẫn nói trong cảnh. hands_only: chỉ tay/sản phẩm, có thể voiceover. voiceover: giọng ngoài cảnh, không ép lộ mặt.
text_only: không dialogue/voiceover, dành thời gian để đọc chữ. Không lặp nguyên lời ở cả dialogue và voiceover.
Quay dọc 9:16 là mặc định gợi ý Finora. Chữ ngắn dễ đọc, chừa UI, phụ đề đồng bộ. Reels cần dễ hiểu cả khi tắt tiếng.
Dựng cắt gọn, tránh hiệu ứng che chi tiết; kiểm tra màu không làm sai sản phẩm. CTA gắn sản phẩm chỉ sau khi shop xác nhận tính năng.
## Âm thanh và kiểm tra trước dùng
Dùng âm thanh thao tác/giọng thật hoặc nhạc đã xác nhận quyền thương mại. Không tự chọn nhạc trend hoặc chèn lyrics.
So timeline, lời thoại, facts và link với snapshot. Shopee không giao dịch ngoài sàn. Xuất thử để đọc chữ trên điện thoại.
Các gợi ý biên tập không bảo đảm lượt xem/chuyển đổi và không thay thế spec chính thức của từng placement.
""", targets=list(TARGETS.values()), sources=["TT01", "TT02", "SP03"])


def write_strategies():
    strategies = [
        ("Hướng dẫn đọc thông tin SKU", "Khách chưa hiểu cách chọn", "Có bảng/thuộc tính được xác nhận", "Chọn theo nhu cầu từ dữ liệu rõ ràng", ["Chọn một câu hỏi cách chọn.", "Chụp thông tin/bảng thật.", "Viết hướng dẫn ngắn và CTA xem chi tiết.", "Ghi lại câu hỏi còn vướng."], "lượt mở chi tiết, câu hỏi cách chọn", "So hướng dẫn bằng ảnh với hướng dẫn bằng chữ"),
        ("Demo một tình huống", "Ảnh tổng thể chưa cho thấy thao tác", "Có sản phẩm và thao tác phù hợp", "Cho thấy chi tiết trước quyết định", ["Chọn một thao tác thật.", "Quay cận bằng điện thoại.", "Gắn chữ đúng facts.", "Đăng bản đã duyệt và ghi nhận phản hồi."], "thời gian xem, lượt vào sản phẩm", "Thay hook, giữ demo và CTA"),
        ("FAQ tháo gỡ trở ngại", "Khách hỏi lặp về chi tiết", "Có câu hỏi thật đã ẩn dữ liệu cá nhân", "Giải thích một điều còn chưa rõ", ["Tổng hợp một câu hỏi không lộ PII.", "Xác nhận câu trả lời với shop.", "Viết câu trả lời kèm hình chi tiết.", "Đo số câu hỏi chưa giải quyết."], "câu hỏi tiếp diễn, lượt xem chi tiết", "Thử câu hỏi ở hook và ở ảnh bìa"),
        ("Chuỗi giới thiệu từng SKU", "Nhiều sản phẩm dễ bị lẫn", "Có danh mục và facts riêng từng SKU", "Mỗi bài giúp hiểu một sản phẩm", ["Chọn nhóm SKU có dữ liệu đầy đủ.", "Viết mỗi SKU một góc riêng.", "Rà giá/thuộc tính từng sản phẩm.", "Đăng theo lịch nguồn lực cho phép."], "lượt vào từng SKU, bản nháp được duyệt", "Đổi thứ tự SKU, giữ tiêu chí nội dung"),
        ("Giới thiệu combo có thật", "Khách chưa biết thành phần bộ", "Shop thực sự bán combo, có thành phần và giá xác nhận", "Nói rõ bộ gồm gì, không tự cộng lợi ích", ["Xác minh mã combo và thành phần.", "Chụp đầy đủ món trong bộ.", "Nêu điều kiện/giá đã xác nhận.", "Theo dõi câu hỏi về thành phần."], "lượt xem combo, câu hỏi thành phần", "So ảnh toàn bộ với ảnh tách thành phần"),
        ("Nội dung khách đã cho phép", "Thiếu góc nhìn sử dụng có nguồn", "Có đồng ý sử dụng và nội dung thật; không tự chế review", "Dẫn lời đúng phạm vi khách cho phép", ["Lưu bằng chứng đồng ý ở BE.", "Ẩn thông tin cá nhân theo quyền.", "Giữ đúng lời thật và bối cảnh.", "Cho shop duyệt trước sử dụng."], "phản hồi có nội dung, yêu cầu gỡ", "So nội dung demo của shop với phản hồi đã được phép, không đổi lời khách"),
        ("Hướng dẫn sau mua và mua lại", "Khách chưa biết cách dùng/chọn tiếp", "Có hướng dẫn xác nhận, kênh liên hệ được phép, khách đồng ý nhận", "Giúp dùng đúng trước khi đề nghị mua tiếp", ["Chọn hướng dẫn liên quan SKU đã mua.", "Soạn tin ngắn có ích.", "Chỉ gửi qua kênh/quyền được phép.", "Ghi nhận từ chối và dừng gửi."], "phản hồi hữu ích, tỷ lệ từ chối, mua lại có gắn nguồn", "Đổi chủ đề hướng dẫn, không tăng tần suất tùy tiện"),
        ("Thử hai góc tiếp cận", "Chưa biết khách cần tình huống hay chi tiết", "Có baseline và đủ năng lực duy trì đo", "Tìm góc có ích bằng dữ liệu", ["Chọn một SKU và một chỉ số chính.", "Giữ ảnh/CTA, chỉ đổi góc hook.", "Đo baseline rồi thử trong điều kiện tương đương.", "Xem độ bất định trước quyết định."], "chỉ số chính đã chọn, chi phí/nỗ lực, phân phối tiếp cận", "Không kết luận từ vài view; không bịa cỡ mẫu hoặc ngưỡng thành công"),
    ]
    body = ""
    for i, (name, problem, condition, message, actions, kpis, experiment) in enumerate(strategies, 1):
        body += json_section(name, {"strategy_id": f"strategy_{i}", "problem": problem,
            "suitable_when": problem + " và shop có nguồn lực duy trì nội dung", "conditions": [condition],
            "message": message, "channels": ["facebook", "tiktok", "shopee"], "actions": actions,
            "resources": ["người phụ trách nội dung", "điện thoại", "dữ liệu SKU đã xác nhận"],
            "assumptions": ["Chưa biết baseline; cần đo trước khi đặt mục tiêu."],
            "kpis_to_measure": kpis.split(", "), "experiment": experiment,
            "stop_or_adjust_when": "Điều chỉnh khi phản hồi cho thấy hiểu sai, điều kiện đầu vào đổi hoặc công sức vượt nguồn lực; dừng nếu hết quyền dùng dữ liệu/ưu đãi. KPI là đề xuất đo, không phải kết quả."})
    write_doc("07_marketing_strategies.md", "8 chiến lược thực thi cho shop nhỏ", body, kind="strategies", sources=["HS02", "MC01"])
    plays = [
        ("Giới thiệu sản phẩm", ["Tổng thể SKU", "Cận chi tiết", "Tình huống dùng", "FAQ về lựa chọn", "Xem phân loại", "Ảnh nhiều góc", "Tổng hợp thông tin"]),
        ("Giải đáp trở ngại mua", ["Thu câu hỏi thật", "Trả lời cấu tạo", "Demo thao tác", "Giải thích phân loại", "Đối chiếu bảng thông tin", "FAQ tiếp diễn", "Tổng hợp câu trả lời"]),
        ("Ưu đãi đã xác nhận", ["Kiểm tra điều kiện và hiệu lực", "Giới thiệu sản phẩm áp dụng", "Giải thích điều kiện", "Demo SKU", "FAQ ưu đãi", "Rà thời hạn hiện tại", "Tổng kết và dừng khi hết hạn"]),
    ]
    body = ""
    for i, (goal, topics) in enumerate(plays, 1):
        body += json_section(goal, {"playbook_id": f"playbook_{i}", "synthetic_example": True, "objective": goal,
            "conditions": "Dùng facts/snapshot đúng SKU; lịch ưu đãi chỉ khi BE xác nhận điều kiện và còn hiệu lực.",
            "days": [{"day": d, "topic": topic, "channel": ["facebook", "tiktok", "shopee"][(d-1) % 3],
                "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
                "reference": None, "status": "needs_generation"} for d, topic in enumerate(topics, 1)],
            "measurement": "Ghi baseline lượt xem chi tiết/câu hỏi; không coi kế hoạch là đã tạo hoặc đăng nội dung."})
    write_doc("08_seven_day_playbooks.md", "3 lịch đề xuất đủ 7 ngày", body, kind="playbooks", synthetic=True)


def write_sources():
    rows = [
        ("TT01", "TikTok", "https://ads.tiktok.com/business/en-US/creative-codes", "verified", "Học cấu trúc hook/body/close và cách thể hiện theo kênh. Hướng dẫn ads, không áp thành luật video organic.", "04,09,14"),
        ("TT02", "TikTok", "https://ads.tiktok.com/resources/help/article/creative-best-practices?lang=en", "verified", "Hook sớm, sản phẩm rõ và CTA; cần thử nghiệm. Gợi ý ads, không hứa hiệu quả.", "04,09,14"),
        ("HS01", "HubSpot", "https://blog.hubspot.com/marketing/aida-model", "verified", "AIDA là cách tổ chức sự chú ý, quan tâm, cân nhắc và hành động, không bảo đảm chuyển đổi.", "02"),
        ("HS02", "HubSpot", "https://blog.hubspot.com/marketing/content-marketing-plan", "verified", "Chọn mục tiêu trước, phân bổ nội dung theo đối tượng và nguồn lực, đặt chỉ số để đánh giá.", "07"),
        ("SP01", "Shopee", "https://help.shopee.vn/portal/4/article/77246", "verified", "Đã đọc phần tên/mô tả: đúng hàng hóa, thống nhất thông tin, trung thực; tránh khuyến mãi trong tên và dẫn giao dịch ngoài sàn. Không bao phủ mọi điều kiện ngành hàng.", "05,09"),
        ("SP02", "Shopee", "https://help.shopee.vn/portal/10/article/153132", "verified", "Mô tả Shopee Video và quy trình; quyền gắn sản phẩm có điều kiện. BE xác nhận khả năng tài khoản, không suy từ bài chung.", "09,13"),
        ("SP03", "Shopee", "https://help.shopee.vn/portal/4/article/128167", "verified", "Có quay, chỉnh sửa, lồng tiếng, văn bản và mô tả. Bài có số giây trong phạm vi riêng; code dùng 15/30/60 như lựa chọn Finora, không hardcode thành trần nền tảng.", "09,13,14"),
        ("BF01", "Buffer", "https://buffer.com/resources/copywriting-formulas/", "verified", "Tham khảo AIDA/PAS/FAB, chọn cấu trúc phù hợp nội dung; không dùng clickbait hoặc hứa kết quả.", "02"),
        ("MC01", "Mailchimp", "https://mailchimp.com/resources/marketing-strategies-for-small-businesses/", "verified", "Chọn đối tượng, mục tiêu, kênh vừa nguồn lực, theo dõi và điều chỉnh. Chiến lược thực thi trong bộ này do Finora tự biên soạn.", "07"),
        ("MC02", "Mailchimp", "https://styleguide.mailchimp.com/writing-principles/", "verified", "Nguyên tắc rõ, hữu ích, thân thiện, phù hợp và trung thực. Ví dụ tiếng Việt là bản tự viết.", "01"),
        ("META01", "Meta", "https://www.facebook.com/business/m/reels-ads-creative-essentials", "unverified", "URL chuyển tới đăng nhập/thông báo chặn; chưa đọc được nội dung, không dùng làm nguồn rule cứng.", "không áp dụng"),
        ("META02", "Meta", "https://www.facebook.com/business/ads-guide/update/video/facebook-facebook-reels", "unverified", "URL chuyển tới đăng nhập/thông báo chặn; chưa xác minh spec theo placement. Hướng dẫn Reels trong bộ là đề xuất Finora.", "không áp dụng"),
    ]
    body = "## Phương pháp\n\nĐã mở và đọc nội dung nguồn trong phiên ngày 2026-11-06. Verified nghĩa truy cập/đọc được, không chứng nhận chính sách còn đúng cho mọi tài khoản. Hai URL Meta chỉ kiểm tra truy cập, chưa đọc được. Không vượt chặn.\n\n"
    for ident, publisher, url, status, learning, applies in rows:
        body += f"## {ident}\n\n- Publisher: {publisher}\n- URL: {url}\n- Checked at: {DATE}\n- Status: {status}\n- Nội dung học: {learning}\n- Áp dụng: {applies}\n\n"
    write_doc("11_sources.md", "Nguồn và trạng thái xác minh", body, kind="source_register")


if __name__ == "__main__":
    build()
    print("Created 16 Markdown documents; 8 captions, 8 listings, 24 video scripts, 3 adaptation sets (9 scripts).")
