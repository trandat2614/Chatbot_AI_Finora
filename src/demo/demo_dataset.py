"""Immutable sample amounts with rolling Vietnam calendar labels."""
from __future__ import annotations

from datetime import date, timedelta


def build_demo_dataset(today: date) -> str:
    """Render the approved Demo Store dataset; only the dates vary."""
    amounts = ("18,5", "21,2", "15,8", "19,4", "22,6", "24,1", "20,3")
    days = []
    for offset, amount in zip(range(6, -1, -1), amounts):
        label = (today - timedelta(days=offset)).isoformat()
        suffix = " (hôm qua)" if offset == 1 else " (hôm nay, tính đến hiện tại)" if offset == 0 else ""
        days.append(f"- {label}{suffix}: {amount} triệu")
    start = (today - timedelta(days=29)).isoformat()
    end = today.isoformat()
    previous_start = (today - timedelta(days=59)).isoformat()
    previous_end = (today - timedelta(days=30)).isoformat()
    revenue_lines = "\n".join(days)
    return f"""[Doanh thu 7 ngày gần nhất]
{revenue_lines}
=> Tổng 7 ngày: 141,9 triệu (7 ngày trước đó, {(today - timedelta(days=13)).isoformat()} đến {(today - timedelta(days=7)).isoformat()}: 128,7 triệu, tăng 10,3%)

[Doanh thu 30 ngày gần nhất: {start} đến {end}]
586,4 triệu | 30 ngày trước đó ({previous_start} đến {previous_end}): 541,2 triệu => tăng 8,4%

[Đơn hàng 30 ngày gần nhất]
- Tổng đơn: 1.248 | AOV: ~470.000đ
- Hoàn thành: 1.062 | Đang giao: 96 | Chờ xác nhận: 48 | Huỷ/hoàn: 42 (3,4%)

[Top 5 sản phẩm theo doanh thu, 30 ngày gần nhất]
1. Áo thun Basic: 98,2 triệu (412 cái)
2. Giày sneaker Urban: 87,5 triệu (146 đôi)
3. Balo Travel Pro: 64,8 triệu (118 cái)
4. Áo khoác Windy: 59,3 triệu (73 cái)
5. Quần jeans Slim: 52,1 triệu (97 cái)

[Doanh thu theo kênh bán] Website 38% | Shopee 27% | TikTok Shop 20% | Cửa hàng 15%

[Khách hàng] Tổng: 3.820 | Khách mới (30 ngày): 312 | Tỷ lệ khách quay lại: 34%

[Tồn kho cần chú ý] Giày sneaker Urban size 42: còn 5 đôi | Balo Travel Pro màu đen: còn 8 cái

[Chi phí & lợi nhuận, 30 ngày gần nhất]
- Doanh thu: 586,4 triệu | Giá vốn (55%): 322,5 triệu => Lợi nhuận gộp: 263,9 triệu (biên gộp 45%)
- Quảng cáo: 82,1 triệu (14% doanh thu) | Phí sàn & cổng thanh toán: 24,8 triệu
- Vận chuyển: 41,2 triệu | Nhân sự & mặt bằng: 78,0 triệu
- Lợi nhuận ròng: 37,8 triệu (biên ròng 6,4%)

[Quảng cáo, 30 ngày gần nhất]
- Meta Ads: chi 38,5 triệu, ROAS 5,2 | TikTok Ads: chi 24,6 triệu, ROAS 6,1 | Shopee Ads: chi 19,0 triệu, ROAS 9,8
- ROAS tổng hợp (toàn bộ doanh thu / toàn bộ chi phí quảng cáo): 7,1. ROAS theo kênh tính trên doanh thu quy về chính kênh đó nên không cộng thẳng ra 7,1.
- CAC: ~263.000đ | LTV 12 tháng (theo lợi nhuận gộp): ~540.000đ => LTV/CAC ≈ 2,1

[Website, 30 ngày gần nhất]
- Lượt truy cập: 21.600 | Thêm vào giỏ: 8,5% | Bỏ giỏ hàng: 71% | Tỷ lệ chuyển đổi: 2,2% (~475 đơn)
- Nguồn truy cập: Quảng cáo trả phí 42% | Tìm kiếm tự nhiên 23% | Mạng xã hội 20% | Trực tiếp/Email 15%
"""
