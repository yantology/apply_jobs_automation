"""
    Glints provider for job apllication
"""

from patchright.async_api import Page,Locator,expect
import asyncio
import os
import re
from pydantic_ai_role import generate_role,JobCategoryAi
from generate_cv.pdf_generator import generate_cv_pdf,JobCategory
from generate_cv.models import Output
from db.models import JobApplication, ApplicationStatus
from sqlmodel import Session
from db.database import engine
from db.crud import create_job_application,check_link_availability

async def glints_provider(page: Page):
        
    # Menggunakan halaman yang sudah ada atau halaman baru
    try :
        url = "https://glints.com/id/opportunities/jobs/explore?keyword=golang&country=ID&locationName=All+Cities%2FProvinces&yearsOfExperienceRanges=ONE_TO_THREE_YEARS%2CFRESH_GRAD%2CNO_EXPERIENCE%2CLESS_THAN_A_YEAR"
        await page.goto(url,wait_until="domcontentloaded",timeout=60000)
    except Exception as e:
        print(f"Error saat mengakses URL: {e}")
        raise e
    
    job_card_selector = ".JobCardsc__JobcardContainer-sc-hmqj50-0"
    try:
        # Tunggu elemen yang menunjukkan bahwa halaman telah dimuat sepenuhnya
        await page.wait_for_selector(job_card_selector, timeout=60000)
    except Exception as e:
        print(f"Error saat menunggu elemen: {e}")
        raise e
    
    count = await count_job_card(page, job_card_selector)

    print(f"Found {count} job cards to process")
    for i in range(count):
        print(f"Processing job card {i+1}/{count}")
        current_job_card = page.locator(job_card_selector).nth(i)
        
        print(f"Opening new tab for job card {i+1}")
        job_page = await new_tab(page, current_job_card)

        await asyncio.sleep(1)
        try:
            print("Waiting for job page to load")
            await job_page.wait_for_load_state("domcontentloaded", timeout=60000)
            await asyncio.sleep(1)
            print(f"Checking if job URL already exists: {job_page.url}")
            await check_availability(job_page.url)
            await asyncio.sleep(1)
            button_apply = "button:has-text('Lamar'):not([disabled])"

            print("Checking if apply button is available")
            await apply_button_not_disabled(job_page, button_apply)
            await asyncio.sleep(1)

            job_selector = "h1[aria-label='Job Title'].TopFoldsc__JobOverViewTitle-sc-1fbktg5-3"
            company_name_selector = "div.AboutCompanySectionsc__Title-sc-c7oevo-6"
            location_selector = "p.TypographyStyles__StyledTypography-sc-ro16eu-0.bGShET"
            salary_selector = "span.TopFoldsc__BasicSalary-sc-1fbktg5-13"
            description_title_selector = "div.JobDescriptionsc__TitleContainer-sc-22zrgx-1.hiYwUK"
            description_description_selector = "div.JobDescriptionsc__DescriptionContainer-sc-22zrgx-2.btZuDu"
            
            print("Getting job role")
            role = await get_role(job_page, job_selector)
            await asyncio.sleep(1)
            print(f"Job role: {role}")
            
            print("Getting company name")
            company_name = await get_company_name(job_page, company_name_selector)
            await asyncio.sleep(1)
            print(f"Company name: {company_name}")
            
            print("Getting job location")
            location = await get_location(job_page, location_selector)
            await asyncio.sleep(1)
            print(f"Location: {location}")
            
            print("Getting minimum salary")
            salary_min = await get_salary_min(job_page, salary_selector)
            await asyncio.sleep(1)
            print(f"Salary minimum: {salary_min}")
            
            print("Getting job description")
            description = await get_description(job_page, description_title_selector, description_description_selector)
            await asyncio.sleep(1)
            print(f"Description : {description} ")
            
            print("Generating CV")
            cv_output = await generate_cv(role, description, salary_min)
            await asyncio.sleep(1)
            print(f"CV generated at: {cv_output.pdf_path}")

            print("Applying for job")
            await apply_job(job_page, button_apply, path=cv_output.pdf_path)
            await asyncio.sleep(1)
            print("Job application submitted successfully")

            print("Creating job application record")
            job_application = JobApplication(
                link=job_page.url,
                company_name=company_name,
                role=role,
                location=location,
                salary_min=salary_min,
                description=description,
                status=ApplicationStatus.APPLY,
                cv_summary=cv_output.summary,
            )

            print("Saving job application to database")
            await save_job_application(job_application)
            await asyncio.sleep(1)
            print(f"Berhasil melamar pekerjaan: {job_application.link} dengan role {role} dan gaji minimum {salary_min}")
        except Exception as e:
            print(f"Error halaman : {e}")
            print(f"Error details: {type(e).__name__}")
        finally:
            print(f"Closing job page {i+1}")
            if job_page and not job_page.is_closed():
                await job_page.close()
                await asyncio.sleep(1)
            print(f"Job page {i+1} closed")
             
        
