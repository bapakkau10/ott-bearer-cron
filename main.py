from playwright.sync_api import sync_playwright

def get_live_link():
    with sync_playwright() as p:
        # Menjalankan pelayar dalam mod 'headless' (tanpa paparan)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Buka laman web
        page.goto("https://malaysia-tv.net/tv3-live/")
        
        # Cari dan klik butang 'OK' (menunggu butang wujud dahulu)
        try:
            # Sesuaikan selector berdasarkan class/text butang 'OK' dalam inspect element
            page.click("text=OK", timeout=10000)
            print("Butang OK telah ditekan.")
        except:
            print("Butang OK tidak dijumpai atau sudah ditekan.")

        # Tunggu pautan .m3u8 muncul dalam rangkaian
        with page.expect_request("**/streamer/*.m3u8*") as request_info:
            page.wait_for_timeout(5000) # Tunggu seketika
        
        final_link = request_info.value.url
        print(f"Link terkini: {final_link}")
        
        # Di sini anda boleh tambah kod untuk simpan ke file, database, atau POST ke API anda
        
        browser.close()

if __name__ == "__main__":
    get_live_link()
