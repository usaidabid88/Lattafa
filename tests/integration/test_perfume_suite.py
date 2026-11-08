"""
PERFUME SUITE VERIFICATION TEST SCRIPT
Tests the domain transformation against online_shop_perfume_test.
Validates:
- 100 genuine perfumes present in product_perfume_details and v_perfume_catalog
- 17 mandatory fragrances with complete olfactory pyramids
- All 5 featured collection hubs (/collections, /collection/<slug>)
- Gender classification hubs (/men, /women, /unisex)
- Discovery hubs (/bestsellers, /new-arrivals)
- Faceted filtering & sorting
- Product detail pages with Olfactory Pyramid display
"""

import os
import sys
import unittest
import pymysql

os.environ['TEST_DB_NAME'] = 'online_shop_perfume_test'
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.app import app

class TestPerfumeTransformation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['DB_NAME'] = 'online_shop_perfume_test'
        cls.client = app.test_client()

    def test_01_database_count(self):
        """Verify exactly 100 perfumes in product_perfume_details and view."""
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '090078601'),
            database='online_shop_perfume_test',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM product_perfume_details")
            res = cur.fetchone()
            self.assertEqual(res['total'], 100, f"Expected 100 perfumes, found {res['total']}")

            cur.execute("SELECT COUNT(*) AS total FROM v_perfume_catalog WHERE concentration IS NOT NULL")
            v_res = cur.fetchone()
            self.assertEqual(v_res['total'], 100)
        conn.close()

    def test_02_all_17_mandatory_fragrances_present(self):
        """Verify presence of the 17 mandatory perfumes specified in requirements."""
        mandatory_names = [
            "Khamrah", "Asad", "Yara", "Yara Candy", "Eclaire",
            "Angham", "Khamrah Dukhan", "Teriaq", "Badee Al Oud Noble Blush",
            "His Confession", "Victoria", "The Kingdom Men", "Liam Grey",
            "Asad Zanzibar", "Atheeri", "Art Of Universe", "Art Of Nature II"
        ]
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '090078601'),
            database='online_shop_perfume_test',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cur:
            for name in mandatory_names:
                cur.execute("""
                    SELECT p.product_id, p.name, ppd.top_notes, ppd.heart_notes, ppd.base_notes,
                           ppd.concentration, ppd.bottle_size, ppd.collection_name
                    FROM products p
                    JOIN product_perfume_details ppd ON p.product_id = ppd.product_id
                    WHERE p.name LIKE %s
                """, (f"%{name}%",))
                row = cur.fetchone()
                self.assertIsNotNone(row, f"Mandatory fragrance '{name}' missing from catalog!")
                self.assertTrue(bool(row['top_notes']), f"{name} has empty top notes")
                self.assertTrue(bool(row['heart_notes']), f"{name} has empty heart notes")
                self.assertTrue(bool(row['base_notes']), f"{name} has empty base notes")
                self.assertTrue(bool(row['bottle_size']), f"{name} has empty bottle size")
        conn.close()

    def test_03_homepage_sections(self):
        """Verify homepage renders all luxury sections."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        # Section checks
        self.assertIn("A Fragrance That Defines Your Presence", html)
        self.assertIn("Featured Fragrance Houses", html)
        self.assertIn("Our Best Sellers", html)
        self.assertIn("Shop by Category", html)
        self.assertIn("New Fragrance Releases", html)
        self.assertIn("The Art of Arabian Haute Parfumerie", html)
        self.assertIn("The Lattafa Pride & Gift Treasury", html)

    def test_04_collections_hubs(self):
        """Verify collections directory and specific collection landing pages."""
        res = self.client.get('/collections')
        self.assertEqual(res.status_code, 200)
        self.assertIn("Our Fragrance Collections", res.data.decode('utf-8'))

        collections_to_test = [
            'khamrah-collection',
            'asad-collection',
            'yara-collection',
            'badee-al-oud',
            'lattafa-pride'
        ]
        for slug in collections_to_test:
            res_col = self.client.get(f'/collection/{slug}')
            self.assertEqual(res_col.status_code, 200, f"Failed GET /collection/{slug}")
            self.assertIn("Collection", res_col.data.decode('utf-8'))

    def test_05_gender_and_curation_routes(self):
        """Verify gender landing pages and discovery routes."""
        routes = ['/men', '/women', '/unisex', '/bestsellers', '/new-arrivals']
        for r in routes:
            res = self.client.get(r, follow_redirects=True)
            self.assertEqual(res.status_code, 200, f"Route {r} returned {res.status_code}")

    def test_06_faceted_filtering(self):
        """Verify faceted filters by gender, family, and sorting."""
        # Men filter
        res_men = self.client.get('/products?gender=Men')
        self.assertEqual(res_men.status_code, 200)
        # Unisex filter
        res_unisex = self.client.get('/products?gender=Unisex')
        self.assertEqual(res_unisex.status_code, 200)
        # Sort price asc
        res_sort = self.client.get('/products?sort=price_asc')
        self.assertEqual(res_sort.status_code, 200)

    def test_07_product_detail_olfactory_pyramid(self):
        """Verify product detail page renders olfactory pyramid notes."""
        # Product 101 is Khamrah
        res = self.client.get('/product/101')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        self.assertIn("Khamrah", html)
        self.assertIn("Olfactory Pyramid", html)
        self.assertIn("Top Notes", html)
        self.assertIn("Heart Notes", html)
        self.assertIn("Base Notes", html)
        self.assertIn("Product Details", html)
        self.assertIn("Provenance", html)
        self.assertIn("Concentration", html)

if __name__ == '__main__':
    unittest.main()
