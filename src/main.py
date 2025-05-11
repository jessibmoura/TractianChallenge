from Baldor import Baldor

if __name__ == "__main__":
    baldor = Baldor()

    baldor.open()
    baldor.load_products_page(target_category="Grinders, Buffers, Lathes")
    baldor.scrap_product(limit=5)
    baldor.exit()
