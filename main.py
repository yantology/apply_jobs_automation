from patchright.async_api import async_playwright
import asyncio
import os
from provider.glints import glints_provider


async def main():
    context = None
    page = None
    # Tentukan path user_data_dir dengan lebih hati-hati
    user_data_dir_path = "/home/wijayanto1320/.config/google-chrome/Default" # Sesuaikan jika perlu

    # Cek apakah direktori user_data_dir ada
    if not os.path.exists(user_data_dir_path):
        print(f"Peringatan: Direktori user_data_dir tidak ditemukan di {user_data_dir_path}. Pastikan path-nya benar atau buat direktorinya.")
        # Jika direktori tidak ada, Playwright akan membuatnya, tetapi profil yang ada tidak akan dimuat.
        # Anda bisa memilih untuk menghentikan skrip di sini jika profil persisten adalah krusial.
        # return

    try:
        async with async_playwright() as p:
            print("Meluncurkan browser dengan konteks persisten...")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir_path,
                channel="chrome",
                headless=False,
                no_viewport=True,
            )
            print("Browser diluncurkan dengan konteks persisten.")

            # Gunakan halaman pertama yang mungkin sudah ada (misalnya, 'new tab page')
            # atau buat halaman baru jika tidak ada halaman.
            if context.pages:
                page = context.pages[0]
                print("Menggunakan halaman yang sudah ada di konteks.")
            else:
                print("Membuat halaman baru...")
                page = await context.new_page()
                print("Halaman baru dibuat.")
            
            # Pastikan viewport diatur jika tidak menggunakan start-maximized
            # await page.set_viewport_size({"width": 1920, "height": 1080})


            await glints_provider(
                page=page)

    except Exception as e:
        print(f"\nTerjadi kesalahan utama selama operasi Playwright: {e}")
        try:
            if page and not page.is_closed():
                error_screenshot_path = "error_screenshot_main_page.png"
                await page.screenshot(path=error_screenshot_path)
                print(f"Tangkapan layar error dari halaman utama disimpan sebagai {error_screenshot_path}")
            elif context and context.pages:
                for idx, p_err in enumerate(context.pages):
                    if not p_err.is_closed():
                        error_screenshot_path_ctx = f"error_screenshot_context_page_{idx}.png"
                        await p_err.screenshot(path=error_screenshot_path_ctx)
                        print(f"Tangkapan layar error dari halaman konteks ke-{idx} disimpan sebagai {error_screenshot_path_ctx}")
                        break # Ambil satu saja
        except Exception as e_screenshot:
            print(f"Gagal mengambil tangkapan layar saat error utama: {e_screenshot}")

    finally:
        if context:
            print("\nSelesai. Menutup konteks browser...")
            # await asyncio.sleep(10) # Tambahkan jeda jika ingin melihat browser sebelum ditutup
            await context.close()
            print("Konteks browser ditutup.")
        else:
            print("Konteks browser tidak diinisialisasi atau sudah ditutup.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEksekusi dihentikan oleh pengguna.")
    except Exception as e_run:
        print(f"\nTerjadi kesalahan saat menjalankan asyncio loop: {e_run}")