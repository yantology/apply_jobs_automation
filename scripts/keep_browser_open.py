from patchright.async_api import async_playwright
import asyncio

async def main():
    user_data_dir_path = "/home/wijayanto1320/.config/google-chrome/Default" # Sesuaikan jika perlu

    async with async_playwright() as p:
        print("Meluncurkan browser dengan konteks persisten...")
        
        # Opsi argumen browser
        browser_args = [
            # Cobalah untuk TIDAK menyertakan '--no-sandbox' jika Anda ingin sandbox aktif.
            # Namun, perhatikan bahwa patchright mungkin tetap menambahkannya atau memerlukan ini.
            # '--disable-setuid-sandbox', # Sering digunakan bersama --no-sandbox di lingkungan Linux
            # '--disable-dev-shm-usage', # Sering membantu di lingkungan Docker/CI
            # Anda bisa mencoba menambahkan argumen lain di sini jika diperlukan
        ]

        # Jika Anda ingin secara eksplisit mencoba MENGHINDARI --no-sandbox, 
        # Anda bisa mencoba tidak memasukkannya ke 'browser_args'.
        # Namun, jika 'patchright' menambahkannya secara internal, ini mungkin tidak berpengaruh.

        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir_path,
            channel="chrome",
            headless=False,
            no_viewport=True, # no_viewport biasanya berarti Anda ingin viewport default, bukan tidak ada viewport sama sekali
            args=browser_args # Tambahkan parameter args di sini
        )
        print("Browser diluncurkan dengan konteks persisten.")
        
        print("Anda dapat melakukan operasi dengan browser sekarang.")
        print("Script akan menunggu beberapa detik sebagai contoh, lalu menutup browser.")
        await asyncio.sleep(10000) # Diberi waktu lebih lama untuk observasi

        print("Menutup browser...")
        await context.close()
        print("Browser berhasil ditutup.")

if __name__ == "__main__":
    asyncio.run(main())