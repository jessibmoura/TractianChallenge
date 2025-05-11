from Baldor import Baldor

if __name__ == "__main__":
    baldor = Baldor()

    baldor.open()
    baldor.load_products_page(target_category="DC Motors")
    baldor.scrap_product(limit=5)
    baldor.exit()