async def count_job_card(page: Page, job_card_selector: str) -> int:
    try:
        all_job_cards = page.locator(job_card_selector)
        job_card_count = await all_job_cards.count()
        if job_card_count == 0:
            print("Tidak ada job card ditemukan.")
            raise ValueError("tidak ada")
        else :
            return job_card_count
    except Exception as e:
        print(f"Error saat menghitung job card: {e}")
        raise e

async def new_tab(page: Page, Locator: Locator) -> Page:
    try:
        # First ensure the element is visible in the viewport
        await Locator.scroll_into_view_if_needed(timeout=5000)
        
        # Then click to open a new tab
        async with page.context.expect_page(timeout=10000) as new_page_info:
            await Locator.click(timeout=5000)
            new_tab = await new_page_info.value
            return new_tab
    except Exception as e:
        print(f"Error saat mengakses halaman baru: {e}")
        raise e

async def get_role(page : Page, selector: str) -> str:
    try:
        title_container = page.locator(selector)
        await title_container.wait_for(state="visible", timeout=5000)
        role = await title_container.inner_text()
        return role.strip()
    except Exception as e:
        print(f"Error saat mendapatkan role: {e}")
        raise e

async def get_company_name(page: Page, selector: str) -> str:
    try:
        company_name_container = page.locator(selector)
        await company_name_container.wait_for(state="visible", timeout=5000)
        company_name = await company_name_container.inner_text()
        return company_name.strip()
    except Exception as e:
        print(f"Error saat mendapatkan nama perusahaan: {e}")
        raise e

async def get_location(page: Page, selector: str) -> str:
    try:
        location_container = page.locator(selector)
        await location_container.wait_for(state="visible", timeout=5000)
        location = await location_container.inner_text()
        return location.strip()
    except Exception as e:
        print(f"Error saat mendapatkan lokasi: {e}")
        raise e
    
async def get_salary_min(page: Page, selector: str) -> int:
    try:
        salary_container = page.locator(selector)
        await salary_container.first.wait_for(state="visible", timeout=5000)
        salary = await salary_container.inner_text()
        salary = re.sub(r'\s+', ' ', salary).strip()
        # Ekstrak angka gaji minimum menggunakan regex
        # Format: IDR X.XXX.XXX - Y.YYY.YYY/Bulan
        salary_pattern = r'IDR\s*(\d[\d\.,]*)\s*-'
        salary_match = re.search(salary_pattern, salary)
        if salary_match:
            # Konversi ke integer (menghapus titik sebagai pemisah ribuan)
            salary_minimum_number = int(salary_match.group(1).replace(".", "").replace(",", "").strip())
            salary_min = salary_minimum_number
            
            return salary_min # salary_min will always be an int here, or raise an error before this point.
        else:
            return 0
    except Exception:
        return 0

async def get_description(page: Page, title_selector: str, description_selector: str) -> str:
    try:
        title_container = page.locator(title_selector)
        await title_container.wait_for(state="visible", timeout=5000)
        title = await title_container.inner_text()
        
        description_container = page.locator(description_selector)
        await description_container.wait_for(state="visible", timeout=5000)
        description = await description_container.inner_text()
        
        return f"{title}\n{description}"
    except Exception as e:
        print(f"Error saat mendapatkan deskripsi: {e}")
        raise e

