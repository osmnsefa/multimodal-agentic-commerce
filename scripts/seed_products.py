import asyncio
import io
import sys
import uuid
from decimal import Decimal
from pathlib import Path
from PIL import Image, ImageDraw

# Ensure utf-8 stdout on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "services" / "backend"))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.product import Product
from app.services.clip_service import clip_service

def generate_synthetic_product_image(title: str, category: str, bg_color: tuple) -> bytes:
    """
    Creates an in-memory representative RGB image for visual CLIP feature encoding.
    """
    img = Image.new("RGB", (256, 256), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Decorative geometric pattern representing product shape
    draw.rounded_rectangle([32, 32, 224, 224], radius=24, outline=(255, 255, 255), width=4)
    draw.ellipse([80, 80, 176, 176], fill=(255, 255, 255), outline=(230, 230, 230), width=2)

    # Category and title watermark text
    draw.text((45, 190), f"[{category.upper()}]", fill=(255, 255, 255))
    draw.text((45, 205), title[:22], fill=(240, 240, 240))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

SEED_PRODUCTS = [
    {
        "sku": "AEGIS-CLOTH-001",
        "title": "Waterproof Mountain Trail Hardshell Jacket",
        "description": "3-layer breathable stormproof jacket engineered for alpine conditions and rugged hiking.",
        "category": "Clothing",
        "price": Decimal("189.99"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1544923246-77307dd654cb",
        "attributes": {"color": "Alpine Blue", "waterproof_rating": "28000mm", "gender": "Unisex"},
        "bg_color": (30, 75, 135)
    },
    {
        "sku": "AEGIS-CLOTH-002",
        "title": "Slim Fit Japanese Selvedge Indigo Denim Jeans",
        "description": "Authentic 14oz redline selvedge denim crafted from organic cotton with custom copper rivets.",
        "category": "Clothing",
        "price": Decimal("139.50"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1542272604-780c96856592",
        "attributes": {"color": "Dark Indigo", "material": "100% Selvedge Cotton", "fit": "Slim"},
        "bg_color": (25, 45, 80)
    },
    {
        "sku": "AEGIS-CLOTH-003",
        "title": "Merino Wool Thermal Outdoor Crewneck Sweater",
        "description": "Extra-fine 260gsm merino wool sweater providing superior natural insulation and odor resistance.",
        "category": "Clothing",
        "price": Decimal("119.00"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633",
        "attributes": {"color": "Charcoal Grey", "material": "100% Merino Wool", "breathable": True},
        "bg_color": (65, 65, 70)
    },
    {
        "sku": "AEGIS-TECH-001",
        "title": "Aegis Pro Active Noise-Canceling Wireless Headphones",
        "description": "Flagship wireless over-ear headphones with 40mm beryllium drivers, hybrid ANC, and 45h battery life.",
        "category": "Electronics",
        "price": Decimal("349.99"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
        "attributes": {"battery_hours": 45, "bluetooth": "5.3", "has_anc": True, "driver": "40mm"},
        "bg_color": (20, 20, 25)
    },
    {
        "sku": "AEGIS-TECH-002",
        "title": "Ultra-Slim 27-inch 4K UHD IPS Designer Monitor",
        "description": "Studio-grade 4K monitor featuring 99% DCI-P3 color accuracy, HDR400, and 90W USB-C Power Delivery.",
        "category": "Electronics",
        "price": Decimal("499.00"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf",
        "attributes": {"resolution": "3840x2160", "refresh_rate": "144Hz", "usb_c_pd": "90W"},
        "bg_color": (40, 45, 55)
    },
    {
        "sku": "AEGIS-TECH-003",
        "title": "Ergonomic Custom Mechanical Wireless Keyboard",
        "description": "Gasket-mounted 75% mechanical keyboard with factory-lubed linear switches and hot-swappable PCB.",
        "category": "Electronics",
        "price": Decimal("169.95"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3",
        "attributes": {"layout": "75%", "switch": "Linear Oil King", "wireless": True, "rgb": True},
        "bg_color": (80, 50, 110)
    },
    {
        "sku": "AEGIS-HOME-001",
        "title": "Minimalist Nordic Solid Oak Coffee Table",
        "description": "Handcrafted Scandinavian coffee table made of sustainably sourced white oak and tempered glass.",
        "category": "Home & Living",
        "price": Decimal("279.00"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88",
        "attributes": {"wood": "White Oak", "finish": "Matte Lacquer", "dimensions": "100x60x45cm"},
        "bg_color": (160, 120, 80)
    },
    {
        "sku": "AEGIS-HOME-002",
        "title": "Ultrasonic Aroma Diffuser with Ambient Warm Light",
        "description": "Quiet essential oil diffuser with 500ml water tank, whisper-quiet ultrasonic atomization, and LED lighting.",
        "category": "Home & Living",
        "price": Decimal("59.90"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108",
        "attributes": {"capacity_ml": 500, "timer": ["1h", "3h", "6h"], "auto_shutoff": True},
        "bg_color": (180, 150, 130)
    },
    {
        "sku": "AEGIS-HOME-003",
        "title": "Smart LiDAR Laser Robot Vacuum and Mop Cleaner",
        "description": "Autonomous smart cleaner with 5000Pa suction power, 3D obstacle avoidance, and auto-emptying station.",
        "category": "Home & Living",
        "price": Decimal("429.99"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1518640467707-6811f4a6ab73",
        "attributes": {"suction_pa": 5000, "battery_mah": 5200, "app_control": True},
        "bg_color": (210, 215, 220)
    },
    {
        "sku": "AEGIS-SPORT-001",
        "title": "Carbon Fiber Lightweight Trail Running Shoes",
        "description": "Ultra-responsive mountain trail running shoes equipped with embedded carbon plate and Vibram Megagrip.",
        "category": "Sports & Outdoors",
        "price": Decimal("179.95"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "attributes": {"plate": "Carbon Fiber", "drop_mm": 6, "weight_g": 240, "outsole": "Vibram"},
        "bg_color": (180, 40, 40)
    },
    {
        "sku": "AEGIS-SPORT-002",
        "title": "Aero Road Cycling Helmet with MIPS Protection",
        "description": "Wind-tunnel tested aerodynamic road helmet featuring integrated MIPS rotational impact protection.",
        "category": "Sports & Outdoors",
        "price": Decimal("199.00"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1559348349-86f1f65817fe",
        "attributes": {"safety": "MIPS Air", "vents": 18, "weight_g": 220},
        "bg_color": (20, 140, 100)
    },
    {
        "sku": "AEGIS-SPORT-003",
        "title": "Insulated Stainless Steel 1-Liter Outdoor Flask",
        "description": "Double-wall vacuum insulated bottle keeping liquids icy cold for 24 hours or piping hot for 12 hours.",
        "category": "Sports & Outdoors",
        "price": Decimal("39.99"),
        "currency": "USD",
        "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8",
        "attributes": {"volume_l": 1.0, "material": "18/8 Stainless Steel", "bpa_free": True},
        "bg_color": (50, 110, 120)
    }
]

async def seed_products():
    print("=" * 70)
    print("AegisCommerce: Seeding Products with CLIP Multimodal Embeddings")
    print("=" * 70)

    async with AsyncSessionLocal() as session:
        for idx, item in enumerate(SEED_PRODUCTS, start=1):
            sku = item["sku"]
            title = item["title"]
            desc = item["description"]
            cat = item["category"]

            print(f"[{idx}/{len(SEED_PRODUCTS)}] Processing '{title}' ({sku})...")

            # 1. Generate visual embedding via synthetic representative product image
            image_bytes = generate_synthetic_product_image(title, cat, item["bg_color"])
            image_emb = clip_service.get_image_embedding(image_bytes)

            # 2. Generate textual embedding
            full_text = f"{title}. {desc}. Category: {cat}"
            text_emb = clip_service.get_text_embedding(full_text)

            # Check if product with this SKU already exists
            stmt = select(Product).where(Product.sku == sku)
            existing = (await session.execute(stmt)).scalar_one_or_none()

            if existing:
                existing.title = title
                existing.description = desc
                existing.category = cat
                existing.price = item["price"]
                existing.currency = item["currency"]
                existing.image_url = item["image_url"]
                existing.attributes = item["attributes"]
                existing.image_embedding = image_emb
                existing.text_embedding = text_emb
                existing.status = "published"
                print(f"   Updated existing product: {sku}")
            else:
                new_product = Product(
                    id=uuid.uuid4(),
                    sku=sku,
                    title=title,
                    description=desc,
                    category=cat,
                    price=item["price"],
                    currency=item["currency"],
                    image_url=item["image_url"],
                    attributes=item["attributes"],
                    image_embedding=image_emb,
                    text_embedding=text_emb,
                    status="published"
                )
                session.add(new_product)
                print(f"   Created new product: {sku}")

        await session.commit()
        print("=" * 70)
        print(f"Successfully seeded {len(SEED_PRODUCTS)} products with 512-dim CLIP embeddings!")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(seed_products())
