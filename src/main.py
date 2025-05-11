from Baldor import Baldor

if __name__ == "__main__":
    """
        main.py

        Script to initialize and run the Baldor web scraping pipeline.

        This script creates an instance of the Baldor class and automates the process
        of opening the Baldor catalog website, navigating to a specific product category
        ("DC Motors"), scraping data from a defined number of products (limit=5),
        and finally closing the browser session.

        The collected data includes product specifications, descriptions, images, and manuals,
        which are saved locally in structured JSON format.

        Usage
        -----
        Run this script as the main entry point:
            python src/main.py
    """
    baldor = Baldor()

    baldor.open()
    baldor.load_products_page(target_category="DC Motors")
    baldor.scrap_product(limit=5)
    baldor.exit()