async def generate_cv(role:str,vacancy:str,min_salary:int) -> Output:
    try:
        result_role = await generate_role(role=role,vacancy=vacancy,min_salary=min_salary)
        if result_role.job_category == JobCategoryAi.NONE:
            raise ValueError(f"{result_role.reason}")
        
        # Map JobCategoryAi to JobCategory using a dictionary
        category_mapping = {
            JobCategoryAi.BACKEND: JobCategory.BACKEND,
            JobCategoryAi.FRONTEND: JobCategory.FRONTEND,
        }
                
        # Get appropriate JobCategory or default to FULLSTACK if category not found
        role_cv = category_mapping.get(result_role.job_category,JobCategory.FULLSTACK)

        output = generate_cv_pdf(vacancy=vacancy,roles=role_cv)
        
        return output
    except Exception as e:
        print(f"Error saat menghasilkan CV: {e}")
        raise e

async def apply_button_not_disabled(page: Page, selector: str) -> None:
    try:
        apply_button = page.locator(selector)
        await apply_button.first.wait_for(state="visible", timeout=15000)
    except Exception as e:
        print(f"Error saat memeriksa tombol apply: {e}")
        raise e
    
async def apply_job(page: Page, selector: str,path: str) -> None:
    try:
        apply_button = page.locator(selector)
        await apply_button.first.wait_for(state="visible", timeout=5000)
        await apply_button.first.click(timeout=5000)
        
        file_input_locator = page.locator('input[type="file"].HiddenFileInputsc__FileInput-sc-hz4dcq-0')
        # Tombol "Hapus file"
        delete_button_locator = page.locator('button.ResumeFieldsc__DeleteButton-sc-yk9awg-6:has-text("Hapus file")')
        # Tombol "Upload CV-mu"
        upload_cv_button_locator = page.locator('button.ResumeFieldsc__UploadResumeButton-sc-yk9awg-2:has-text("Upload CV-mu")')
        # Container detail file yang sudah diupload
        resume_detail_container_locator = page.locator('div.ResumeFieldsc__EditResumeContainer-sc-yk9awg-3')
        
        # Kita beri sedikit waktu jika elemen butuh waktu untuk muncul
        try:
            await delete_button_locator.wait_for(state="visible", timeout=5000) # Tunggu hingga 5 detik
            print("File terdeteksi (tombol 'Hapus file' terlihat).")
            is_file_present = True
        except Exception: # TimeoutException jika tidak ditemukan
            print("Tidak ada file yang terdeteksi (tombol 'Hapus file' tidak terlihat).")
            is_file_present = False
        
        if is_file_present:
            # Jika file sudah ada, kita hapus dulu
            await delete_button_locator.click(timeout=5000)
            # Tunggu hingga tombol "Upload CV-mu" terlihat
            await upload_cv_button_locator.wait_for(state="visible", timeout=5000)

        await file_input_locator.set_input_files(path)

        uploaded_file_name = os.path.basename(path)


        await expect(resume_detail_container_locator).to_be_visible(timeout=15000) # Waktu lebih lama untuk proses upload

        uploaded_file_name_locator = resume_detail_container_locator.locator(f'p.ResumeFieldsc__ResumeFileName-sc-yk9awg-8:has-text("{uploaded_file_name}")')
        # Tunggu hingga nama file yang diupload terlihat di dalam container
        await expect(uploaded_file_name_locator).to_be_visible(timeout=10000)
        # Locate and click the "Kirim" (Send) button
        kirim_button_locator = page.locator('button:has-text("Kirim")')
        await expect(kirim_button_locator).to_be_visible(timeout=10000)
        await kirim_button_locator.click(timeout=5000)
        await asyncio.sleep(5)  # Tunggu beberapa detik untuk memastikan pengiriman selesai
    except Exception as e:
        print(f"Error saat mengklik tombol apply: {e}")
        raise e

async def check_availability(link: str) -> None:
    try:
        print(f"Memeriksa ketersediaan link: {link}")
        with Session(engine) as session:
            print(f"Memeriksa ketersediaan link di database: {link}")
            if check_link_availability(session, link):
                print(f"Link dapat digunakan")
                return
            else:
                raise ValueError(f"Link '{link}' sudah ada di database. Tidak menyimpan.")
    except Exception as e:
        print(f"Error saat memeriksa ketersediaan link: {e}")
        raise e

async def save_job_application(job_application: JobApplication) -> None:
    try:
        with Session(engine) as session:
            # Cek ketersediaan link sebelum menyimpan
            if check_link_availability(session, job_application.link):
                create_job_application(session, job_application)
            else:
                raise ValueError(f"Link '{job_application.link}' sudah ada di database. Tidak menyimpan.")
    except Exception as e:
        print(f"Error menyimpan JobApplication ke database: {e}")
        raise e